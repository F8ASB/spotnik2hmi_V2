#!/bin/bash
#VERSION 130719a


whiptail --title "INFORMATION:" --msgbox "Ce script considere que vous partez d une image disponible par F5NLG du Spotnik 1.95 et fonctionnelle sur Raspberry ou Orange Pi. Il permet d ajouter un ecran Nextion a la distribution. Plus d informations sur http://blog.f8asb.com/spotnik2hmi.                                                                                         Team F0DEI/F5SWB/F8ASB" 15 60


#!/bin/bash
INSTALL=$(whiptail --title "Choisir votre installation" --radiolist \
"Que voulez vous installer?" 15 60 4 \
"SPOTNIK2HMI" "Gestion Nextion avec Spotnik " ON \
"NEXTION" "Programmation ecran Nextion " OFF 3>&1 1>&2 2>&3)
 
exitstatus=$?

pathinstall="/opt/spotnik/spotnik2hmi_V2"

if [ $exitstatus = 0 ]; then
    echo "Installation de :" $INSTALL

else
    echo "Vous avez annulé"
fi

if [ $INSTALL = "SPOTNIK2HMI" ]; then
 
echo "INSTALLATION DEPENDANCE PYTHON"

#Dependances necessaire deja presentes dans l'image Spotnik

# Sur image Orange Pi

# apt-get install python3-serial
# apt install python3-pip
# pip3 install speedtest-cli
# apt-get install libpython3-dev
# apt-get install libasound2-dev
# pip3 install pyalsaaudio

# Sur image Raspberry (Buster)

# apt-get update
# apt-get install python3-serial
# apt install python3-pip
# pip3 install speedtest-cli
# pip3 install pyalsaaudio

#apt-get update
#apt-get upgrade
rm - rf /opt/spotnik/spotnik2hmi_V2
apt-get install python3-serial
apt install python3-pip
pip3 install speedtest-cli
apt-get install libpython3-dev
apt-get install libasound2-dev
pip3 install pyalsaaudio
pip3 install requests
apt-get install python-serial

echo "INSTALLATION scripts python"
git clone https://github.com/F8ASB/spotnik2hmi_V2.git $pathinstall

chmod +x $pathinstall/spotnik2hmi.py

echo "INSTALLATION UTILITAIRE METAR"
git clone https://github.com/python-metar/python-metar.git $pathinstall/python-metar/

chmod +x $pathinstall/python-metar/get_report.py

#Dans /etc/spotnik/
wget -P /etc/spotnik/ https://raw.githubusercontent.com/F8ASB/package_spotnik/master/Divers_files/restart.exp
chmod +x /etc/spotnik/restart.exp
wget -P /etc/spotnik/ https://raw.githubusercontent.com/F8ASB/package_spotnik/master/sounds_salons/Sexp.wav
wget -P /etc/spotnik/ https://raw.githubusercontent.com/F8ASB/package_spotnik/master/sounds_salons/Sreg.wav

#Fichiers Database
rm /opt/spotnik/spotnik2hmi_V2/datas/amat_annuaire.csv
wget -P /opt/spotnik/spotnik2hmi_V2/datas/ https://raw.githubusercontent.com/F4ICR/datas/master/amat_FR.dat
wget -P /opt/spotnik/spotnik2hmi_V2/datas/ https://raw.githubusercontent.com/F4ICR/datas/master/cache_amat_FR.dat
wget -P /opt/spotnik/spotnik2hmi_V2/datas/ https://raw.githubusercontent.com/F4ICR/datas/master/database_version


PORT=$(whiptail --title "Choix du Port de communication" --radiolist \
"Sur quoi raccorder vous le Nextion?" 15 60 4 \
"ttyAMA0" "Sur Raspberry Pi " ON \
"ttyS1" "Sur Orange Pi " OFF \
"ttyUSB0" "Orange Pi ou Raspberry Pi " OFF 3>&1 1>&2 2>&3)

exitstatus=$?
if [ $exitstatus = 0 ]; then

sed -i '/make start/a \python3 '$pathinstall'/spotnik2hmi.py '$PORT' 9600' /etc/rc.local

sed -i '/make start/a \sleep 20' /etc/rc.local
else
    echo "Vous avez annulé"
fi
exit

else

PORT=$(whiptail --title "Choix du Port de communication" --radiolist \
"Sur quoi raccorder vous le Nextion?" 15 60 4 \
"ttyAMA0" "Sur Raspberry Pi " ON \
"ttyS1" "Sur Orange Pi " OFF \
"ttyUSB0" "Orange Pi ou Raspberry Pi " OFF 3>&1 1>&2 2>&3)
 
exitstatus=$?
if [ $exitstatus = 0 ]; then
    echo "Port du Nextion :" $PORT
else
    echo "Vous avez annule"
fi

ECRAN=$(whiptail --title "Choix type d'ecran NEXTION" --radiolist \
"Quel Type d'ecran ?" 15 60 4 \
"NX4832K035.tft" "Ecran 3,5 Enhanced" ON 3>&1 1>&2 2>&3)
 
exitstatus=$?
if [ $exitstatus = 0 ]; then
    echo "Type d'écran :" $ECRAN
python $pathinstall'/nextion/nextion.py' $pathinstall'/nextion/'$ECRAN '/dev/'$PORT

else
    echo "Vous avez annule"
fi
fi

echo ""
echo " ENJOY ;) TEAM:F0DEI,F5SWB,F8ASB"
echo ""

