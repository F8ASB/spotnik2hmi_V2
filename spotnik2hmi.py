#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#Parametrage port serie
import settings as d
from fonctions import *
import serial
import sys
from datetime import  *
import time
from time import time,sleep
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


#ssl._create_default_https_context = ssl._create_unverified_context

portcom(sys.argv[1],sys.argv[2])

salon_current=""
dateold=""
heureSold=""
#routine ouverture fichier de config
# config = ConfigParser.RawConfigParser()
# config.read(svxconfig)

#recuperation indicatif et frequence    
callsign = get_callsign()
freq = get_frequency()

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
    Call_spot()
    ReqaudioOut=os.popen("amixer scontrols", "r").read()
    audioinfo= ReqaudioOut.split("'")
    audioOut=audioinfo[1]	
    print("Peripherique audio Out: "+audioOut)
print(board)

#Envoi des infos 
  
logo(d.versionDash)

print("Proc: "+(str(chargecpu))+"%   " + "CPU: "+cputemp+"°C") 
print("Station: "+d.callsign)
print("Frequence: "+d.freq+" Mhz")
print("Spotnik: Version:"+d.version)

#Reset ecran Nextion

resetHMI()

sleep(1);

ecrire("boot.va0.txt",d.callsign)
ecrire("boot.vascript.txt",d.versionDash)
ecrire("boot.vaverspotnik",d.version)

#Reglage niveau audio visible si Raspberry
if board =='Raspberry Pi':
    ecrireval("trafic.vasound.val","1")

sleep(4);

#envoi indicatif
print("Maj Call ...")

checkversion()

print("Page trafic ...")
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
		
    if tn.find("fon") != -1 and salon_current!="FON":
        ecrire("monitor.Vtxt_saloncon.txt","RESEAU FON")	
        salon_current="FON"
	
    if tn.find("tec") != -1 and salon_current!="TEC":
        ecrire("monitor.Vtxt_saloncon.txt","SALON TECHNIQUE")
        salon_current="TECHNIQUE"
    
    if tn.find("urg") != -1 and salon_current!="INTERNATIONNAL":
        ecrire("monitor.Vtxt_saloncon.txt","SALON INTER.")
        salon_current="INTERNATIONAL"
    
    if tn.find("stv") != -1 and salon_current!="BAVARDAGE":
        ecrire("monitor.Vtxt_saloncon.txt","SALON BAVARDAGE")
        salon_current="BAVARDAGE"
    if tn.find("bav") != -1 and salon_current!="BAVARDAGE":
        ecrire("monitor.Vtxt_saloncon.txt","SALON BAVARDAGE")    
        salon_current="BAVARDAGE"
    if tn.find("cd2") != -1 and salon_current!="LOCAL":
        ecrire("monitor.Vtxt_saloncon.txt","SALON LOCAL")
        salon_current="LOCAL"
    if tn.find("loc") != -1 and salon_current!="LOCAL":
        ecrire("monitor.Vtxt_saloncon.txt","SALON LOCAL")    
        salon_current="LOCAL"

    if tn.find("default") != -1:
        ecrire("monitor.Vtxt_saloncon.txt","PERROQUET")

    if tn.find("sat") != -1:
        ecrire("monitor.Vtxt_saloncon.txt","SALON SATELLITE")          
	
    a.close()


#Gestion des commandes serie reception du Nextion
    s = hmiReadline()
    #enlever les # pour voir trames recus et longueur 
    #if len(s)<59 and len(s)>0:
        #print(s)
        #print(len(s))

#OUIREBOOT#
    if s.find("ouireboot")!= -1:
        print("REBOOT")
        gopage("boot")
        os.system('reboot')

#OUIRESTART#
    if s.find("ouiredem")!= -1:
        print("REDEMARRAGE")
        dtmf("96#")
        gopage ("trafic")
                
#OUIARRET#
    if s.find("ouiarret")!= -1:
        print("ARRET DU SYSTEM")
        os.system('shutdown -h now')

#OUIWIFI
    if s.find("ouimajwifi")!= -1:

        wifi(newssid,newpass)
        page("wifi")
#
#Gestion commande du Nextion
#
                                                                              
#MAJWIFI
    if s.find("majwifi")!= -1:

        print("MAJ Wifi....")
        requete("get t0.txt")
        requete("get t1.txt")

        while 1:
            s = hmiReadline()
            if len(s)<71:
                test= s.split("p")
                newpass= test[1][:-3]
                newssid= test[2][:-3]
                print("New SSID: "+newssid)
                print("New PASS: "+newpass)
                wifistatut = 0
                break
        gopage("confirm")
        ecrire("confirm.t0.txt","CONFIRMER LA MAJ WIFI ?")		
#MAJAUDIO
    if s.find("MAJAUDIO")!= -1:
  
        print("MAJ AUDIO....")
        requete("get nOut.val")

        while 1:
            s = hmiReadline()
            if len(s)<71:
                print("Niveau audio out: "+ str(ord(s[1])))	
                audiooutinfo=str(ord(s[1]))
                break

        requete("get nIn.val")

        while 1:
            s = hmiReadline()
            if len(s)<71:
                
                print("Niveau audio in: "+ str(ord(s[1])))
                audioininfo=str(ord(s[1]))
                setAudio(audioOut,audiooutinfo,audioininfo)             
                break

#PAGE MAJ 
    if s.find("checkversion")!= -1:
        print("PAGE MAJ")
        checkversion()

#PAGE UPDATE
    if s.find("majpython")!= -1:

        os.system('sh /opt/spotnik/spotnik2hmi_v2/maj.sh')
    
    if s.find("majnextion")!= -1:
        updatehmi()

#MUTE AUDIO
    if s.find("MUTEON")!= -1:
        print("MUTE")
        os.system('amixer -c 0 set ' +audioOut+ ' mute')

#UNMUTE AUDIO
    if s.find("MUTEOFF")!= -1:
        print("UNMUTE")
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
        print("Detection bouton meteo")
        get_meteo()

#SPEEDNET#
    if s.find("starttestNet")!= -1:
        print("Detection page speedNet")
        getspeednet()

#MIXER#
    if s.find("mixer")!= -1:
        print("Detection page mixer")
        GetAudioInfo(audioOut)
						
#TRAFIC#		
    if s.find("trafic")!= -1:
        print("Page trafic")

        if tn.find("default") != -1 or tn.find("sat") != -1:
            calltrafic_current=d.salon[tn[0:3].upper()]['call_current']
            print(d.salon[tn[0:3].upper()]['call_current'])
            ecrire("trafic.Txt_call.txt",calltrafic_current)
    ecrire("Txt_date.txt",date)
    ecrire("Txt_heure.txt",heureS)

#DASHBOARD#
    if s.find("dashboard")!= -1:
        print("Page dashboard")
		
#MENU#
    if s.find("menu")!= -1:
        print("Page menu")
#MONITOR#
    if s.find("monitor")!= -1:
        print("Page monitor")
        ecrire("monitor.Txt_nbrrrf.txt",str(len(d.salon['RRF']['node_list'])))
        ecrire("monitor.Txt_nbrtec.txt",str(len(d.salon['TEC']['node_list'])))
        ecrire("monitor.Txt_nbrloc.txt",str(len(d.salon['LOC']['node_list'])))
        ecrire("monitor.Txt_nbrint.txt",str(len(d.salon['INT']['node_list'])))
        ecrire("monitor.Txt_nbrbav.txt",str(len(d.salon['BAV']['node_list'])))
        ecrire("monitor.Txt_nbrfon.txt",str(len(d.salon['FON']['node_list'])))
       
#SCAN#
    if s.find("scan")!= -1:
        print("Page scan")

        ecrire("scan.Txt_listtec.txt",str(d.salon['TEC']['node_list']).replace("'",'').replace(", ",',')[1:-1])
        ecrire("scan.Txt_listloc.txt",str(d.salon['LOC']['node_list']).replace("'",'').replace(", ",',')[1:-1])
        ecrire("scan.Txt_listint.txt",str(d.salon['INT']['node_list']).replace("'",'').replace(", ",',')[1:-1])
        ecrire("scan.Txt_listbav.txt",str(d.salon['BAV']['node_list']).replace("'",'').replace(", ",',')[1:-1])

        ecrire("scan.Txt_nbrtec.txt",str(len(d.salon['TEC']['node_list'])))
        ecrire("scan.Txt_nbrloc.txt",str(len(d.salon['LOC']['node_list'])))
        ecrire("scan.Txt_nbrint.txt",str(len(d.salon['INT']['node_list'])))
        ecrire("scan.Txt_nbrbav.txt",str(len(d.salon['BAV']['node_list'])))
        #ecrire("scan.Txt_nbrfon.txt",d.salon[FON]['node_count'])   
        
        


#WIFI#
    if s.find("wifi")!= -1:
   
        print("Page wifi")
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

#Numkaypad#
    if s.find("keypadnum")!= -1:
   
        print("Page clavier numerique")
	            
#Reglage DIM#
   # if s.find("regdim")== -1:
   #     print"..."
   # else:
   #     print "Reglage DIM recu"
   #     rxdim = s[9:-3]
   #     rdim = rxdim
   #     print rdim
		
#QSYSALONRRF#
    if s.find("qsyrrf")!= -1:

        print("QSY SALON RRF")
        dtmf("96#")
#QSYFON#
    if s.find("qsyfon")!= -1:

        print("QSY FON")
        dtmf("97#")
#QSYSALONTECH#
    if s.find("qsytech")!= -1:
        print("QSY SALON TECH")
        dtmf("98#")
#QSYINTER#
    if s.find("qsyinter")!= -1:
    
        print("QSY INTER")
        dtmf("99#")
#QSYSSTV#
    if s.find("qsybav")!= -1:

        print("QSY BAVARDAGE")
        dtmf("100#")
#QSYCODECS#
    if s.find("qsyloc")!= -1:
  
        print("QSY LOCAL")
        dtmf("101#")
#QSYSAT#
    if s.find("qsysat")!= -1:
  
        print("QSY SAT")
        dtmf("102#")

#DONNMETEO#
    if s.find("dmeteo")!= -1:

        print("BULETIN METEO")
        dtmf("*51#")
#PERROQUET
    if s.find("qsyperroquet")!= -1:

        print("QSY PERROQUET")
        dtmf("95#")
#DASHBOARD#
    if s.find("listdash")!= -1 and tn!="RRF" and tn!="FON":

        print("ENVOI DASH")
        print(d.dashlist)
        ecrire("trafic.g0.txt",d.dashlist)
