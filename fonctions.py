#!/usr/bin/env python3
# -*- coding: utf-8 -*-

############################################################################
# .-') _   ('-.  ) (`-.      .-') _                            .-') _      #        
#    ( OO ) )_(  OO)  ( OO ).   (  OO) )                          ( OO ) ) #
#,--./ ,--,'(,------.(_/.  \_)-./     '._ ,-.-')  .-'),-----. ,--./ ,--,'  #
#|   \ |  |\ |  .---' \  `.'  / |'--...__)|  |OO)( OO'  .-.  '|   \ |  |\  #
#|    \|  | )|  |      \     /\ '--.  .--'|  |  \/   |  | |  ||    \|  | ) #
#|  .     |/(|  '--.    \   \ |    |  |   |  |(_/\_) |  |\|  ||  .     |/  #
#|  |\    |  |  .--'   .'    \_)   |  |  ,|  |_.'  \ |  | |  ||  |\    |   #
#|  | \   |  |  `---. /  .'.  \    |  | (_|  |      `'  '-'  '|  | \   |   #
#`--'  `--'  `------''--'   '--'   `--'   `--'        `-----' `--'  `--'   #
#                                 TEAM: F0DEI,F5SWB,F8ASB      #    
############################################################################
#import echolink
import settings as d
import serial
import time
import os
import sys
import struct
import subprocess
import socket
import fcntl
import struct
from datetime import  *
import time
from time import time,sleep
import locale
import mmap
import requests
import configparser, os
try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen

#librairie Speedtest
import speedtest

#partie dashboard
#import urllib.request, urllib.error, urllib.parse
import ssl
url = "http://rrf.f5nlg.ovh"
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

#Variables:
#eof = '\xff\xff\xff'
eof=bytes([0xFF,0xFF,0xFF])
port= 0 
#Chemin fichier Json
Json="/etc/spotnik/config.json"
icao="/opt/spotnik/spotnik2hmi_V2/datas/icao.cfg"
#routine ouverture fichier de config
svxconfig="/etc/spotnik/svxlink.cfg"
config = configparser.RawConfigParser()
config.read(svxconfig)
#reglage audio
import alsaaudio

#Fonction pour lancement routin console

from subprocess import Popen, PIPE

DEBUG=True

#Fonction Debug
def log(s,color):
    if DEBUG:
        if color=="red":
            print ('\x1b[7;30;41m'+"DEBUG: "+s+'\x1b[0m')
        if color=="blue":
            print ('\x1b[7;34;40m'+"DEBUG: "+s+'\x1b[0m')
        if color=="yellow":
            print ('\x1b[7;30;43m'+"DEBUG: "+s+'\x1b[0m')
        if color=="white":
            print ('\x1b[7;30;47m'+"DEBUG: "+s+'\x1b[0m')
        if color=="none":
            print (s)   

def portcom(portseriel,vitesse):
    global port
    global screentype
    global porthmi
    
    porthmi=portseriel

    port=serial.Serial(port='/dev/'+portseriel,baudrate=vitesse,timeout=1, writeTimeout=1)
    print("Port serie: " +portseriel+" Vitesse: "+vitesse)

    cmdinfo= eof + b'connect' + eof 
    port.write(cmdinfo)

    r = port.read(128)
    
    if b'comok' in r:
        print(r)
        status, unknown1, model, fwversion, mcucode, serialn, flashSize = r.split(b',')
        print('Status: ' + status.split(b' ')[0].decode("utf-8"))
        screentype=model.split(b' ')[0][0:10]
        print('Model: ' + screentype.decode("utf-8"))

def updatehmi():

    log("MAJ ECRAN HMI","red")
    print(screentype)
    print(porthmi)
    os.system ('python /opt/spotnik/spotnik2hmi_V2/nextion/nextion.py '+'/opt/spotnik/spotnik2hmi_V2/nextion/' +screentype.decode("utf-8") +'.tft '+ '/dev/'+porthmi)


def getspeednet():

    servers = []

    s = speedtest.Speedtest()

    downinfo=s.download()
    
    a=round(downinfo/1000000,2)
    ecrire("speednet.t0.txt",str(a))
    log(("Download: "+ str(a)+" Mbit/s"),"white")
    
    upinfo=s.upload()
    b=round(upinfo/1000000,2)
    ecrire("speednet.t1.txt",str(b))
    log(("Upload: " + str(b)+" Mbit/s"),"white")

    res = s.results.dict()
    info= res["client"]

    c =info["isp"]
    ecrire("speednet.t2.txt",str(c))
    log(("Fournisseur: " + str(c)),"white")

    d = info["ip"]
    ecrire("speednet.t3.txt",str(d))
    log(("Adresse IP: "+str(d)),"white")
    
    e = round(res["ping"],2)
    ecrire("speednet.t4.txt",str(e))
    log(("Ping: "+str(e) + " ms"),"white")

def resetHMI():
    global port
    log("Reset HMI ...","white")
    rstcmd=b'rest' + eof
    port.write(rstcmd)
     
#Fonction reglage dim du nextion
def setdim(dimv):
    log("dim debut","white")
    dimsend ="dim="+str(dimv)+eof
    port.write(b'dimsend')
    log("dim fin","white")

#Fonction info parametres Audio
#recuperation info niveau 
def GetAudioInfo(interfaceaudio):
    
    templevelOut = subprocess.check_output('amixer -c 0 get ' + interfaceaudio +" -M", shell=True)
    templevelOut =  str(templevelOut).split('[')
    levelOut=templevelOut[1][:-3]

    lIn= alsaaudio.Mixer(control='Mic')
    templevelIn=lIn.getvolume()
    levelIn=str(templevelIn).strip('[]')
    
    log("Lecture du niveau audio In Alsamixer: "+str(levelIn),"white")
    log("Lecture du niveau audio Out Alsamixer: "+str(levelOut),"white")

    ecrireval("hIn.val",str(levelIn))
    ecrireval("nIn.val",str(levelIn))
    #levelOutcor=round(int(levelOut)/1.240)
    ecrireval("hOut.val",str(levelOut))
    ecrireval("nOut.val",str(levelOut))


#Fonction reglage des niveaux    
def setAudio(interfaceaudio,levelOut,levelIn):
    lIn= alsaaudio.Mixer(control='Mic')
    levelOutcor = int(levelOut)*1
    os.system('amixer -c 0 set' + " Mic " + str(levelIn) + "%")
    log(("Reglage du niveau audio In: "+str(levelIn)+"%"),"white")
    log((">>>>>>>>>>>>>> INFO" + interfaceaudio),"white")
    os.system('amixer -c 0 set ' + interfaceaudio +" -M "+ str(levelOutcor) + "%")
    log(("Reglage du niveau audio Out: "+str(levelOut)+"%"),"white")

def requete(valeur):
    requetesend = str.encode(valeur)+eof
    port.write(requetesend)
    log(valeur,"blue")
    
#Fonction suivre le log svxlink
def follow(thefile):
    thefile.seek(0,2)      # Go to the end of the file
    while True:
         line = thefile.readline()
         if not line:
             time.sleep(0.1)    # Sleep briefly
             continue
         yield line

def hmiReadline():
    global port
    rcv = port.readline()
    myString = str(rcv)
    return myString

def checkversion():
        r =""
        r = requests.get('https://raw.githubusercontent.com/F8ASB/spotnik2hmi_V2/master/version')
        
        versions = r.text.replace("\n","").split(':')
        hmiversion = versions[1]
        log(hmiversion,"white")
        scriptversion = versions[3]
        log(scriptversion,"white")
        ecrire("maj.Txt_Vhmi.txt",hmiversion)
        ecrire("maj.Txt_Vscript.txt",scriptversion)        

def getCPUuse():

    CPU_Pct=str(round(float(os.popen('''grep 'cpu ' /proc/stat | awk '{usage=($2+$4)*100/($2+$4+$5)} END {print usage }' ''').readline()),2))
    print(("CPU Usage = " + CPU_Pct))
    return(CPU_Pct)

#Return information sur espace disque                     
# Index 0: total disk space                                                         
# Index 1: used disk space                                                          
# Index 2: remaining disk space                                                     
# Index 3: percentage of disk used                                                  
def getDiskSpace():
    p = os.popen("df -h /")
    i = 0
    while 1:
        i = i +1
        line = p.readline()
        if i==2:
            disk_space=(line.split()[4])
            return(disk_space[:-1]+" %")    

#Fonction de control d'extension au demarrage
def usage():
    program = os.path.basename(sys.argv[0])
    print("")   
    print("             "'\x1b[7;37;41m'"****ATTENTION****"+'\x1b[0m')
    print("")   
    print("Commande: python3 spotnik2hmi.py <port> <vitesse>")
    print("Ex: python3 spotnik2hmi.py ttyAMA0 9600")
    print("")
    sys.exit(1)

if len(sys.argv) > 2:
    log("Ok","white")
else:
    usage()

#Fonction envoyer un code DTMF au system
def dtmf(code):
    
    b = open("/tmp/svxlink_dtmf_ctrl_pty","w")
    b.write(code)
    log(("code DTMF: "+code),"white")
    b.close()

#Fonction envoyer le prenom selon le call
def prenom(Searchcall):

    callcut = Searchcall.split (" ")
    Searchprenom = callcut[1]
    print(Searchprenom)
    lines = csv.reader(open("amat_annuaire.csv","rb"),delimiter=";")

    for indicatif,nom,prenom,adresse,ville,cp in lines:
        if indicatif==Searchprenom:
            print(prenom)                   
#recuperation Frequence dans JSON

def get_gpio(port):
    global gpioptt
    global gpiosql

    svxconfig="/etc/spotnik/svxlink.cfg"
    config = configparser.RawConfigParser()
    config.read(svxconfig)
    
    if port=="sql":
        gpioptt = config.get('Tx1', 'PTT_PIN')
        log(gpioptt,"white")
        return(gpioptt)
    if port=="ptt":
        gpiosql = config.get('Rx1', 'GPIO_SQL_PIN')
        log(gpiosql,"white")
        return(gpiosql)

def get_frequency():
    global frequence
    
    with open(Json, 'r') as c:
        afind= json.load(c)
        frequence=afind['rx_qrg']
        return(frequence)
#recuperation indicatif dans Json       
def get_callsign():
    global indicatif
    with open(Json, 'r') as d:
        afind= json.load(d)
        call=afind['callsign']
        dept = afind['Departement']
        band = afind['band_type']
        indicatif = "("+dept+") "+call+" "+band
        return(indicatif)        

#Fonction envoyer des commande console
def console(cmd):
    p = Popen(cmd, shell=True, stdout=PIPE)
    out, err = p.communicate()
    return (p.returncode, out, err)

#Fonction Wifi ECRITURE
def wifi(wifiid,wifipass):
#        cfg = conf.ConfigParser()
        # cfg.read(conf)
        # cfg.set('connection', 'id', wifiid)
        # cfg.set('wifi', 'ssid', wifiid)
        # cfg.set('wifi-security', 'psk', wifipass)
        # cfg.write(open(conf,'w'))

        #lecture de donnees JSON
        with open(Json, 'r') as f:
            config = json.load(f)
        #editer la donnee
        config['wifi_ssid'] = wifiid
        config['wpa_key'] = wifipass
        #write it back to the file
        with open(Json, 'w') as f:
            json.dump(config, f)
#Fonction ecriture texte sur Nextion ex: ecrire(t0.txt,"hello word")
def ecrire(champ,texte):
    wcmd = str.encode(champ)+b'="'+str.encode(texte)+b'"'+ eof
    port.write(wcmd)
    infoserialtxt=champ+"=" +texte
    log(infoserialtxt,"blue")

def ecrireval(champ,valeur):
    wcmdval = str.encode(champ)+b'='+str.encode(valeur)+ eof
    port.write(wcmdval)
    infoserialval=champ+"=" +valeur
    log(infoserialval,"blue") 
    


#Fonction appel de page
def gopage(choixnompage):
    appelpage = b'page ' + str.encode(choixnompage)+eof
    port.write(appelpage)
    infoserialpage="page " +choixnompage
    log(infoserialpage,"yellow")

#Fonction recherche de nom de ville selon code ICAO
def getcity():
    #lecture valeur icao dans config.json       
        with open(Json, 'r') as b:
            afind= json.load(b)
            airport =afind['airport_code']
            #lecture ville dans fichier icao.cfg        
            icao2city = configparser.RawConfigParser()
            config.read(icao)
            Result_city = config.get('icao2city', airport)
            print (Result_city)
            #city= '"'+Result_city+'"'
            ecrire("meteo.t0.txt",str(Result_city)) 
            print("Aeroport de: " +Result_city) 

#Fonction Meteo Lecture des donnees Metar + envoi Nextion
def get_meteo():
    #recherche code IMAO dans config.json
    with open(Json, 'r') as b:
        afind= json.load(b)
        airport =afind['airport_code']
        #Info ville Aéroport
        log(("Le code ICAO est: "+airport),"white")
        getcity()
        fichier = open("/tmp/meteo.txt", "w")
        fichier.write("[rapport]")
        fichier.close()
        result = console('/opt/spotnik/spotnik2hmi_V2/python-metar/get_report.py '+ airport+ '>> /tmp/meteo.txt')
        log(str(result),"white")
        #routine ouverture fichier de config
        config = configparser.RawConfigParser()
        config.read('/tmp/meteo.txt')
        #recuperation indicatif et frequence
        pression = config.get('rapport', 'pressure')
        temperature = config.get('rapport', 'temperature')
        rose = config.get('rapport', 'dew point')
        buletin = config.get('rapport', 'time')
        buletin = config.get('rapport', 'time')
        heure = buletin.split(':')
        heure = heure[0][-2:] + ":"+heure[1]+ ":"+heure[2][:2]
        log((pression[:-2]),"white")
        log(rose,"white")
        log(temperature,"white")
        ecrire("meteo.t1.txt",str(temperature))
        ecrire("meteo.t3.txt",str(heure))
        ecrire("meteo.t4.txt",str(rose))
        Pression = pression[:-2]+'hPa'
        ecrire("meteo.t2.txt",str(Pression))

def logo(Current_version):
    print(" ")
    print('\x1b[7;30;43m'+"                                           .-''-.                                " +'\x1b[0m')                                   
    print('\x1b[7;30;43m'+"                                         .' .-.  )  " +'\x1b[0m')
    print('\x1b[7;30;43m'+"                                        / .'  / /" +'\x1b[0m')
    print('\x1b[7;30;47m'+"  ____  ____   ___ _____ _   _ ___ _  _" +'\x1b[7;30;43m'+"(_/   / /"+'\x1b[7;30;47m'+"      _   _ __  __ ___ " +'\x1b[0m')
    print('\x1b[7;30;47m'+" / ___||  _ \ / _ \_   _| \ | |_ _| |/ / " +'\x1b[7;30;43m'+"   / /     "+'\x1b[7;30;47m'+" | | | |  \/  |_ _|" +'\x1b[0m')
    print('\x1b[7;30;47m'+" \___ \| |_) | | | || | |  \| || || ' /  " +'\x1b[7;30;43m'+"  / /  "+'\x1b[7;30;47m'+"     | |_| | |\/| || | " +'\x1b[0m')
    print('\x1b[7;30;47m'+"  ___) |  __/| |_| || | | |\  || || . \ " +'\x1b[7;30;43m'+"  . '       "+'\x1b[7;30;47m'+" |  _  | |  | || | " +'\x1b[0m')
    print('\x1b[7;30;47m'+" |____/|_|    \___/ |_| |_| \_|___|_|\_\ " +'\x1b[7;30;43m'+"/ /    _.-')"+'\x1b[7;30;47m'+"|_| |_|_|  |_|___|" +'\x1b[0m')
    print('\x1b[7;30;43m'+"                                       .' '  _.'.-'' " +'\x1b[0m')
    print('\x1b[7;30;43m'+"                                      /  /.-'_.'          Version:" + d.versionDash +'\x1b[0m')                
    print('\x1b[7;30;43m'+"                                     /    _.'  TEAM:"+ '\x1b[0m' +'\x1b[3;37;44m' + "/F0DEI"+ '\x1b[0m' +'\x1b[6;30;47m' + "/F5SWB"+ '\x1b[0m' + '\x1b[6;37;41m' + "/F8ASB"+ '\x1b[0m')               
    print('\x1b[7;30;43m'+"                                    ( _.-'              " +'\x1b[0m')             
    
