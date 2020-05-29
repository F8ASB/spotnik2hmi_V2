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
#                                 TEAM: F0DEI,F5SWB,F8ASB,F4ICR            #    
############################################################################

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
from subprocess import Popen, PIPE
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
import re

DEBUG=False

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

#************************
#* NOM DE L'APPLICATION *
#************************
def set_procname(newname):
    from ctypes import cdll, byref, create_string_buffer
    libc = cdll.LoadLibrary('libc.so.6')    #Loading a 3rd party library C
    buff = create_string_buffer(len(newname)+1) #Note: One larger than the name (man prctl says that)
    buff.value = newname.encode('utf-8')                 #Null terminated string as it should be
    libc.prctl(15, byref(buff), 0, 0, 0) #Refer to "#define" of "/usr/include/linux/prctl.h" for the misterious value 16 & arg[3..5] are zero as the man page says.

#***************
#* GESTION LOG *
#***************

def debugON():
    global DEBUG
    DEBUG=True

#Fonction Debug
def log(s,color):
    if DEBUG:
        if color=="red":
            print ('\x1b[47;1;31m'+"DEBUG: "+s+'\x1b[0m')
        if color=="blue":
            print ('\x1b[47;1;34m'+"DEBUG: "+s+'\x1b[0m')
        if color=="yellow":
            print ('\x1b[7;30;43m'+"DEBUG: "+s+'\x1b[0m')
        if color=="white":
            print ('\x1b[7;30;47m'+"DEBUG: "+s+'\x1b[0m')
        if color=="none":
            print (s)   
def logct():
    sock = socket.socket(socket.AF_INET, 
    socket.SOCK_DGRAM)
    #29-05-2020;10:11:00;F8ASB;3.00;3.60;Raspberry Pi
    MESSAGE=str(d.today.strftime('%d-%m-%Y'))+";"+str((d.today.strftime('%H:%M:%S')))+";"+str(d.callsign)+";"+str(d.version)+";"+str(d.versionDash)+";"+str(d.board)
    sock.sendto(bytes(MESSAGE, "utf-8"), ("51.38.115.164",9254 ))
    log(MESSAGE,"white")

#***************
#* GESTION COM *
#***************

def portcom(portseriel,vitesse):
    global port
    global screentype
    global porthmi
    
    porthmi=portseriel

    port=serial.Serial(port='/dev/'+portseriel,baudrate=vitesse,timeout=1, writeTimeout=1)
    log("Port serie: " +portseriel+" Vitesse: "+vitesse,"white")

    cmdinfo= eof + b'connect' + eof 
    port.write(cmdinfo)

    r = port.read(128)
    
    if b'comok' in r:
        log(r,"white")
        status, unknown1, model, fwversion, mcucode, serialn, flashSize = r.split(b',')
        log('Status: ' + status.split(b' ')[0].decode("utf-8"),"white")
        screentype=model.split(b' ')[0][0:10]
        log('Model: ' + screentype.decode("utf-8"),"white")
        print(screentype.decode("utf-8"))
    else:
        print('\x1b[7;37;41m'+"VOTRE ECRAN N'EST PAS ACCESSIBLE, MERCI DE VERIFIER VOTRE CABLAGE !"+'\x1b[0m')
        sys.exit()

#*************************
#* GESTION ECRAN NEXTION *
#*************************

def resetHMI():
    global port
    log("Reset HMI ...","white")
    rstcmd=b'rest' + eof
    port.write(rstcmd)

def updatehmi():

    log("MAJ ECRAN HMI","red")
  #  log(str(screentype),"white")
  #  log(str(porthmi),"white")
    os.system ('python /opt/spotnik/spotnik2hmi_V2/nextion/nextion.py '+'/opt/spotnik/spotnik2hmi_V2/nextion/NX4832K035.tft '+ '/dev/'+porthmi)

def setdim(dimv):
    log("dim debut","white")
    dimsend ="dim="+str(dimv)+eof
    port.write(b'dimsend')
    log("dim fin","white")

def hmiReadline():
    global port
    rcv = port.readline()
    myString = str(rcv)
    return myString

#Fonction ecriture texte sur Nextion ex: ecrire(t0.txt,"hello word")
def ecrire(champ,texte):
    wcmd = str.encode(champ)+b'="'+str.encode(texte)+b'"'+ eof
    port.write(wcmd)
    infoserialtxt=champ+"=" +texte
    log(infoserialtxt,"blue")
#Fonction ecriture valeur sur ecran
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

#Gestion des statuts en TX des salon
def envoistatut():

    if d.salon["RRF"]['transmit'] is True:
        rrfstatut = 1                    
    else:
        rrfstatut = 0
    if d.salon["BAV"]['transmit'] is True:
        bavstatut = 1                    
    else:
        bavstatut = 0
    if d.salon["TEC"]['transmit'] is True:
        tecstatut = 1                    
    else:
        tecstatut = 0
    if d.salon["INT"]['transmit'] is True:
        intstatut = 1                    
    else:
        intstatut = 0
    if d.salon["LOC"]['transmit'] is True:
        locstatut = 1                    
    else:
        locstatut = 0
    if d.salon["FON"]['transmit'] is True:
        fonstatut = 1                    
    else:
        fonstatut = 0
    
    #Genere un trame de 6 0 ou 1 selon etat
    #l'ordre RRF/BAVARDAGE/TECHNIQUE/INTERNATIONNAL/LOCAL/FON
    # 000000   => aucun trafic
    # 100000   => trafic sur salon RRF

    ecrire("trafic.Vtxt_status.txt",(str(rrfstatut)+str(bavstatut)+str(tecstatut)+str(intstatut)+str(locstatut)+str(fonstatut)))

#*************************
#* GESTION TEST INTERNET *
#*************************

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

#*************************
#*  TEST INTERNET DISPO  *
#*************************

def is_connected():
    
    #heureError= '"'+d.heureS+'"'
    try:
        # connect to the host -- tells us if the host is actually
        # reachable
        socket.create_connection(("www.google.com", 80))
        log("INTERNET PRESENT PROBLEME SERVEUR "+d.key,"white")

        if d.key == d.salon_current and d.alerte == 0:
            ecrire("alerte.Txt_alerte.txt","Probleme sur serveur: "+str(d.key))
            ecrire("alerte.T_alerte.txt",d.heureS)
            gopage("alerte")
            d.alerte=1
        
    except OSError:
        log("COUPURE INTERNET: "+str(d.heureS),"white")
        if d.key == d.salon_current and d.alerte == 0:
            ecrire("alerte.Txt_alerte.txt","Coupure Internet")
            ecrire("alerte.T_alerte.txt",d.heureS)
            gopage("alerte")
            d.alerte=1
            pass


#***************************
#* GESTION PARAMETRE AUDIO *
#***************************
 
def GetAudioInfoOut(interfaceaudioOUT):
     
    templevelOut = subprocess.check_output('amixer -c 0 get ' + interfaceaudioOUT +" -M", shell=True)
    templevelOut =  str(templevelOut).split('[')
    levelOut=templevelOut[1][:-3]
    #ecrireval("boot.Vtxt_nOut.val",str(levelOut))
    ecrireval("mixer.V_mout.val",str(levelOut))
    log("Lecture du niveau audio Out Alsamixer: "+str(levelOut),"white")

def GetAudioInfoIn(interfaceaudioIN):
    if interfaceaudioIN =="Capture":
        templevelIn = subprocess.check_output('amixer -c 0 get ' + interfaceaudioIN +" -M", shell=True)
        templevelIn =  str(templevelIn).split('[')  
        levelIn=templevelIn[1][:-3]
    else:
        templevelIn = subprocess.check_output('amixer -c 0 get ' + interfaceaudioIN +" -M", shell=True)
        templevelIn =  str(templevelIn).split('[')
        levelIn=templevelIn[1][:-3]  

    #ecrireval("boot.Vtxt_nIn.val",str(levelIn))
    ecrireval("mixer.V_min.val",str(levelIn))
    log("Lecture du niveau audio In Alsamixer: "+str(levelIn),"white")
    

#Fonction reglage des niveaux IN  
def setAudioIn(interfaceaudio,levelIn):
    
    log((">>>>>>>>>>>>>> INFO " + interfaceaudio),"white")
    os.system('amixer -c 0 set ' + interfaceaudio +" -M " + str(levelIn) + "%")
    log(("Reglage du niveau audio In: "+str(levelIn)+"%"),"white")
    ecrireval("mixer.Vnb_mixer.val","1")

    if d.soundcard == "WM8960":

        os.system('alsactl --file=/etc/voicecard/wm8960_asound.state store')
        
        #file=open(d.soundsh,"r")
        #lines = file.readlines()
        #file.close()
        #lines [2] = "amixer -c 0 set 'Capture' -M "+ str(levelIn) + "%\n"
        #file=open(d.soundsh,"w")
        #file.writelines(lines)
        #file.close()
    

#Fonction reglage des niveaux OUT    
def setAudioOut(interfaceaudio,levelOut):
    
    levelOutcor = int(levelOut)*1
    log((">>>>>>>>>>>>>> INFO " + interfaceaudio),"white")
    os.system('amixer -c 0 set ' + interfaceaudio +" -M "+ str(levelOutcor) + "%")
    log(("Reglage du niveau audio Out: "+str(levelOut)+"%"),"white")
    ecrireval("mixer.Vnb_mixer.val","1")
   
    if d.soundcard == "WM8960":
        
        os.system('alsactl --file=/etc/voicecard/wm8960_asound.state store')

        #file=open(d.soundsh,"r")
        #lines = file.readlines()
        #file.close()
        #lines [1] = "amixer -c 0 set 'Headphone' -M "+ str(levelOut) +"%\n"
        #file=open(d.soundsh,"w")
        #file.writelines(lines)
        #file.close()

def requete(valeur):
    requetesend = str.encode(valeur)+eof
    port.write(requetesend)
    log(valeur,"blue")

#****************************
#* REQUETE VERSION SOFTWARE *
#****************************

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

#**************************
#* REQUETE INFOS SYSTEMES *
#**************************

def getCPUuse():

    CPU_Pct=str(round(float(os.popen('''grep 'cpu ' /proc/stat | awk '{usage=($2+$4)*100/($2+$4+$5)} END {print usage }' ''').readline()),2))
    log(("CPU Usage = " + CPU_Pct),"white")
    return(CPU_Pct)
                                                 
def getDiskSpace():
    p = os.popen("df -h /")
    i = 0
    while 1:
        i = i +1
        line = p.readline()
        if i==2:
            disk_space=(line.split()[4])
            return(disk_space[:-1]+" %") 

#********************* 
#* GESTION DEMARRAGE *
#*********************  

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
#recuperation GPIO en fonction

def get_gpioptt():
    global gpioptt
   
    svxconfig="/etc/spotnik/svxlink.cfg"
    config = configparser.RawConfigParser()
    config.read(svxconfig)

    gpioptt = config.get('Tx1', 'PTT_PIN')
    log(gpioptt,"white")
    return(gpioptt)

def get_gpiosql():
    global gpiosql
   
    svxconfig="/etc/spotnik/svxlink.cfg"
    config = configparser.RawConfigParser()
    config.read(svxconfig)

    gpiosql = config.get('Rx1', 'GPIO_SQL_PIN')
    log(gpiosql,"white")
    return(gpiosql)

#recuperation frequence dans Json
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

#regarde la version Raspberry
def getrevision():

  # Extract board revision from cpuinfo file
    myrevision = "0000"
    try:
        f = open('/proc/cpuinfo','r')
        for line in f:
            if line[0:8]=='Revision':
                length=len(line)
                myrevision = line[11:length-1]
        f.close()
    except:
        myrevision = "0000"

    return myrevision 

#Logo de demarrage

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



#***********************
# GESTION MAJ DATABASE *
#***********************

def datacheckversion():
#lecture de la version sur le web disponible
        v =""
        v = requests.get('https://raw.githubusercontent.com/F4ICR/datas/master/database_version')

        infodataversion = v.text.replace("\n","").split(':')
        database_version = infodataversion[1]
        print("La version Database disponible est: "+database_version)
#lecture de la version actuel
        dbactuel = open("/opt/spotnik/spotnik2hmi_V2/datas/database_version", "r")
        db= dbactuel.read()
        dbactuel.close
        dataversionactuel = db.replace("\n","").split(':')
        print("La version Database actuelle est: " +dataversionactuel[1])

        if infodataversion[1] != dataversionactuel[1] :
            majdb()
            d.database=infodataversion[1]
        else:
            print("DATABASE A JOUR")
            d.database=infodataversion[1]

def majdb():
       print("*** DATABASE NON ACTUALISE ***")
       print("SUPPRESSION DES ANCIENS FICHIERS...")
       os.system('rm /opt/spotnik/spotnik2hmi_V2/datas/database_version')
       os.system('rm /opt/spotnik/spotnik2hmi_V2/datas/cache_amat_FR.dat')
       os.system('rm /opt/spotnik/spotnik2hmi_V2/datas/amat_FR.dat')
       os.system('rm /opt/spotnik/spotnik2hmi_V2/datas/icao.cfg') 
       print("TELECHARGEMENT en cours...")
       os.system('wget -P /opt/spotnik/spotnik2hmi_V2/datas/ https://raw.githubusercontent.com/F4ICR/datas/master/database_version')
       os.system('wget -P /opt/spotnik/spotnik2hmi_V2/datas/ https://raw.githubusercontent.com/F4ICR/datas/master/cache_amat_FR.dat')
       os.system('wget -P /opt/spotnik/spotnik2hmi_V2/datas/ https://raw.githubusercontent.com/F4ICR/datas/master/amat_FR.dat')
       os.system('wget -P /opt/spotnik/spotnik2hmi_V2/datas/ https://raw.githubusercontent.com/F4ICR/datas/master/icao.cfg')


#********************** 
#* GESTION ENVOI DTMF *
#**********************  

def dtmf(code):
    print(d.version)
    if d.version =="2.0":
        b = open("/tmp/svxlink_dtmf_ctrl_pty","w")
    else:
        b = open("/tmp/dtmf_uhf","w")

    b.write(code)
    log(("code DTMF: "+code),"white")
    b.close()

#***************************
#*  RECHERCHE INFOS OM FR  *
#***************************

def Infocall(Searchcall):

    #Verificaion du format de l'indicatif
    pattern = '\(([^)]+)\) ([^)]+) (H|V|U|R|T10M|T6M|T|10M|6M)'

    check = re.match(pattern, Searchcall)

    if check:
        log(('Indicatif valide :' + '--->' + check.groups()[1]),"white")
        ckcall=check.groups()[1]
        recherche_call(ckcall,d.cache_amat_data)

    else:
        log(('Indicatif invalide: '+Searchcall),"white")
        ecrireval("trafic.Vnb_info.val","0")
    #Ecriture dans fichier novalid
        fichiernovalid = open('/opt/spotnik/spotnik2hmi_V2/datas/novalid.dat', "a")
        lignenovalid=Searchcall
        fichiernovalid.write(lignenovalid+'\n')
        fichiernovalid.close()

def recherche_call(callachercher,database):
    if database == d.cache_amat_data and os.path.isfile(d.cache_amat_data)==True:
        
        log('Recherche dans liste call en cache',"white")
        log(database,"white")
    else:
        log('Recherche dans liste call complete',"white")
        log(database,"white")
        if os.path.isfile(d.cache_amat_data)==False:
            fichiercache = open(d.cache_amat_data, "w")
            fichiercache.close()

    with open(database) as csvfile:
        readCSV = csv.reader(csvfile, delimiter=';')
        indicatifs = []
        noms = []
        prenoms = []
        typeaccess = []
        villes = []
        codes = []
        payss = []

        for row in readCSV:
            indicatif = row[0]
            nom = row[1]
            prenom = row[2]
            typeacces = row[3]
            ville = row[4]
            code = row[5]
            pays = row[6]

            indicatifs.append(indicatif)
            noms.append(nom)
            prenoms.append(prenom)
            typeaccess.append(typeacces)
            villes.append(ville)
            codes.append(code)
            payss.append(pays)

    try:
        recherchecall = indicatifs.index(callachercher)
        
        log(('Database position: '+str(recherchecall)),"white")
           
        theprenom = prenoms[recherchecall]
        thenom = noms[recherchecall]
        thetypeacces = typeaccess[recherchecall]
        thecode = codes[recherchecall]
        theville = villes[recherchecall]
        thepays = payss[recherchecall]

        log(("Indicatif: "+callachercher),"white")
        log(('Nom: '+thenom),"white")
        log(('Prenom: '+theprenom),"white")
        log(('Type acces: '+thetypeacces),"white")
        log(('CP: '+thecode),"white")
        log(('Ville: '+theville),"white")
        log(('pays: '+thepays),"white")

        ecrire("infostation.Txt_callinfo.txt",str(callachercher))
        ecrire("infostation.Txt_prenom.txt",str(theprenom))
        ecrire("infostation.Txt_code.txt",str(thecode))
        ecrire("infostation.Txt_ville.txt",str(theville))
        ecrireval("infostation.Vnb_info.val",str(thetypeacces))
        ecrire("infostation.Txt_pays.txt",str(thepays))

        ecrireval("trafic.Vnb_info.val","1")

        if database == d.full_amat_data:
            fichiercache = open(d.cache_amat_data, "a")
            ligneaecrire=callachercher+";"+thenom+";"+theprenom+";"+thetypeacces+";"+theville+";"+thecode+";"+thepays
            fichiercache.write(ligneaecrire+'\n')
            fichiercache.close()

    except:

        if database == d.cache_amat_data:
            
            recherche_call(callachercher,d.full_amat_data)
            
        else:
            log('Indicatif inconnu',"white")
            #Ecriture dans fichier inconnu
            fichierunknow = open('/opt/spotnik/spotnik2hmi_V2/datas/unknow.dat', "a")
            fichierunknow.write(callachercher+'\n')
            fichierunknow.close()
            ecrireval("trafic.Vnb_info.val","0")
    

#***************************
#*  ENVOI COMMANDE SHELL   *
#***************************

#Fonction envoyer des commande console
def console(cmd):
    p = Popen(cmd, shell=True, stdout=PIPE)
    out, err = p.communicate()
    return (p.returncode, out, err)

#**************** 
#* GESTION WIFI *
#****************

#Fonction Wifi ECRITURE
def wifi(wifiid,wifipass):
    #ecriture fichier /etc/NetworkManager/system-connections/SPOTNIK
    confwifi="/etc/NetworkManager/system-connections/SPOTNIK"

    log("Ecriture fichier SPOTNIK + fichier Gui","yellow")
    cfg = configparser.ConfigParser()
    cfg.read(confwifi)
    cfg.set('connection', 'id', wifiid)
    cfg.set('wifi', 'ssid', wifiid)
    cfg.set('wifi-security', 'psk', wifipass)
    cfg.write(open(confwifi,'w'))

    #lecture de donnees JSON
    with open(Json, 'r') as f:
        config = json.load(f)
    config['wifi_ssid'] = wifiid
    config['wpa_key'] = wifipass
    #ecriture de donnees JSON
    with open(Json, 'w') as f:
        json.dump(config, f)
 
#Fonction ecriture wifi RPI3B+
def wifi3bplus(ssid,password):
    pathwpasupplicant="/etc/wpa_supplicant/"
    log("Ecriture fichier wpa_supplicant.conf + fichier Gui","yellow")

    #lecture de donnees JSON
    with open(Json, 'r') as f:
        config = json.load(f)
    config['wifi_ssid'] = ssid
    config['wpa_key'] = password
    #ecriture de donnees JSON
    with open(Json, 'w') as f:
        json.dump(config, f)    

    header4='    ssid="'+ssid+'"'
    header5='    psk="'+password+'"'

#Sauvegarde de wpa_supplicant.conf existant et renommage en wpa_supplicant.conf.old
    os.rename(pathwpasupplicant+'wpa_supplicant.conf', pathwpasupplicant+'wpa_supplicant.conf.old')
#creation d'un nouveau fichier wpa_supplicant.conf.new
    fichier = open(pathwpasupplicant+"wpa_supplicant.conf.new", "a")
    lines="%s \n %s \n %s \n %s \n %s \n %s \n %s \n" % (d.header1, d.header2, d.header3, header4, header5, d.header6, d.header7)
    fichier.write(lines)
    fichier.close()
#renommage du ficher wpa_supplicant.conf.new en wpa_supplicant.conf
    os.rename(d.pathwpasupplicant+'wpa_supplicant.conf.new', pathwpasupplicant+'wpa_supplicant.conf')

#*****************************
#* DETECTION CONNEXION SALON *
#*****************************
def voirsalon():

    a = open("/etc/spotnik/network","r")
    tn = a.read()


    if tn.find("rrf") != -1 and d.salon_current!="RRF":
        ecrire("monitor.Vtxt_saloncon.txt","RESEAU RRF")
        d.salon_current="RRF"
        d.API=True
        ecrire("trafic.g0.txt","")
        if d.qsystatut==False and d.firstboot==False:
            gopage("qsy")
        d.qsystatut=False
        
    if tn.find("fon") != -1 and d.salon_current!="FON":
        ecrire("monitor.Vtxt_saloncon.txt","RESEAU FON")    
        d.salon_current="FON"
        d.API=True
        ecrire("trafic.g0.txt","")
        if d.qsystatut==False and d.firstboot==False:
            gopage("qsy")
        d.qsystatut=False
    
    if tn.find("tec") != -1 and d.salon_current!="TEC":
        ecrire("monitor.Vtxt_saloncon.txt","SALON TECHNIQUE")
        d.salon_current="TEC"
        d.API=True
        ecrire("trafic.g0.txt","")
        if d.qsystatut==False and d.firstboot==False:
            gopage("qsy")
        d.qsystatut=False

    if tn.find("int") != -1 and d.salon_current!="INT":
        ecrire("monitor.Vtxt_saloncon.txt","SALON INTER.")
        d.salon_current="INT"
        d.API=True
        ecrire("trafic.g0.txt","")
        if d.qsystatut==False and d.firstboot==False:
            gopage("qsy")
        d.qsystatut=False

    if tn.find("bav") != -1 and d.salon_current!="BAV":
        ecrire("monitor.Vtxt_saloncon.txt","SALON BAVARDAGE")    
        d.salon_current="BAV"
        d.API=True
        ecrire("trafic.g0.txt","")
        if d.qsystatut==False and d.firstboot==False:
            gopage("qsy")
        d.qsystatut=False

    if tn.find("loc") != -1 and d.salon_current!="LOC":
        ecrire("monitor.Vtxt_saloncon.txt","SALON LOCAL")    
        d.salon_current="LOC"
        d.API=True
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
        d.API=True
        if d.qsystatut==False and d.firstboot==False:
            gopage("qsy")
        d.qsystatut=False   

    if tn.find("exp") != -1 and d.salon_current!="EXP":
        ecrire("monitor.Vtxt_saloncon.txt","SALON EXP.")
        ecrire("trafic.g0.txt","") 
        d.salon_current="EXP"
        d.API=True
        if d.qsystatut==False and d.firstboot==False:
            gopage("qsy")
        d.qsystatut=False   

    if tn.find("fdv") != -1 and d.salon_current!="EXP":
        ecrire("monitor.Vtxt_saloncon.txt","SALON EXP. DV")
        ecrire("trafic.g0.txt","") 
        d.salon_current="EXP"
        d.API=True
        if d.qsystatut==False and d.firstboot==False:
            gopage("qsy")
        d.qsystatut=False   

    if tn.find("reg") != -1 and d.salon_current!="REG":
        ecrire("monitor.Vtxt_saloncon.txt","SALON REGIONAL")
        ecrire("trafic.g0.txt","") 
        d.salon_current="REG"
        d.API=False
        if d.qsystatut==False and d.firstboot==False:
            gopage("qsy")
        d.qsystatut=False 
        d.region=False

    if tn.find("est") != -1 and d.salon_current!="REG":
        ecrire("monitor.Vtxt_saloncon.txt","SALON REGIONAL")
        ecrire("trafic.g0.txt","") 
        d.salon_current="REG"
        if d.qsystatut==False and d.firstboot==False:
            gopage("qsy")
        d.qsystatut=False 
        d.API=True  

    if tn.find("el") != -1 and d.salon_current!="ECH":
        ecrire("monitor.Vtxt_saloncon.txt","ECHOLINK")
        ecrire("trafic.g0.txt","")
        d.API=True 
        d.salon_current="ECH"
        if d.qsystatut==False and d.firstboot==False:
            gopage("qsy")
        d.qsystatut=False


#***********************************
#*Gestion salon Perroquet TX et RX *
#***********************************

    if tn.find("default") != -1 and d.salon_current=="PER":
        
        p= open("/sys/class/gpio/"+d.nbgpiosql+"/value","r")
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

        q= open("/sys/class/gpio/"+d.nbgpioptt+"/value","r")
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

#*************************
#*  INFO SALON AU REVEIL *
#********************

def diresalon():
    
    if d.salon_current=="RRF":
        ecrire("monitor.Vtxt_saloncon.txt","RESEAU RRF")
    if d.salon_current=="FON":
        ecrire("monitor.Vtxt_saloncon.txt","RESEAU FON")  
    if d.salon_current=="TEC":
        ecrire("monitor.Vtxt_saloncon.txt","SALON TECHNIQUE")  
    if d.salon_current=="INT":
        ecrire("monitor.Vtxt_saloncon.txt","SALON INTER.")
    if d.salon_current=="BAV":
        ecrire("monitor.Vtxt_saloncon.txt","SALON BAVARDAGE")
    if d.salon_current=="LOC":
        ecrire("monitor.Vtxt_saloncon.txt","SALON LOCAL") 
    if d.salon_current=="PER":
        ecrire("monitor.Vtxt_saloncon.txt","PERROQUET")
    if d.salon_current=="EXP":
        ecrire("monitor.Vtxt_saloncon.txt","SALON EXP.") 
    if d.salon_current=="EXP":
        ecrire("monitor.Vtxt_saloncon.txt","SALON EXP. DV")
    if d.salon_current=="REG":
        ecrire("monitor.Vtxt_saloncon.txt","SALON REGIONAL") 
    if d.salon_current=="REG":
        ecrire("monitor.Vtxt_saloncon.txt","SALON REGIONAL") 
    if d.salon_current=="REG":
        ecrire("monitor.Vtxt_saloncon.txt","SALON REGIONAL")
    if d.salon_current=="ECH":
        ecrire("monitor.Vtxt_saloncon.txt","ECHOLINK")
    
#********************
#*  RECHERCHE METEO *
#********************

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
    if d.noerror:
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
            control_meteo()

#Suite à des manques de datas Metar, je teste si le fichier meteo.txt est conforme
def control_meteo():
        if d.noerror:
            m = open("/tmp/meteo.txt","r")
            meteofile= m.read()
            if meteofile.find("Unparsed groups in body") != -1:
                log("Error fichier Meteo","white")
            else:
                read_meteo()

#Lecture des datas meteo
def read_meteo():    
        if d.noerror:
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
            log((rose[:-2]+" °C"),"white")
            log((temperature[:-2]+" °C"),"white")
            ecrire("meteo.t1.txt",str(temperature[:-2]))
            ecrire("meteo.t3.txt",str(heure))
            ecrire("meteo.t4.txt",str(rose[:-2]))
            Pression = pression[:-2]+'hPa'
            ecrire("meteo.t2.txt",str(Pression))

#*********************
#* TEST RAPTOR ACTIF *
#*********************

def raptortest():
    raptor_status = os.popen( 'pgrep -f -c \'python /opt/RRFRaptor/RRFRaptor.py\'' ).read()
    #Decommenter ci-dessous si utilisation python 3, et comment ligne ci-dessus 
    #raptor_status = os.popen( 'pgrep -f -c \'python /opt/RRFRaptor/RRFRaptor.py\'' ).read()
    raptor_status = raptor_status.strip()
    if raptor_status == '2':
        ecrireval("scan.Vnb_rapstate.val","1")
        log("Raptor ON","white")
    else:
        ecrireval("scan.Vnb_rapstate.val","0")
        log("Raptor OFF","white")


