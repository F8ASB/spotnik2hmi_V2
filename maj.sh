#Sauvegarde des fichiers existants
mv /opt/spotnik/spotnik2hmi_V2/fonctions.py /opt/spotnik/spotnik2hmi_V2/old_version/fonctions`date +%d%m%Y`.py
mv /opt/spotnik/spotnik2hmi_V2/spotnik2hmi.py /opt/spotnik/spotnik2hmi_V2/old_version/spotnik2hmi`date +%d%m%Y`.py
mv /opt/spotnik/spotnik2hmi_V2/settings.py /opt/spotnik/spotnik2hmi_V2/old_version/settings`date +%d%m%Y`.py
mv /opt/spotnik/spotnik2hmi_V2/install.sh /opt/spotnik/spotnik2hmi_V2/old_version/install`date +%d%m%Y`.sh
mv /opt/spotnik/spotnik2hmi_V2/maj.sh /opt/spotnik/spotnik2hmi_V2/old_version/maj`date +%d%m%Y`.sh
rm /opt/spotnik/spotnik2hmi_V2/nextion/NX*.*

#Telechargement script
wget -P /opt/spotnik/spotnik2hmi_V2/ https://raw.githubusercontent.com/F8ASB/spotnik2hmi_V2/master/fonctions.py
wget -P /opt/spotnik/spotnik2hmi_V2/ https://raw.githubusercontent.com/F8ASB/spotnik2hmi_V2/master/spotnik2hmi.py 
wget -P /opt/spotnik/spotnik2hmi_V2/ https://raw.githubusercontent.com/F8ASB/spotnik2hmi_V2/master/install.sh 
wget -P /opt/spotnik/spotnik2hmi_V2/ https://raw.githubusercontent.com/F8ASB/spotnik2hmi_V2/master/settings.py
wget -P /opt/spotnik/spotnik2hmi_V2/ https://raw.githubusercontent.com/F8ASB/spotnik2hmi_V2/master/maj.sh

#Telechargement HMI 
wget -P /opt/spotnik/spotnik2hmi_V2/nextion/ https://github.com/F8ASB/spotnik2hmi_V2/raw/master/nextion/NX4832K035.tft

#Maj icao
wget -N -P /opt/spotnik/spotnik2hmi_V2/datas/ https://raw.githubusercontent.com/F8ASB/spotnik2hmi_V2/master/datas/icao.cfg

#Telechargement nouveaux fichiers

#Dans /etc/spotnik/
wget -P /etc/spotnik/ https://raw.githubusercontent.com/F8ASB/package_spotnik/master/Divers_files/restart.exp
chmod +x /etc/spotnik/restart.exp
wget -P /etc/spotnik/ https://raw.githubusercontent.com/F8ASB/package_spotnik/master/sounds_salons/Sexp.wav
wget -P /etc/spotnik/ https://raw.githubusercontent.com/F8ASB/package_spotnik/master/sounds_salons/Sreg.wav

#Fichier son Raptor
rm /opt/spotnik/spotnik2hmi_V2/datas/Sounds_Raptor/*.*
wget -P /opt/spotnik/spotnik2hmi_V2/datas/Sounds_Raptor/ https://raw.githubusercontent.com/F8ASB/package_spotnik/master/Sounds_Raptor/active.wav
wget -P /opt/spotnik/spotnik2hmi_V2/datas/Sounds_Raptor/ https://raw.githubusercontent.com/F8ASB/package_spotnik/master/Sounds_Raptor/desactive.wav

#Fichiers Database
rm /opt/spotnik/spotnik2hmi_V2/datas/amat_annuaire.csv
wget -P /opt/spotnik/spotnik2hmi_V2/datas/ https://raw.githubusercontent.com/F4ICR/datas/master/amat_FR.dat
wget -P /opt/spotnik/spotnik2hmi_V2/datas/ https://raw.githubusercontent.com/F4ICR/datas/master/cache_amat_FR.dat
wget -P /opt/spotnik/spotnik2hmi_V2/datas/ https://raw.githubusercontent.com/F4ICR/datas/master/database_version

sleep 5
reboot
