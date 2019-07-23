
#Sauvegarde des fichiers existants
mv /opt/spotnik/spotnik2hmi_V2/fonctions.py /opt/spotnik/spotnik2hmi_V2/old_version/fonctions`date +%d%m%Y`.py
mv /opt/spotnik/spotnik2hmi_V2/spotnik2hmi.py /opt/spotnik/spotnik2hmi_V2/old_version/spotnik2hmi`date +%d%m%Y`.py
mv /opt/spotnik/spotnik2hmi_V2/spotnik2hmi.py /opt/spotnik/spotnik2hmi_V2/old_version/settings`date +%d%m%Y`.py
mv /opt/spotnik/spotnik2hmi_V2/install.sh /opt/spotnik/spotnik2hmi_v2/old_version/install`date +%d%m%Y`.sh

#Telechargement script
wget https://raw.githubusercontent.com/F8ASB/spotnik2hmi_V2/master/fonctions.py -O /opt/spotnik/spotnik2hmi_V2/
wget https://raw.githubusercontent.com/F8ASB/spotnik2hmi_V2/master/spotnik2hmi.py -O /opt/spotnik/spotnik2hmi_V2/
wget https://raw.githubusercontent.com/F8ASB/spotnik2hmi_V2/master/install.sh -O /opt/spotnik/spotnik2hmi_V2/
wget https://raw.githubusercontent.com/F8ASB/spotnik2hmi_V2/master/settings.py -O /opt/spotnik/spotnik2hmi_V2/

#Telechargement HMI
wget https://github.com/F8ASB/spotnik2hmi_V2/blob/master/nextion/NX4832K035.tft -O /opt/spotnik/spotnik2hmi_V2/nextion/NX4832K035.tft
wget https://github.com/F8ASB/spotnik2hmi_V2/blob/master/nextion/NX4832T035.tft -O /opt/spotnik/spotnik2hmi_V2/nextion/NX4832T035.tft
