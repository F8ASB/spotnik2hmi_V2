#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import  *
#pour lecture fichier de config
import ConfigParser, os
from fonctions import *

#Variables
eof = "\xff\xff\xff"
today = datetime.now()

versionDash = "2.10"
wifistatut = 0
dashlist = ""
monitor = ""

#Reglage de luminosite
#rdim = 10 #ecran sans reception signal
#txdim = 80 # ecran avec reception station

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

#liste des salons

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
    }
}

search_start = ''
search_stop = ''
timestamp = ''

MOVE_MAX = 5


