#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Parametrage port serie

from fonctions import *
#import echolink

import serial
import sys
from datetime import  *
import time
from time import time,sleep
import requests
#pour lecture fichier de config
import ConfigParser, os
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
ssl._create_default_https_context = ssl._create_unverified_context

portcom(sys.argv[1],sys.argv[2])

#Variables
eof = "\xff\xff\xff"
today = datetime.now()
url = ""
url1 = "http://rrf.f5nlg.ovh/api/svxlink/RRF"
url2 = "http://rrf.f5nlg.ovh/api/svxlink/FON"
url3 = "http://rrf.f5nlg.ovh/api/svxlink/technique"
url4 = "http://rrf.f5nlg.ovh/api/svxlink/international"
url5 = "http://rrf.f5nlg.ovh/api/svxlink/bavardage"
url6 = "http://rrf.f5nlg.ovh/api/svxlink/local"
url7 = "http://rrf.f5nlg.ovh/api/svxlink/satellite"
url8 = "http://127.0.0.1"

versionDash = "2.00b"
wifistatut = 0
dashlist = ""

a = open("/etc/spotnik/network","r")
tn = a.read()

if tn.find("sat") == -1:
    print "NETWORK OK"
else:
    os.system('echo "rrf" > /etc/spotnik/network')
    os.system('/etc/spotnik/restart')
    print "NETWORK CHANGE"
        
#Reglage de luminosite
rdim = 10 #ecran sans reception signal
txdim = 80 # ecran avec reception station

#Chemins fichiers
svxconfig="/etc/spotnik/svxlink.cfg"
cheminversion= open("/etc/spotnik/version", "r")
version = cheminversion.read()
version = version.strip()
conf="/etc/NetworkManager/system-connections/SPOTNIK"

#Chemin log a suivre
svxlogfile = "/tmp/svxlink.log"   #SVXLink log file 

#routine ouverture fichier de config
config = ConfigParser.RawConfigParser()
config.read(svxconfig)

#recuperation indicatif et frequence    
callsign = get_callsign()
freq = get_frequency()
#print indicatif

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
print board

#Envoi des infos 
  
logo(versionDash)
print "Proc: "+(str(chargecpu))+"%   " + "CPU: "+cputemp+"°C" 
print "Station: "+callsign
print "Frequence: "+freq+" Mhz"
print "Spotnik: Version:"+version

#Reset ecran Nextion

resetHMI()

sleep(5);

#envoi indicatif
print "Maj Call ..."
ecrire("boot.va0.txt",str(callsign))
#Affichage de la page Dashboard
print "Page trafic ..."
page("trafic")

while 1:
#Gestion Date et heure (en FR)	
    dashlist = ""
    today = datetime.now()
    locale.setlocale(locale.LC_TIME,'')	
    date = (today.strftime('%d-%m-%Y'))
    heure = (today.strftime('%H:%M'))
    heureS =(today.strftime('%H:%M:%S'))
    ecrire("trafic.t18.txt",date)
    ecrire("trafic.t8.txt",heureS)
    ecrire("trafic.V_heure.txt",heure)
    requete("vis p9,0")
    ecrire("trafic.t15.txt",heure)
    #Definition et affichage link actif	
    a = open("/etc/spotnik/network","r")
    tn = a.read()

    if tn.find("rrf") == -1:
        ecrire("page200.t3.txt","Mode autonome")
    else:
        ecrire("trafic.t0.txt","RESEAU RRF")
        url = url1
		
    if tn.find("fon") == -1:
        ecrire("page200.t3.txt","Mode autonome")
    else:
        ecrire("trafic.t0.txt","RESEAU FON")	
        url = url2
	
    if tn.find("tec") == -1:
        ecrire("page200.t3.txt","Mode autonome")
    else:
        ecrire("trafic.t0.txt","SALON TECHNIQUE")
        url = url3

    if tn.find("int") == -1:
        ecrire("page200.t3.txt","Mode autonome")
    else:
        ecrire("trafic.t0.txt","SALON INTER.")
        url = url4    

    if tn.find("bav") == -1:
        ecrire("page200.t3.txt","Mode autonome")
    else:
        ecrire("trafic.t0.txt","SALON BAVARDAGE")
        url = url5

    if tn.find("loc") == -1:
        ecrire("page200.t3.txt","Mode autonome")
    else:
        ecrire("trafic.t0.txt","SALON LOCAL")
        url = url6

    if tn.find("sat") == -1:
        ecrire("page200.t3.txt","Mode autonome")
    else:
        ecrire("trafic.t0.txt","SALON SATELLITE")    
	url = url7	

    if tn.find("reg") == -1:
        ecrire("page200.t3.txt","Mode autonome")
    else:
        ecrire("trafic.t0.txt","SALON REGIONAL")    
	url = url8	

    if tn.find("default") == -1:
        ecrire("page200.t3.txt","Mode autonome")
    else:
        ecrire("trafic.t0.txt","PERROQUET")

    a.close()

#
#Gestion status TRX
#	

# Request HTTP datas
    try:
        r = requests.get(url, verify=False, timeout=10)
        page_web = r.content
    except requests.exceptions.ConnectionError as errc:
        print ('Error Connecting:', errc)
        ecrire("trafic.t1.txt","DASH HS")
    except requests.exceptions.Timeout as errt:
        print ('Timeout Error:', errt)
        ecrire("trafic.t1.txt","DASH HS")
	
#controle si page Dashboard RRF ou TEC
    if tn.find("rrf") != -1:
        fincall= page_web.find ('"transmitter":"')
        #dashdebut= page_web.find ('"nodes":[')
        #dashfin= page_web.find ('],"transmit"')

        if fincall >0:
            tramecall= (page_web[(fincall):fincall+30])
        #     tramedash= (page_web[(dashdebut):(dashfin)])
            call = tramecall.split('"')
            print call[3]
            #dashlist= tramedash.replace('"','')
            #print "dashlist:"+dashlist
            TxStation = call[3]
           # setdim(txdim)
        else:
            TxStation = ""
            #setdim(rdim)

    if tn.find("tec") != -1:
        fincall= page_web.find ('"transmitter":"')	
        dashdebut= page_web.find ('"nodes":[')
        dashfin= page_web.find ('","TECHNIQUE"]')
		
        if fincall >0:
            tramecall= (page_web[(fincall):fincall+30])
            tramedash= (page_web[(dashdebut+10):(dashfin)])
            call = tramecall.split('"')
            print call[3]
            dashfiltre= tramedash.replace('"','')
            dashlist=dashfiltre.replace(',TEC','')
            print "dashlist:"+dashlist
            TxStation = call[3]
            #setdim(txdim)
        else:
            TxStation = ""
            #dimsend ='dim='+str(rdim)+eof
            #setdim(rdim)
    if tn.find("int") != -1:
        fincall= page_web.find ('"transmitter":"')  
        dashdebut= page_web.find ('"nodes":[')
        dashfin= page_web.find (',"INTERNATIONAL"]')
        
        if fincall >0:
            tramecall= (page_web[(fincall):fincall+30])
            tramedash= (page_web[(dashdebut+10):(dashfin)])
            call = tramecall.split('"')
            print call[3]
            dashlist= tramedash.replace('"','')
            print "dashlist:"+dashlist
            TxStation = call[3]
            #setdim(txdim)
        else:
            TxStation = ""
            #dimsend ='dim='+str(rdim)+eof
            #setdim(rdim)
    
    if tn.find("bav") != -1:
        fincall= page_web.find ('"transmitter":"')  
        dashdebut= page_web.find ('"nodes":[')
        dashfin= page_web.find (',"BAVARDAGE"]')
        
        if fincall >0:
            tramecall= (page_web[(fincall):fincall+30])
            tramedash= (page_web[(dashdebut+10):(dashfin)])
            call = tramecall.split('"')
            print call[3]
            dashlist= tramedash.replace('"','')
            print "dashlist:"+dashlist
            TxStation = call[3]
            #setdim(txdim)
        else:
            TxStation = ""
            #dimsend ='dim='+str(rdim)+eof
            #setdim(rdim)

    if tn.find("loc") != -1:
        fincall= page_web.find ('"transmitter":"')  
        dashdebut= page_web.find ('"nodes":[')
        dashfin= page_web.find (',"LOCAL"]')
        
        if fincall >0:
            tramecall= (page_web[(fincall):fincall+30])
            tramedash= (page_web[(dashdebut+10):(dashfin)])
            call = tramecall.split('"')
            print call[3]
            dashlist= tramedash.replace('"','')
            print "dashlist:"+dashlist
            TxStation = call[3]
            #setdim(txdim)
        else:
            TxStation = ""
            #dimsend ='dim='+str(rdim)+eof
            #setdim(rdim)        

    if tn.find("fon") != -1:
        fincall= page_web.find ('"transmitter":"')
      
        if fincall >0:
            tramecall= (page_web[(fincall):fincall+30])
         
            call = tramecall.split('"')
            print call[3]
          
            TxStation = call[3]
            #setdim(txdim)
        else:
            TxStation = ""
            #dimsend ='dim='+str(rdim)+eof
            #setdim(rdim)
    ecrire("trafic.t1.txt",TxStation)
    if tn.find("sat") != -1:
        fincall= page_web.find ('"transmitter":"')
      
        if fincall >0:
            tramecall= (page_web[(fincall):fincall+30])
         
            call = tramecall.split('"')
            print call[3]
          
            TxStation = call[3]
            #setdim(txdim)
        else:
            TxStation = ""
            #dimsend ='dim='+str(rdim)+eof
            #setdim(rdim)
    ecrire("trafic.t1.txt",TxStation)

#Gestion des commandes serie reception du Nextion
    s = hmiReadline()

    if len(s)<59 and len(s)>0:
        print s
#		print len(s)

#REBOOT
    if s.find("reboot")== -1:
        ecrire("page200.t3.txt","Mode autonome")
    else:
        print "Reboot command...."

#
#GESTION DU OUI DE LA PAGE CONFIRM
#


#OUIREBOOT#
    if s.find("ouireboot")== -1:
        ecrire("page200.t3.txt","Mode autonome")
    else:
        print "REBOOT"
        page("boot")
        os.system('reboot')

#OUIRESTART#
    if s.find("ouiredem")== -1:
        ecrire("page200.t3.txt","Mode autonome")
    else:
        print "REDEMARRAGE"
        dtmf("96#")
        page("trafic")
                
#OUIARRET#
    if s.find("ouiarret")== -1:
        ecrire("page200.t3.txt","Mode autonome")
    else:
        print "ARRET DU SYSTEM"
        page("arret")
        os.system('shutdown -h now')

#OUIWIFI
    if s.find("ouimajwifi")== -1:
        ecrire("page200.t3.txt","Mode autonome")
    else:
        wifi(newssid,newpass)
        page("wifi")

#OUIQUITTERECOLINK#
    if s.find("ouiquitecho")== -1:
        ecrire("page200.t3.txt","Mode autonome")
    else:
        print "OUI QUITTE ECHOLINK"
        dtmf("#")
        page("trafic")
        dtmf("96#")
                
#OUIDECONNECTIONNODE#
    if s.find("ouideconnectenode")== -1:
        ecrire("page200.t3.txt","Mode autonome")
    else:
        print "DECONNECTE NODE"
        page("echolink")
        dtmf("#")
#
#Gestion commande du Nextion
#
                                                                              
#STOP
    if s.find("shutdown")== -1:
        ecrire("page200.t3.txt","Mode autonome")
    else:
        print "Shutdown command...."
        page("confirm")
        ecrire("confirm.t0.txt","CONFIRMER UN ARRET TOTAL ?")			
#RESTART
    if s.find("restart")== -1:
        ecrire("page200.t3.txt","Mode autonome")
    else:
        print "Restart command...."
        page("confirm")
        ecrire("confirm.t0.txt","CONFIRMER LE REDEMARRAGE LOGICIEL ?")

#REBOOT
    if s.find("reboot")== -1:
        ecrire("page200.t3.txt","Mode autonome")
    else:
        print "Reboot command...."
        page("confirm")
        ecrire("confirm.t0.txt","CONFIRMER LE REBOOT GENERAL ?")

#MAJWIFI
    if s.find("maj")== -1:
        ecrire("page200.t3.txt","Mode autonome")
    else:
        print "MAJ Wifi...."
        requete("get t0.txt")
        requete("get t1.txt")

        while 1:
            s = hmiReadline()
            if len(s)<71:
                test= s.split("p")
                newpass= test[1][:-3]
                newssid= test[2][:-3]
                print "New SSID: "+newssid
                print "New PASS: "+newpass
                wifistatut = 0
                break
        page("confirm")
        ecrire("confirm.t0.txt","CONFIRMER LA MAJ WIFI ?")		
#INFO#	
    if s.find("info")== -1:
        ecrire("page200.t3.txt","Mode autonome")
    else:
        print "Detection bouton info"
        cput = '"'+cputemp+' C'+'"' 
        ecrire("info.t14.txt",cputemp)
        print "Station: "+callsign
        Freq = str(freq)+ ' Mhz'
        print "Frequence: "+freq
        ecrire("info.t15.txt",Freq)
        print "Spotnik: "+version
        ecrire("info.t10.txt",version)
        print "Script Version: "+versionDash
        ecrire("info.t16.txt",versionDash)
        print "Occupation disk: "+(occupdisk)
        ecrire("info.t13.txt",occupdisk)
        print "IP: "+ip
        ecrire("info.t0.txt",ip)
        print "occupation systeme: "+str(chargecpu)
        ecrire("info.t12.txt",str(chargecpu)+" %")
        dtmf("*#")
#METEO#
    if s.find("meteo")== -1:
        ecrire("page200.t3.txt","Mode autonome")
    else:
        print "Detection bouton meteo"
        #METEO
        get_meteo()
#NODE#
    if s.find("nodeqsy")== -1:
        ecrire("page200.t3.txt","Mode autonome")
    else:
        print "Node choisi"
        print s[s.find("nodeqsy")+7:s.find("nodeqsy")+13]+"#"
        dtmf(s[s.find("nodeqsy")+7:s.find("nodeqsy")+13]+"#")
        page("echolink")							
#TRAFIC#		
    if s.find("trafic")== -1:
        ecrire("page200.t3.txt","Mode autonome")
    else:
        print "Page trafic"
		
#DASHBOARD#
    if s.find("dashboard")== -1:
        ecrire("page200.t3.txt","Mode autonome")
    else:
        print "Page dashboard"
		
#MENU#
    if s.find("menu")== -1:
        ecrire("page200.t3.txt","Mode autonome")
    else:
        print "Page menu"
#WIFI#
    if s.find("wifi")== -1:
        ecrire("page200.t3.txt","Mode autonome")
    else:
        print "Page wifi"
        Json="/etc/spotnik/config.json"
        if wifistatut == 0:
            with open(Json, 'r') as a:
                infojson = json.load(a)
                wifi_ssid = infojson['wifi_ssid']
                wifi_pass = infojson['wpa_key']
                print "Envoi SSID actuel sur Nextion: "+wifi_ssid
                print "Envoi PASS actuel sur Nextion: "+wifi_pass
                ecrire("wifi.t1.txt",str(wifi_ssid))
                ecrire("wifi.t0.txt",str(wifi_pass))
                wifistatut = 1	

#ECHOLINK#
    if s.find("echolink")== -1:
        ecrire("page200.t3.txt","Mode autonome")
    else:
        print "Page echolink"
#Numkaypad#
    if s.find("keypadnum")== -1:
        ecrire("page200.t3.txt","Mode autonome")
    else:
        print "Page clavier numerique"
	
#Connect Echolink#
    if s.find("connexionecho")== -1:
        ecrire("page200.t3.txt","Mode autonome")
    else:
        print "Bouton connexion echolink"
		
		
#Deconnect Echolink#
    if s.find("deconnectioncho")== -1:
        ecrire("page200.t3.txt","Mode autonome")
    else:
        print "Bouton deconnexion echolink"
                

#Reglage DIM#
    if s.find("regdim")== -1:
        ecrire("page200.t3.txt","Mode autonome")
    else:
        print "Reglage DIM recu"
        rxdim = s[9:-3]
        print rdim
        rdmi= rxdim
		
#QSYSALONRRF#
    if s.find("qsyrrf")== -1:
        ecrire("page200.t3.txt","Mode autonome")
    else:
        print "QSY SALON RRF"
        dtmf("96#")
#QSYFON#
    if s.find("qsyfon")== -1:
        ecrire("page200.t3.txt","Mode autonome")
    else:
        print "QSY FON"
        dtmf("97#")
#QSYSALONTECH#
    if s.find("qsytech")== -1:
        ecrire("page200.t3.txt","Mode autonome")
    else:
        print "QSY SALON TECH"
        dtmf("98#")
#QSYINTER#
    if s.find("qsyinter")== -1:
        ecrire("page200.t3.txt","Mode autonome")
    else:
        print "QSY SALON INTER"
        dtmf("99#")
#QSYBAV#
    if s.find("qsyloc")== -1:
        ecrire("page200.t3.txt","Mode autonome")
    else:
        print "QSY SALON LOCAL"
        dtmf("101#")
#QSYLOCAL#
    if s.find("qsybav")== -1:
        ecrire("page200.t3.txt","Mode autonome")
    else:
        print "QSY SALON BAVARDAGE"
        dtmf("100#")
#QSYSAT#
    if s.find("qsysat")== -1:
        ecrire("page200.t3.txt","Mode autonome")
    else:
        print "QSY SALON SAT"
        dtmf("102#")

#QSYSAT#
    if s.find("qsyreg")== -1:
        ecrire("page200.t3.txt","Mode autonome")
    else:
        print "QSY SALON REGIONAL"
        dtmf("104#")

#DONNMETEO#
    if s.find("dmeteo")== -1:
        ecrire("page200.t3.txt","Mode autonome")
    else:
        print "BULETIN METEO"
        dtmf("*51#")
#PERROQUET
    if s.find("qsyperroquet")== -1:
        ecrire("page200.t3.txt","Mode autonome")
    else:
        print "QSY PERROQUET"
        dtmf("95#")
#DASHBOARD#
    if s.find("listdash")== -1 and tn!="rrf" and tn!="fon":
        ecrire("page200.t3.txt","Mode autonome")
    else:
        print "ENVOI DASH"
        ecrire("trafic.g0.txt",dashlist)
