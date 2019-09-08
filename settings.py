#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import  *
#pour lecture fichier de config
import configparser, os
from fonctions import *

#Variables
eof = "\xff\xff\xff"
today = datetime.now()
versionDash = "2.4"
wifistatut = 0
dashlist = ""
monitor = ""
qsystatut=False
salon_current=""
dateold=""
heureSold=""
statutradio=""
firstboot= True
rpi3bplus=False
DEBUG = False

#Chemins fichiers
svxconfig="/etc/spotnik/svxlink.cfg"
cheminversion= open("/etc/spotnik/version", "r")
version = cheminversion.read()
version = version.strip()
confwifi="/etc/NetworkManager/system-connections/SPOTNIK"

#Chemin log a suivre
svxlogfile = "/tmp/svxlink.log"   #SVXLink log file 

#routine ouverture fichier de config
config = configparser.RawConfigParser()
config.read(svxconfig)

#recuperation indicatif et frequence    
callsign = get_callsign()
freq = get_frequency()

#Info pour fichier wifi rpiB+
pathwpasupplicant="/etc/wpa_supplicant/"

header1="ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev"
header2="update_config=1"
header3="network={"
header6="    key_mgmt=WPA-PSK"
header7="}"


#*******************************
#* liste des salons + variable *
#*******************************

salon = {
    'RRF': {
        'url': 'http://rrf.f5nlg.ovh/api/svxlink/RRF', 
        'transmit': True, 
        'call_current': '', 
        'call_previous': '',
        'node_list': '',
        'node_list_old': '',
        'node_list_in': '',
        'node_count': '',
        'node_list_out': ''
    },

    'BAV': {
        'url': 'http://rrf.f5nlg.ovh/api/svxlink/bavardage', 
        'transmit': True, 
        'call_current': '', 
        'call_previous': '',
        'node_list': '',
        'node_list_old': '',
        'node_list_in': '',
        'node_count': '',
        'node_list_out': ''
    },

    'TEC': {
        'url': 'http://rrf.f5nlg.ovh/api/svxlink/technique', 
        'transmit': True, 
        'call_current': '', 
        'call_previous': '',
        'node_list': '',
        'node_list_old': '',
        'node_list_in': '',
        'node_count': '',
        'node_list_out': ''
    },

    'INT': {
        'url': 'http://rrf.f5nlg.ovh/api/svxlink/international', 
        'transmit': True, 
        'call_current': '', 
        'call_previous': '',
        'node_list': '',
        'node_list_old': '',
        'node_list_in': '',
        'node_count': '',
        'node_list_out': ''
    },

    'LOC': {
        'url': 'http://rrf.f5nlg.ovh/api/svxlink/local', 
        'transmit': True, 
        'call_current': '', 
        'call_previous': '',
        'node_list': '',
        'node_list_old': '',
        'node_list_in': '',
        'node_count': '',
        'node_list_out': ''
    },

    'FON': {
#        #'url': 'http://fon.f1tzo.com:8080/api/svxlink/testFON',
        'url': 'http://rrf.f5nlg.ovh/api/svxlink/FON', 
        'transmit': True, 
        'call_current': '', 
        'call_previous': '',
        'node_list': '',
        'node_list_old': '',
        'node_list_in': '',
        'node_count': '',
        'node_list_out': ''
    }
}

search_start = ''
search_stop = ''
timestamp = ''

MOVE_MAX = 5


