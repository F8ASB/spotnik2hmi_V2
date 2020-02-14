#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import settings as d
from fonctions import *
import serial
import sys
from datetime import  *
import time
from time import sleep
import requests
#pour lecture fichier de config
import configparser, os
#pour adresse ip
import socket
#pour CPU
import io
#pour json
import json
#Pour ouverture nomenclature
import csv
#import psutil
import os
import ssl

#creation liste pour Dashboard
listdash =[]

#Envoi des information port com selon arguments script
portcom(sys.argv[1],sys.argv[2])

#Detection mode DEBUG
if len(sys.argv)==4:

    if sys.argv[3]=="DEBUG": 
        print("MODE DEBUG")
        debugON()
#definition du nom de l'application
set_procname('spotnik2hmi')

#recuperation indicatif et frequence    
callsign = get_callsign()
freq = get_frequency()

#recuperation GPIO dans les parametres
nbgpioptt = get_gpioptt()
nbgpiosql = get_gpiosql()

#adresse IP
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
ip= (s.getsockname()[0])
s.close()



#Memoire SD libre
disk= getDiskSpace()
occupdisk = str(disk)

#Utilisation CPU
chargecpu= getCPUuse()

#Detection carte
revision=getrevision()
if revision =="0000":
    board = 'Orange Pi'
    #temperature CPU
    f = open("/sys/devices/virtual/thermal/thermal_zone0/temp", "r")
    t = f.readline ()
    cputemp = t[0:2]
if revision !="0000":
    board = 'Raspberry Pi'
    #temperature CPU
    f = open("/sys/class/thermal/thermal_zone0/temp", "r")
    t = f.readline ()
    cputemp = t[0:2]
    
#Test presence carte son WM8960 ou autre

subcmd=os.popen('aplay -l','r')
if (subcmd.read().find('8960'))!= -1:
    print("DETECTION WM8960")
    d.audioOut='Headphone'
    d.audioIn="Capture"
    d.soundcard="WM8960"
    os.system("amixer -c 0 set 'Right Output Mixer PCM' unmute")
    os.system("amixer -c 0 set 'Left Output Mixer PCM' unmute")
else:
    ReqaudioOut=os.popen("amixer scontrols", "r").read()
    audioinfo= ReqaudioOut.split("'")
    d.audioOut=audioinfo[1]
    d.audioIn="Mic"
    d.soundcard="USB SOUND"
    os.system('amixer -c 0 set ' +d.audioOut+ ' unmute')
    
log(("Peripherique audio Out: "+d.audioOut),"white")
 

  #Detection RPI 3 B+
revision=getrevision()

if revision=="a020d3":
    log("RASPBERRY 3B+ DETECTION","white")
    d.rpi3bplus=True
else:
    log("pas de 3B+","white")

log(board,"white") 

#Envoi des infos 
logo(d.versionDash)

print("     +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+")
print("     +    "+"Proc: "+(str(chargecpu))+"%   " + "CPU: "+cputemp+"°C"+ "    +   " + "Spotnik: Version:"+d.version+"  +")
print("     +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+")
print("     +   " +"Station: "+d.callsign + "       Frequence: "+d.freq+" Mhz"+"    +")
print("     +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+")

#test version database OM
datacheckversion()

#reset de l'ecran
resetHMI()

sleep(1);
#Envoi des informations callsign et version au HMI
ecrire("boot.va0.txt",d.callsign)
ecrire("boot.vascript.txt",d.versionDash)
ecrire("boot.vaverspotnik.txt",d.version)
date = (d.today.strftime('%d-%m-%Y'))
ecrire("boot.Vtxt_dateinit.txt",date)
heureS =(d.today.strftime('%H:%M'))
ecrire("boot.Vtxt_heureinit.txt",heureS)

#envoi indicatif
log("Maj Call ...","red")

#Reglage niveau audio visible si Raspberry
if board =='Raspberry Pi':
    ecrireval("trafic.vasound.val","1")
    GetAudioInfoOut(d.audioOut)
    GetAudioInfoIn(d.audioIn)

sleep(4);


# Detection Raptor 
# Programme de Armel F4HWN
# https://github.com/armel/RRFRaptor

#detection presence repertoire RRFRaptor
raptor = os.path.isdir('/opt/RRFRaptor')

#Gestion bouton Raptor visble si disponible
if raptor:
    ecrireval("scan.Vnb_raptor.val","1")
    log("Raptor disponible","white") 
    raptortest()
else:
    ecrireval("scan.Vnb_raptor.val","0")
    log("Raptor non disponible","white") 

#verification si nouvelle version disponible
checkversion()

#**************************************
#* demarrage page trafic ou perroquet *
#**************************************

a = open("/etc/spotnik/network","r")
tn = a.read()

if tn.find("default") != -1 :
      gopage("parrot")
else:
      gopage("trafic")
a.close()

os.system ("clear")

while True:
#*************************
#* Gestion Date et heure *
#*************************

    d.dashlist = ""
    d.today = datetime.now()
    locale.setlocale(locale.LC_TIME,'') 
    date = (d.today.strftime('%d-%m-%Y'))
    heureS =(d.today.strftime('%H:%M'))
    if date != d.dateold:
        ecrire("Txt_date.txt",date)
        ecrire("boot.Vtxt_dateinit.txt",date)
        d.dateold=date
    if heureS != d.heureSold:
        ecrire("Txt_heure.txt",heureS)
        ecrire("boot.Vtxt_heureinit.txt",heureS)
        d.heureSold= heureS

    requete("vis p9,0")

    timestamp = d.today.strftime('%d-%m-%Y %H:%M:%S')

    if raptor:
        raptortest()

    for key in d.salon:

        try:
            r = requests.get(d.salon[key]['url'], verify=False, timeout=10)
            page = r.text
        except requests.exceptions.ConnectionError as errc:
            print(('Error Connecting:', errc))
        except requests.exceptions.Timeout as errt:
            print(('Timeout Error:', errt)) 
               
#***********************************
#*  Transmitter en cours sur salon *
#***********************************

        search_start = page.find('TXmit":"')            # Search this pattern
        search_start += 8                               # Shift...
        search_stop = page.find('"', search_start)      # And close it...

        if search_stop != search_start:
            d.salon[key]['transmit'] = True

            d.salon[key]['call_current'] = page[search_start:search_stop]

            if (d.salon[key]['call_previous'] != d.salon[key]['call_current']):
                d.monitor = timestamp + " " + key + " T " + str(d.salon[key]['call_current'])
                dash = heureS +" " + str(d.salon[key]['call_current'])+"-" + key
                d.salon[key]['call_previous'] = d.salon[key]['call_current']
                ecrire("monitor.Txt_statut.txt",d.monitor)
                ecrire("dashboard.Vtxt_dash.txt",str(dash))
                print(d.monitor)
                envoistatut()
                
                #print(str(d.salon["RRF"]['transmit'])

                #Stockage station pour dashboard
                infodash=d.today.strftime('%H:%M ')+ str(d.salon[key]['call_current']) +"-"+key
                listdash.append(infodash)
                if key == d.salon_current:
                	Infocall(d.salon[key]['call_current'])
                
                #print (len(listdash))
                if len(listdash) == 13:
                    #del listdash[12]
                    listdash.pop(0)
                
        else:            
            if d.salon[key]['transmit'] is True:
                d.salon[key]['call_current'] = ''
                d.salon[key]['call_previous'] = ''
                d.monitor = timestamp + " " + key + " T OFF"
                d.salon[key]['transmit'] = False
                ecrire("monitor.Txt_statut.txt",d.monitor)
                print(d.monitor)
                envoistatut()
        

#*************************************************
#* Boucle gestions liste Nodes F8ASB + F4HWN DEV *
#*************************************************

        search_start = page.find('nodes":[')                    
        search_start += 9                                       
        search_stop = page.find('],"TXmit"', search_start)      

        tmp = page[search_start:search_stop]
        tmp = tmp.replace('"', '')

        d.salon[key]['node_list'] = tmp.split(',')

        for n in ['RRF', 'RRF2', 'RRF3', 'TECHNIQUE', 'BAVARDAGE', 'INTERNATIONAL', 'LOCAL', 'FON', 'EXP','REG']:
            if n in d.salon[key]['node_list']:
                d.salon[key]['node_list'].remove(n)

        if d.salon[key]['node_list_old'] == []:
            d.salon[key]['node_list_old'] = d.salon[key]['node_list']

        else:
            if d.salon[key]['node_list_old'] != d.salon[key]['node_list']:
                # Nodes out
                if (list(set(d.salon[key]['node_list_old']) - set(d.salon[key]['node_list']))):
                    d.salon[key]['node_list_out'] = list(set(d.salon[key]['node_list_old']) - set(d.salon[key]['node_list']))

                    for n in d.salon[key]['node_list_out']:
                        if n in d.salon[key]['node_list_in']:
                            d.salon[key]['node_list_in'].remove(n)

                    d.salon[key]['node_list_out'] = sorted(d.salon[key]['node_list_out'])
                    if len(d.salon[key]['node_list_out']) > d.MOVE_MAX:
                        d.monitor = timestamp + ' ' + key + ' > ' + str(','.join(d.salon[key]['node_list_out'][:(d.MOVE_MAX)])) + '...'
                        ecrire("monitor.Txt_statut.txt",d.monitor)
                    else:
                        d.monitor = timestamp + ' ' + key + ' > ' + str(','.join(d.salon[key]['node_list_out']))
                        ecrire("monitor.Txt_statut.txt",d.monitor)
                # Nodes in    
                if (list(set(d.salon[key]['node_list']) - set(d.salon[key]['node_list_old']))):
                    d.salon[key]['node_list_in'] = list(set(d.salon[key]['node_list']) - set(d.salon[key]['node_list_old']))

                    for n in d.salon[key]['node_list_in']:
                        if n in d.salon[key]['node_list_out']:
                            d.salon[key]['node_list_out'].remove(n)

                    d.salon[key]['node_list_in'] = sorted(d.salon[key]['node_list_in'])
                    if len(d.salon[key]['node_list_in']) > d.MOVE_MAX:
                        d.monitor = timestamp + ' ' + key + ' < ' + str(','.join(d.salon[key]['node_list_in'][:(d.MOVE_MAX)])) + '...'
                        ecrire("monitor.Txt_statut.txt",d.monitor)
                        print(d.monitor)
                    else:
                        d.monitor = timestamp + ' ' + key + ' < ' + str(','.join(d.salon[key]['node_list_in']))
                        ecrire("monitor.Txt_statut.txt",d.monitor)
                        print(d.monitor)
                # Nodes count
                d.salon[key]['node_count'] = len(d.salon[key]['node_list'])
                d.monitor = timestamp + ' ' + key + ' = ' + str(d.salon[key]['node_count'])
                d.salon[key]['node_list_old'] = d.salon[key]['node_list']
                print(d.monitor)
                ecrire("monitor.Txt_statut.txt",d.monitor)

#*****************************
#* DETECTION CONNEXION SALON *
#*****************************

    a = open("/etc/spotnik/network","r")
    tn = a.read()

    if tn.find("rrf") != -1 and d.salon_current!="RRF":
        ecrire("monitor.Vtxt_saloncon.txt","RESEAU RRF")
        d.salon_current="RRF"
        ecrire("trafic.g0.txt","")
        if d.qsystatut==False and d.firstboot==False:
            gopage("qsy")
        d.qsystatut=False
        
    if tn.find("fon") != -1 and d.salon_current!="FON":
        ecrire("monitor.Vtxt_saloncon.txt","RESEAU FON")    
        d.salon_current="FON"
        ecrire("trafic.g0.txt","")
        if d.qsystatut==False and d.firstboot==False:
            gopage("qsy")
        d.qsystatut=False
    
    if tn.find("tec") != -1 and d.salon_current!="TEC":
        ecrire("monitor.Vtxt_saloncon.txt","SALON TECHNIQUE")
        d.salon_current="TEC"
        ecrire("trafic.g0.txt","")
        if d.qsystatut==False and d.firstboot==False:
            gopage("qsy")
        d.qsystatut=False

    if tn.find("int") != -1 and d.salon_current!="INT":
        ecrire("monitor.Vtxt_saloncon.txt","SALON INTER.")
        d.salon_current="INT"
        ecrire("trafic.g0.txt","")
        if d.qsystatut==False and d.firstboot==False:
            gopage("qsy")
        d.qsystatut=False

    if tn.find("bav") != -1 and d.salon_current!="BAV":
        ecrire("monitor.Vtxt_saloncon.txt","SALON BAVARDAGE")    
        d.salon_current="BAV"
        ecrire("trafic.g0.txt","")
        if d.qsystatut==False and d.firstboot==False:
            gopage("qsy")
        d.qsystatut=False

    if tn.find("loc") != -1 and d.salon_current!="LOC":
        ecrire("monitor.Vtxt_saloncon.txt","SALON LOCAL")    
        d.salon_current="LOC"
        ecrire("trafic.g0.txt","")
        if d.qsystatut==False and d.firstboot==False:
            gopage("qsy")
        d.qsystatut=False

    if tn.find("default") != -1 and d.salon_current!="PER":
        ecrire("monitor.Vtxt_saloncon.txt","PERROQUET")
        ecrire("trafic.g0.txt","")
        d.salon_current="PER"
        if d.qsystatut==False and d.firstboot==False:
            gopage("qsy") 
        if d.qsystatut==False and d.firstboot==True:
            gopage("Parrot") 
        d.qsystatut=False

    if tn.find("sat") != -1 and d.salon_current!="SAT":
        ecrire("monitor.Vtxt_saloncon.txt","SALON EXP.")
        ecrire("trafic.g0.txt","") 
        d.salon_current="SAT"
        if d.qsystatut==False and d.firstboot==False:
            gopage("qsy")
        d.qsystatut=False   

    if tn.find("exp") != -1 and d.salon_current!="EXP":
        ecrire("monitor.Vtxt_saloncon.txt","SALON EXP.")
        ecrire("trafic.g0.txt","") 
        d.salon_current="EXP"
        if d.qsystatut==False and d.firstboot==False:
            gopage("qsy")
        d.qsystatut=False   

    if tn.find("fdv") != -1 and d.salon_current!="EXP":
        ecrire("monitor.Vtxt_saloncon.txt","SALON EXP. DV")
        ecrire("trafic.g0.txt","") 
        d.salon_current="EXP"
        if d.qsystatut==False and d.firstboot==False:
            gopage("qsy")
        d.qsystatut=False   

    if tn.find("reg") != -1 and d.salon_current!="REG":
        ecrire("monitor.Vtxt_saloncon.txt","SALON REGIONAL")
        ecrire("trafic.g0.txt","") 
        d.salon_current="REG"
        if d.qsystatut==False and d.firstboot==False:
            gopage("qsy")
        d.qsystatut=False   

    if tn.find("el") != -1 and d.salon_current!="ECH":
        ecrire("monitor.Vtxt_saloncon.txt","ECHOLINK")
        ecrire("trafic.g0.txt","")
        d.salon_current="ECH"
        if d.qsystatut==False and d.firstboot==False:
            gopage("qsy")
        d.qsystatut=False
#***********************************
#*Gestion salon Perroquet TX et RX *
#***********************************

    if tn.find("default") != -1 and d.salon_current=="PER":
        
        p= open("/sys/class/gpio/"+nbgpiosql+"/value","r")
        gpiorx_value = p.read()
        
        if gpiorx_value.find("1") != -1 and d.statutradio!="RX":
             log("RX Detected","white")
             d.statutradio="RX"
             #requete("vis p2,1")
             ecrireval("Vnbr_parrot.val","1")
             

        elif gpiorx_value.find("0") != -1 and d.statutradio!="TX" and d.statutradio!="":
             log("RX OFF","white")
             #requete("vis p2,0")
             ecrireval("Vnbr_parrot.val","0")

             d.statutradio=""

        p.close()

        q= open("/sys/class/gpio/"+nbgpioptt+"/value","r")
        gpiotx_value = q.read()
        
        if gpiotx_value.find("1") != -1 and d.statutradio!="TX":
             log("Tx ON","white")
             d.statutradio="TX"
             #requete("vis p3,1")
             ecrireval("Vnbr_parrot.val","2")
             
        elif gpiotx_value.find("0") != -1 and d.statutradio!="RX" and d.statutradio!="":
             log("Tx OFF","white")
             #requete("vis p3,0")
             ecrireval("Vnbr_parrot.val","0")
             d.statutradio=""

        q.close()

    a.close()

#****************************************************
#* Gestion des commandes serie reception du Nextion *
#****************************************************

    s = hmiReadline()
    if len(s)<59 and len(s)>0:
        log(s,"blue")
#**********************
#* confirmation ecran *
#**********************

#OUIREBOOT#
    if s.find("ouireboot")!= -1:
        log("REBOOT","red")
        gopage("boot")
        os.system('reboot')

#OUIRESTART#
    if s.find("ouiredem")!= -1:
        log("REDEMARRAGE","red")
        dtmf("96#")
        gopage ("trafic")

#OUIARRET#
    if s.find("ouiarret")!= -1:
        log("ARRET DU SYSTEM","red")
        os.system('shutdown -h now')

#OUIWIFI
    if s.find("ouimodwifi")!= -1:
        
        if d.rpi3bplus==True:
            wifi3bplus(newssid,newpass)
        else:
            wifi(newssid,newpass)
        log("ECRITURE INFO WIFI DANS JSON + CONFIG","red")
        
        gopage("reglages")

#RAPTOR#
    if s.find("raptorstart")!= -1:
        log("raptor ON","red")
        os.system('/opt/RRFRaptor/RRFRaptor.sh')

    if s.find("raptorstop")!= -1:
        log("raptor OFF","red")
        os.system('/opt/RRFRaptor/RRFRaptor.sh')

#*******************************
#* Gestion commande du Nextion *
#*******************************
                                                                              
#MAJWIFI
    if s.find("majwifi")!= -1:

        log("MAJ Wifi....","white")
        requete("get t0.txt")
        requete("get t1.txt")
    
        while 1:
            s = hmiReadline()
            if len(s)<71:
                print(s)
                wifiinfo= s.split("p")
                newpass= wifiinfo[1][:-12]
                newssid= wifiinfo[2][:-13]
                log(("New SSID: "+newssid),"white")
                log(("New PASS: "+newpass),"white")
                d.wifistatut = 0
                break
        gopage("confirm")
        ecrire("confirm.t0.txt","CONFIRMER LA MAJ WIFI ?")  

#MAJAUDIO
    if s.find("MAJAUDIO")!= -1:
  
        log("MAJ AUDIO....","red")        

#MUTE AUDIO
    if s.find("MUTEON")!= -1:
        log("MUTE","white")
        if d.soundcard=="WM8960":
            os.system("amixer -c 0 set 'Right Output Mixer PCM' mute")
            os.system("amixer -c 0 set 'Left Output Mixer PCM' mute")
        else:
            os.system('amixer -c 0 set ' +d.audioOut+ ' mute')

#UNMUTE AUDIO
    if s.find("MUTEOFF")!= -1:
        log("UNMUTE","white")
        if d.soundcard=="WM8960":
            os.system("amixer -c 0 set 'Right Output Mixer PCM' unmute")
            os.system("amixer -c 0 set 'Left Output Mixer PCM' unmute")
            
        else:
            os.system('amixer -c 0 set ' +d.audioOut+ ' unmute')

#NIVEAU AUDIO IN
    if s.find("Audioin")!= -1: 
        log(s[s.find("Audioin")+7:(len(s)-13)],"white")
        levelIn=(s[25:(len(s)-13)])
        
        try:
            setAudioIn(d.audioIn,levelIn)

        except ValueError:
            log("Erreur valeur audio","red")
            ecrireval("mixer.Vnb_mixer.val","0")
        

#NIVEAU AUDIO OUT      
    if s.find("Audioout")!= -1: 
        log(s[s.find("Audioout")+8:(len(s)-13)],"white")
        levelOut=(s[s.find("Audioout")+8:(len(s)-13)])
        
        try:
            setAudioOut(d.audioOut,levelOut)

        except ValueError:
            log("Erreur valeur audio","red")
            ecrireval("mixer.Vnb_mixer.val","0")
           

#ENVOI DASHBOARD
    if s.find("listdash")!= -1 and d.salon_current!="RRF":
        log("List dash","red")
        if d.salon_current=="RRF" or d.salon_current=="SAT"or d.salon_current=="ECH"or d.salon_current=="PER":
            ecrire("trafic.g0.txt","")
        else:    
            ecrire("trafic.g0.txt",str(d.salon[d.salon_current]['node_list']).replace("'",'').replace(", ",',')[1:-1]) 
#INFO STATUTS SUR SALON
    if s.find("statutsalon")!= -1:
        log("INFOSTATUT","white")
        envoistatut()


#******************
#* detection page *
#******************       
#PAGE REGLAGES#
    if s.find("page reglages")!= -1:
        log("Page reglages","red")

#Numkaypad#
    if s.find("keypadnum")!= -1:
        log("Page clavier numerique","red")


#DASHBOARD#
    if s.find("dashboard")!= -1:
        log("Page dashboard","red")
        length = len(listdash)
        for i in range(0, length):
            ecrire('Txt_Dash' + str(length - i) + '.txt', listdash[i])
 
   

#MENU#
    if s.find("menu")!= -1:
        log("Page menu","red")
#MONITOR#
    if s.find("monitor")!= -1:
        log("Page monitor","red")
        #Envoi liste des connectes
        ecrire("monitor.Txt_nbrrrf.txt",str(len(d.salon['RRF']['node_list'])))
        ecrire("monitor.Txt_nbrtec.txt",str(len(d.salon['TEC']['node_list'])))
        ecrire("monitor.Txt_nbrloc.txt",str(len(d.salon['LOC']['node_list'])))
        ecrire("monitor.Txt_nbrint.txt",str(len(d.salon['INT']['node_list'])))
        ecrire("monitor.Txt_nbrbav.txt",str(len(d.salon['BAV']['node_list'])))
        ecrire("monitor.Txt_nbrfon.txt",str(len(d.salon['FON']['node_list'])))
        #Envoi station en cours de TX
        calltrafic_currentRRF=d.salon["RRF"]['call_current']
        ecrire("monitor.Txt_Txrrf.txt","")
        ecrire("monitor.Txt_Txrrf.txt",calltrafic_currentRRF)
        calltrafic_currentTEC=d.salon["TEC"]['call_current']
        ecrire("monitor.Txt_Txtec.txt","")
        ecrire("monitor.Txt_Txtec.txt",calltrafic_currentTEC)
        calltrafic_currentBAV=d.salon["BAV"]['call_current']
        ecrire("monitor.Txt_Txbav.txt","")
        ecrire("monitor.Txt_Txbav.txt",calltrafic_currentBAV)
        calltrafic_currentINT=d.salon["INT"]['call_current']
        ecrire("monitor.Txt_Txint.Txt","")
        ecrire("monitor.Txt_Txint.Txt",calltrafic_currentINT)
        calltrafic_currentLOC=d.salon["LOC"]['call_current']
        ecrire("monitor.Txt_Txloc.txt","")
        ecrire("monitor.Txt_Txloc.txt",calltrafic_currentLOC)
        calltrafic_currentFON=d.salon["FON"]['call_current']
        ecrire("monitor.Txt_Txfon.txt","")
        ecrire("monitor.Txt_Txfon.txt",calltrafic_currentFON)

#PAGE SCAN
    if s.find("Pagescan")!= -1:
        log("Page scanner","red")

#PAGE INFO STATION
    if s.find("infostation")!= -1:
        log("Page info Station","red")
        ecrire("infostation.V_verdbase.txt",str(d.database))
        datacheckversion()
        ecrire("infostation.V_verdbase.txt",str(d.database))

#MAJSCAN#
    if s.find("majscan")!= -1:
        log("majscan","red")

        ecrire("scan.Txt_listtec.txt",str(d.salon['TEC']['node_list']).replace("'",'').replace(", ",',')[1:-1])
        ecrire("scan.Txt_listloc.txt",str(d.salon['LOC']['node_list']).replace("'",'').replace(", ",',')[1:-1])
        ecrire("scan.Txt_listint.txt",str(d.salon['INT']['node_list']).replace("'",'').replace(", ",',')[1:-1])
        ecrire("scan.Txt_listbav.txt",str(d.salon['BAV']['node_list']).replace("'",'').replace(", ",',')[1:-1])

        ecrire("scan.Txt_nbrtec.txt",str(len(d.salon['TEC']['node_list'])))
        ecrire("scan.Txt_nbrloc.txt",str(len(d.salon['LOC']['node_list'])))
        ecrire("scan.Txt_nbrint.txt",str(len(d.salon['INT']['node_list'])))
        ecrire("scan.Txt_nbrbav.txt",str(len(d.salon['BAV']['node_list'])))

        #Envoi station en cours de TX
        calltrafic_currentTEC=d.salon["TEC"]['call_current']
        ecrire("scan.Txt_Txtec.txt","")
        ecrire("scan.Txt_Txtec.txt",calltrafic_currentTEC)
        calltrafic_currentINT=d.salon["INT"]['call_current']
        ecrire("scan.Txt_Txint.Txt","")
        ecrire("scan.Txt_Txint.Txt",calltrafic_currentINT)
        calltrafic_currentBAV=d.salon["BAV"]['call_current']
        ecrire("scan.Txt_Txbav.txt","")
        ecrire("scan.Txt_Txbav.txt",calltrafic_currentBAV)
        calltrafic_currentLOC=d.salon["LOC"]['call_current']
        ecrire("scan.Txt_Txloc.txt","")
        ecrire("scan.Txt_Txloc.txt",calltrafic_currentLOC)
        
#BALISE#
    if s.find("balise")!= -1:
        print("Balise vocale")
        dtmf("*#")

#METEO#
    if s.find("meteo")!= -1:
        log("Page meteo","red")
        get_meteo()

#SPEEDNET#
    if s.find("starttestNet")!= -1:
        log("Detection page speedNet","red")
        getspeednet()

#MIXER#
    if s.find("mixer")!= -1:
        log("Detection page mixer","red")
        
                        
#TRAFIC#        
    if s.find("trafic")!= -1:
        log("Page trafic","red")
        ecrire("Txt_date.txt",date)
        ecrire("Txt_heure.txt",heureS)
        
        if d.salon_current in ["TEC", "RRF", "FON", "INT", "BAV", "LOC"]:
            calltrafic_current=d.salon[d.salon_current]['call_current']
            ecrire("trafic.Txt_call.txt","")
            ecrire("trafic.Txt_call.txt",calltrafic_current)

#INFO#  
    if s.find("infosystem")!= -1:
        log("Page info","red")
        #lecture t° CPU temps reel
        if board == 'Orange Pi':
    
            f = open("/sys/devices/virtual/thermal/thermal_zone0/temp", "r")
            t = f.readline ()
            cputemp = t[0:2]
            cput = cputemp 
        
        else:
            
            f = open("/sys/class/thermal/thermal_zone0/temp", "r")
            t = f.readline ()
            cputemp = t[0:2]
            cput = cputemp
        
        print ("T° CPU: "+cput+" °C")
        ecrire("info.t14.txt",cput)
        
        print("Station: "+d.callsign)
        Freq = str(d.freq)+ ' Mhz'
        print("Frequence: "+d.freq)
        ecrire("info.t15.txt",Freq)
        print("Spotnik: "+d.version)
        ecrire("info.t10.txt",d.version)
        print("Script Version: "+d.versionDash)
        ecrire("info.t16.txt",d.versionDash)
        print("Occupation disk: "+(occupdisk))
        ecrire("info.t13.txt",occupdisk)
        print("IP: "+ip)
        ecrire("info.t0.txt",ip)
        print("Ocupation systeme: "+str(chargecpu))
        ecrire("info.t12.txt",str(chargecpu)+" %")
        print("Database: "+str(d.database))
        ecrire("info.V_verdbase.txt",str(d.database))
#WIFI#
    if s.find("pagewifi")!= -1:

        log("Page wifi","red")
        Json="/etc/spotnik/config.json"
        if d.wifistatut == 0:
            with open(Json, 'r') as a:
                infojson = json.load(a)
                wifi_ssid = infojson['wifi_ssid']
                wifi_pass = infojson['wpa_key']
                print("Envoi SSID actuel sur Nextion: "+wifi_ssid)
                print("Envoi PASS actuel sur Nextion: "+wifi_pass)
                ecrire("wifi.t1.txt",str(wifi_ssid))
                ecrire("wifi.t0.txt",str(wifi_pass))
                d.wifistatut = 1   

#PAGE MAJ 
    if s.find("checkversion")!= -1:
        log("PAGE MAJ","red")
        checkversion()

#PAGE UPDATE
    if s.find("majpython")!= -1:

        os.system('sh /opt/spotnik/spotnik2hmi_V2/maj.sh')
    
    if s.find("majnextion")!= -1:
        updatehmi()     

#***************
#* gestion QSY *
#***************

#QSYSALONRRF#
    if s.find("qsyrrf")!= -1:
        d.qsystatut=True
        log("QSY SALON RRF","red")
        ecrire("monitor.Vtxt_saloncon.txt","RESEAU RRF")
        os.system("/etc/spotnik/restart.rrf")
#QSYFON#
    if s.find("qsyfon")!= -1:
        d.qsystatut=True
        log("QSY FON","red")
        ecrire("monitor.Vtxt_saloncon.txt","RESEAU FON")
        os.system("/etc/spotnik/restart.fon")
#QSYSALONTECH#
    if s.find("qsytec")!= -1:
        d.qsystatut=True
        log("QSY SALON TECH","red")
        ecrire("monitor.Vtxt_saloncon.txt","SALON TECHNIQUE")
        os.system("/etc/spotnik/restart.tec")
#QSYINTER#
    if s.find("qsyint")!= -1:
        d.qsystatut=True
        log("QSY INTER","red")
        ecrire("monitor.Vtxt_saloncon.txt","SALON INTER.")
        os.system("/etc/spotnik/restart.int")
#QSYBAV#
    if s.find("qsybav")!= -1:
        d.qsystatut=True
        log("QSY BAVARDAGE","red")
        ecrire("monitor.Vtxt_saloncon.txt","SALON BAVARDAGE")
        #dtmf("100#")
        os.system("/etc/spotnik/restart.bav")
#QSYLOCAL#
    if s.find("qsyloc")!= -1:
        d.qsystatut=True
        log("QSY LOCAL","red")
        ecrire("monitor.Vtxt_saloncon.txt","SALON LOCAL")
        #dtmf("101#")
        os.system("/etc/spotnik/restart.loc")
#QSYSAT#
    if s.find("qsysat")!= -1:
        d.qsystatut=True
        log("QSY SAT","red")
        ecrire("monitor.Vtxt_saloncon.txt","SALON EXP.")
        #dtmf("102#")
        os.system("/etc/spotnik/restart.sat")
#QSYEXP#
    if s.find("qsyexp")!= -1:
        d.qsystatut=True
        log("QSY EXP","red")
        ecrire("monitor.Vtxt_saloncon.txt","SALON EXP.")
        #dtmf("102#")
        os.system("/etc/spotnik/restart.exp")
#QSYREGION#
    if s.find("qsyreg")!= -1:
        d.qsystatut=True
        log("QSY EXP","red")
        ecrire("monitor.Vtxt_saloncon.txt","SALON REGIONAL")
        #dtmf("102#")
        os.system("/etc/spotnik/restart.reg")

#QSYECHOLINK#
    if s.find("qsyel")!= -1:
        log("QSY ECHOLINK","red")
        #dtmf("51#")
        os.system("/etc/spotnik/restart.el")

#DONNMETEO#
    if s.find("dmeteo")!= -1:
        log("BULETIN METEO","red")
        dtmf("*51#")
#PERROQUET
    if s.find("qsydefault")!= -1:
        d.qsystatut=True
        log("QSY PERROQUET","red")
        ecrire("monitor.Vtxt_saloncon.txt","PERROQUET")
        os.system("/etc/spotnik/restart.default")

        
               
    d.firstboot= False
