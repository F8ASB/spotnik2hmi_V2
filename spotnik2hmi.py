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


portcom(sys.argv[1],sys.argv[2])

if len(sys.argv)==4:

    if sys.argv[3]=="DEBUG": 
        print("MODE DEBUG")
        debugON()

qsystatut=False

salon_current=""
dateold=""
heureSold=""
statutradio=""
firstboot= True
rpi3bplus=False
#audiooutinfo=0
#audioininfo=0
#routine ouverture fichier de config
# config = ConfigParser.RawConfigParser()
# config.read(svxconfig)

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

#temperature CPU
f = open("/sys/class/thermal/thermal_zone0/temp", "r")
t = f.readline ()
cputemp = t[0:2]

#Memoire SD libre
disk= getDiskSpace()
occupdisk = str(disk)

#Utilisation CPU
chargecpu= getCPUuse()

#Detection carte

tmp = os.popen("uname -a").readline()
if 'sun8i' in tmp:
    board = 'Orange Pi'
else:
    board = 'Raspberry Pi'
    #peripheriques audio Out
    ReqaudioOut=os.popen("amixer scontrols", "r").read()
    audioinfo= ReqaudioOut.split("'")
    audioOut=audioinfo[1]   
    log(("Peripherique audio Out: "+audioOut),"white")
    log(board,"white")
    
    #Detection RPI 3 B+
    revision=getrevision()

    if revision=="a020d3":
        log("RASPBERRY 3B+ DETECTION","white")
        rpi3bplus=True
    else:
        log("pas de 3B+","white")
 
 os.system('amixer -c 0 set ' +audioOut+ ' unmute')   

#Envoi des infos 
logo(d.versionDash)

print("     +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+")
print("     +    "+"Proc: "+(str(chargecpu))+"%   " + "CPU: "+cputemp+"°C"+ "    +   " + "Spotnik: Version:"+d.version+"  +")
print("     +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+")
print("     +   " +"Station: "+d.callsign + "       Frequence: "+d.freq+" Mhz"+"    +")
print("     +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+")

resetHMI()

sleep(1);

ecrire("boot.va0.txt",d.callsign)
ecrire("boot.vascript.txt",d.versionDash)
ecrire("boot.vaverspotnik.txt",d.version)

#Reglage niveau audio visible si Raspberry
if board =='Raspberry Pi':
    ecrireval("trafic.vasound.val","1")

sleep(4);

#envoi indicatif
log("Maj Call ...","red")

checkversion()

gopage("trafic")

os.system ("clear")

while True:
    #Gestion Date et heure (en FR)
    d.dashlist = ""
    d.today = datetime.now()
    locale.setlocale(locale.LC_TIME,'') 
    date = (d.today.strftime('%d-%m-%Y'))
    heureS =(d.today.strftime('%H:%M'))
    if date != dateold:
        ecrire("Txt_date.txt",date)
        dateold=date
    if heureS != heureSold:
        ecrire("Txt_heure.txt",heureS)
        heureSold= heureS

    requete("vis p9,0")

    #tmp = datetime.datetime.now()
    timestamp = d.today.strftime('%d-%m-%Y %H:%M:%S')

    for key in d.salon:

        try:
            r = requests.get(d.salon[key]['url'], verify=False, timeout=10)
            page = r.text
        except requests.exceptions.ConnectionError as errc:
            print(('Error Connecting:', errc))
        except requests.exceptions.Timeout as errt:
            print(('Timeout Error:', errt))    
        # Transmitter

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
        else:            
            if d.salon[key]['transmit'] is True:
                d.salon[key]['call_current'] = ''
                d.salon[key]['call_previous'] = ''
                d.monitor = timestamp + " " + key + " T OFF"
                d.salon[key]['transmit'] = False
                ecrire("monitor.Txt_statut.txt",d.monitor)
                print(d.monitor)

        # Nodes

        search_start = page.find('nodes":[')                    # Search this pattern
        search_start += 9                                       # Shift...
        search_stop = page.find('],"TXmit"', search_start)      # And close it...

        tmp = page[search_start:search_stop]
        tmp = tmp.replace('"', '')

        d.salon[key]['node_list'] = tmp.split(',')

        for n in ['RRF', 'RRF2', 'RRF3', 'TECHNIQUE', 'BAVARDAGE', 'INTERNATIONAL', 'LOCAL', 'FON']:
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

    #detection connexion salon

    a = open("/etc/spotnik/network","r")
    tn = a.read()

    if tn.find("rrf") != -1 and salon_current!="RRF":
        ecrire("monitor.Vtxt_saloncon.txt","RESEAU RRF")
        salon_current="RRF"
        ecrire("trafic.g0.txt","")
        if qsystatut==False and firstboot==False:
            gopage("qsy")
        qsystatut=False
        
    if tn.find("fon") != -1 and salon_current!="FON":
        ecrire("monitor.Vtxt_saloncon.txt","RESEAU FON")    
        salon_current="FON"
        ecrire("trafic.g0.txt","")
        if qsystatut==False and firstboot==False:
            gopage("qsy")
        qsystatut=False
    
    if tn.find("tec") != -1 and salon_current!="TEC":
        ecrire("monitor.Vtxt_saloncon.txt","SALON TECHNIQUE")
        salon_current="TEC"
        ecrire("trafic.g0.txt","")
        if qsystatut==False and firstboot==False:
            gopage("qsy")
        qsystatut=False

    if tn.find("int") != -1 and salon_current!="INT":
        ecrire("monitor.Vtxt_saloncon.txt","SALON INTER.")
        salon_current="INT"
        ecrire("trafic.g0.txt","")
        if qsystatut==False and firstboot==False:
            gopage("qsy")
        qsystatut=False

    if tn.find("bav") != -1 and salon_current!="BAV":
        ecrire("monitor.Vtxt_saloncon.txt","SALON BAVARDAGE")    
        salon_current="BAV"
        ecrire("trafic.g0.txt","")
        if qsystatut==False and firstboot==False:
            gopage("qsy")
        qsystatut=False

    if tn.find("loc") != -1 and salon_current!="LOCAL":
        ecrire("monitor.Vtxt_saloncon.txt","SALON LOCAL")    
        salon_current="LOC"
        ecrire("trafic.g0.txt","")
        if qsystatut==False and firstboot==False:
            #gopage("qsy")
        qsystatut=False

    if tn.find("default") != -1 and salon_current!="PER":
        ecrire("monitor.Vtxt_saloncon.txt","PERROQUET")
        ecrire("trafic.g0.txt","")
        salon_current="PER"
        if qsystatut==False and firstboot==False:
            gopage("qsy") 
        f qsystatut==False and firstboot==True:
            gopage("Parrot") 
        qsystatut=False

    if tn.find("sat") != -1 and salon_current!="SAT":
        ecrire("monitor.Vtxt_saloncon.txt","SALON SATELLITE")
        ecrire("trafic.g0.txt","") 
        salon_current="SAT"
        if qsystatut==False and firstboot==False:
            gopage("qsy")
        qsystatut=False   

    if tn.find("el") != -1 and salon_current!="ECH":
        ecrire("monitor.Vtxt_saloncon.txt","ECHOLINK")
        ecrire("trafic.g0.txt","")
        salon_current="ECH"
        if qsystatut==False and firstboot==False:
            gopage("qsy")
        qsystatut=False

#Gestion salon Perroquet TX et RX
    if tn.find("default") != -1 and salon_current=="PER":
        
        p= open("/sys/class/gpio/"+nbgpiosql+"/value","r")
        gpiorx_value = p.read()
        
        if gpiorx_value.find("1") != -1 and statutradio!="RX":
             log("RX Detected","white")
             statutradio="RX"
             #requete("vis p2,1")
             ecrireval(Vnbr_ledparrot.val,"1")
             

        elif gpiorx_value.find("0") != -1 and statutradio!="TX" and statutradio!="":
             log("RX OFF","white")
             #requete("vis p2,0")
             ecrireval(Vnbr_ledparrot.val,"0")

             statutradio=""

        p.close()

        q= open("/sys/class/gpio/"+nbgpioptt+"/value","r")
        gpiotx_value = q.read()
        
        if gpiotx_value.find("1") != -1 and statutradio!="TX":
             log("Tx ON","white")
             statutradio="TX"
             #requete("vis p3,1")
             ecrireval(Vnbr_ledparrot.val,"2")
             
        elif gpiotx_value.find("0") != -1 and statutradio!="RX" and statutradio!="":
             log("Tx OFF","white")
             #requete("vis p3,0")
             ecrireval(Vnbr_ledparrot.val,"0")
             statutradio=""

        q.close()

    a.close()


#Gestion des commandes serie reception du Nextion
    s = hmiReadline()
    if len(s)<59 and len(s)>0:
        log(s,"blue")


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
        
        if rpi3bplus==True:
            wifi3bplus(newssid,newpass)
        else:
            wifi(newssid,newpass)
        log("ECRITURE INFO WIFI DANS JSON + CONFIG","red")
        
        gopage("reglage")
#
#Gestion commande du Nextion
#
                                                                              
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

#MAJAUDIO
    if s.find("MAJAUDIO")!= -1:
  
        log("MAJ AUDIO....","red")
        requete("get nOut.val")

        while 1:
            s = hmiReadline()
            log(s,"blue")
            sa=s[2:]
            log(sa,"blue")
   
            
            
            if len(sa)<71:
                if sa[2:3] == "x":
                    log(("Niveau audio out: "+ str(int(sa[3:5], 16))),"white")  
                    audiooutinfo=str(int(sa[3:5], 16))
                    break
                elif sa[2:3] == "t":
                    log("Niveau audio out: "+ "9","white")  
                    audiooutinfo=9
                    break
                elif sa[2:3] == "n":
                    log("Niveau audio out: "+ "10","white") 
                    audiooutinfo=10
                    break
                elif sa[2:3] == "r":
                    log("Niveau audio out: "+ "13","white") 
                    audiooutinfo=13
                    break
                else:
                    log(("Niveau audio out: "+ str(ord(sa[1]))),"white")    
                    audiooutinfo=str(ord(sa[1]))
                    break
        
        time.sleep(1)

        requete("get nIn.val")

        while 1:

            s = hmiReadline()
            log(s,"blue")
            sb=s[2:]
            log(sb,"blue")

            if len(sb)<71:
                if sb[2:3] == "x":
                    log(("Niveau audio in: "+ str(int(sb[3:5], 16))),"white")   
                    audioininfo=str(int(sb[3:5], 16))
                    setAudio(audioOut,audiooutinfo,audioininfo)
                    break
                elif sb[2:3] == "t":
                    log("Niveau audio in: "+ "9","white")   
                    audioininfo=9
                    setAudio(audioOut,audiooutinfo,audioininfo)
                    break
                elif sb[2:3] == "n":
                    log("Niveau audio in: "+ "10","white")  
                    audioininfo=10
                    setAudio(audioOut,audiooutinfo,audioininfo)
                    break
                elif sb[2:3] == "r":
                    log("Niveau audio in: "+ "13","white")  
                    audioininfo=13
                    setAudio(audioOut,audiooutinfo,audioininfo)
                    break
                else:
                    log(("Niveau audio in: "+ str(ord(sb[1]))),"white") 
                    audioininfo=str(ord(sb[1]))
                    setAudio(audioOut,audiooutinfo,audioininfo)
                    break       


#PAGE MAJ 
    if s.find("checkversion")!= -1:
        log("PAGE MAJ","red")
        checkversion()

#PAGE UPDATE
    if s.find("majpython")!= -1:

        os.system('sh /opt/spotnik/spotnik2hmi_V2/maj.sh')
    
    if s.find("majnextion")!= -1:
        updatehmi()

#MUTE AUDIO
    if s.find("MUTEON")!= -1:
        log("MUTE","white")
        os.system('amixer -c 0 set ' +audioOut+ ' mute')

#UNMUTE AUDIO
    if s.find("MUTEOFF")!= -1:
        log("UNMUTE","white")
        os.system('amixer -c 0 set ' +audioOut+ ' unmute')         

#INFO#  
    if s.find("info")!= -1:
        print("Detection bouton info")
        cput = '"'+cputemp+' C'+'"' 
        ecrire("info.t14.txt",cputemp)
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
        print("occupation systeme: "+str(chargecpu))
        ecrire("info.t12.txt",str(chargecpu)+" %")

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
        GetAudioInfo(audioOut)
                        
#TRAFIC#        
    if s.find("trafic")!= -1:
        log("Page trafic","red")
        ecrire("Txt_date.txt",date)
        ecrire("Txt_heure.txt",heureS)
        
        if salon_current=="TEC":

            calltrafic_current=d.salon["TEC"]['call_current']
            ecrire("trafic.Txt_call.txt","")
            ecrire("trafic.Txt_call.txt",calltrafic_current)

        if salon_current=="RRF":

            calltrafic_current=d.salon["RRF"]['call_current']
            ecrire("trafic.Txt_call.txt","")
            ecrire("trafic.Txt_call.txt",calltrafic_current)
        if salon_current=="FON":

            calltrafic_current=d.salon["FON"]['call_current']
            ecrire("trafic.Txt_call.txt","")
            ecrire("trafic.Txt_call.txt",calltrafic_current)
        
        if salon_current=="INT":

            calltrafic_current=d.salon["INT"]['call_current']
            ecrire("trafic.Txt_call.txt","")
            ecrire("trafic.Txt_call.txt",calltrafic_current)
        
        if salon_current=="BAV":

            calltrafic_current=d.salon["BAV"]['call_current']
            ecrire("trafic.Txt_call.txt","")
            ecrire("trafic.Txt_call.txt",calltrafic_current)

        if salon_current=="LOC":

            calltrafic_current=d.salon["LOC"]['call_current']
            ecrire("trafic.Txt_call.txt","")
            ecrire("trafic.Txt_call.txt",calltrafic_current)

        
            

    

#DASHBOARD#
    if s.find("dashboard")!= -1:
        log("Page dashboard","red")
        
#MENU#
    if s.find("menu")!= -1:
        log("Page menu","red")
#MONITOR#
    if s.find("monitor")!= -1:
        log("Page monitor","red")
        ecrire("monitor.Txt_nbrrrf.txt",str(len(d.salon['RRF']['node_list'])))
        ecrire("monitor.Txt_nbrtec.txt",str(len(d.salon['TEC']['node_list'])))
        ecrire("monitor.Txt_nbrloc.txt",str(len(d.salon['LOC']['node_list'])))
        ecrire("monitor.Txt_nbrint.txt",str(len(d.salon['INT']['node_list'])))
        ecrire("monitor.Txt_nbrbav.txt",str(len(d.salon['BAV']['node_list'])))
        ecrire("monitor.Txt_nbrfon.txt",str(len(d.salon['FON']['node_list'])))

#SCAN#
    if s.find("scan")!= -1:
        log("Page scan","red")

        ecrire("scan.Txt_listtec.txt",str(d.salon['TEC']['node_list']).replace("'",'').replace(", ",',')[1:-1])
        ecrire("scan.Txt_listloc.txt",str(d.salon['LOC']['node_list']).replace("'",'').replace(", ",',')[1:-1])
        ecrire("scan.Txt_listint.txt",str(d.salon['INT']['node_list']).replace("'",'').replace(", ",',')[1:-1])
        ecrire("scan.Txt_listbav.txt",str(d.salon['BAV']['node_list']).replace("'",'').replace(", ",',')[1:-1])

        ecrire("scan.Txt_nbrtec.txt",str(len(d.salon['TEC']['node_list'])))
        ecrire("scan.Txt_nbrloc.txt",str(len(d.salon['LOC']['node_list'])))
        ecrire("scan.Txt_nbrint.txt",str(len(d.salon['INT']['node_list'])))
        ecrire("scan.Txt_nbrbav.txt",str(len(d.salon['BAV']['node_list'])))
       

#Numkaypad#
    if s.find("keypadnum")!= -1:
        log("Page clavier numerique","red")

#QSYSALONRRF#
    if s.find("qsyrrf")!= -1:
        qsystatut=True
        log("QSY SALON RRF","red")
        os.system("/etc/spotnik/restart.rrf")
#QSYFON#
    if s.find("qsyfon")!= -1:
        qsystatut=True
        log("QSY FON","red")
        os.system("/etc/spotnik/restart.fon")
#QSYSALONTECH#
    if s.find("qsytech")!= -1:
        qsystatut=True
        log("QSY SALON TECH","red")
        os.system("/etc/spotnik/restart.tec")
#QSYINTER#
    if s.find("qsyinter")!= -1:
        qsystatut=True
        log("QSY INTER","red")
        os.system("/etc/spotnik/restart.int")
#QSYSSTV#
    if s.find("qsybav")!= -1:
        qsystatut=True
        log("QSY BAVARDAGE","red")
        #dtmf("100#")
        os.system("/etc/spotnik/restart.bav")
#QSYCODECS#
    if s.find("qsyloc")!= -1:
        qsystatut=True
        log("QSY LOCAL","red")
        #dtmf("101#")
        os.system("/etc/spotnik/restart.loc")
#QSYSAT#
    if s.find("qsysat")!= -1:
        qsystatut=True
        log("QSY SAT","red")
        #dtmf("102#")
        os.system("/etc/spotnik/restart.sat")

#DONNMETEO#
    if s.find("dmeteo")!= -1:
        log("BULETIN METEO","red")
        dtmf("*51#")
#PERROQUET
    if s.find("qsyperroquet")!= -1:
        qsystatut=True
        log("QSY PERROQUET","red")
        os.system("/etc/spotnik/restart.default")
        
#DASHBOARD#
    if s.find("listdash")!= -1 and salon_current!="RRF" and salon_current!="FON":
        log("List dash","red")
        if salon_current=="RRF" or salon_current=="FON"or salon_current=="SAT"or salon_current=="ECH"or salon_current=="PER":
            ecrire("trafic.g0.txt","")
        else:    
            ecrire("trafic.g0.txt",str(d.salon[salon_current]['node_list']).replace("'",'').replace(", ",',')[1:-1])                
    firstboot= False
