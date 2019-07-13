#!/bin/bash
whiptail --title "INFORMATION:" --msgbox "Ce script considere que vous partez d une image disponible par F5NLG du Spotnik 1.9 et fonctionnelle sur Raspberry ou Orange Pi. Il permet d ajouter un ecran Nextion a la distribution. Plus d informations sur http://blog.f8asb.com/spotnik2hmi.                                                                                         Team F0DEI/F5SWB/F8ASB" 15 60


#!/bin/bash
INSTALL=$(whiptail --title "Choisir votre installation" --radiolist \
"Que voulez vous installer?" 15 60 4 \
"SPOTNIK2HMI" "Gestion Nextion avec Spotnik " ON \
"NEXTION" "Programmation ecran Nextion " OFF 3>&1 1>&2 2>&3)
 
exitstatus=$?

if [ $exitstatus = 0 ]; then
    echo "Installation de :" $INSTALL

else
    echo "Vous avez annulé"
fi

if [ $INSTALL = "SPOTNIK2HMI" ]; then
 
echo "INSTALLATION DEPENDANCE PYTHON"

apt-get install python-dev
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python3 get-pip.py
pip3 install setuptools
pip3 install requests
pip3 install speedtest-cli
pip3 install pyalsaaudio
pip3 install configparser
pip3 install pyserial
#python3 -m pip install pyserial


echo "INSTALLATION scripts python"
git clone https://github.com/F8ASB/spotnik2hmi_V2.git /opt/spotnik/spotnik2hmi_v2/

chmod +x /opt/spotnik/spotnik2hmi_v2/spotnik2hmi.py

echo "INSTALLATION UTILITAIRE METAR"
git clone https://github.com/python-metar/python-metar.git /opt/spotnik/spotnik2hmi_v2/python-metar/


PORT=$(whiptail --title "Choix du Port de communication" --radiolist \
"Sur quoi raccorder vous le Nextion?" 15 60 4 \
"ttyAMA0" "Sur Raspberry Pi " ON \
"ttyS0" "Sur Orange Pi " OFF \
"ttyUSB0" "Orange Pi ou Raspberry Pi " OFF 3>&1 1>&2 2>&3)

exitstatus=$?
if [ $exitstatus = 0 ]; then

sed -i '/make start/a \python /opt/spotnik/spotnik2hmi_v2/spotnik2hmi.py '$PORT' 9600' /etc/rc.local

sed -i '/make start/a \sleep 10' /etc/rc.local
else
    echo "Vous avez annulé"
fi
exit

else

PORT=$(whiptail --title "Choix du Port de communication" --radiolist \
"Sur quoi raccorder vous le Nextion?" 15 60 4 \
"ttyAMA0" "Sur Raspberry Pi " ON \
"ttyS0" "Sur Orange Pi " OFF \
"ttyUSB0" "Orange Pi ou Raspberry Pi " OFF 3>&1 1>&2 2>&3)
 
exitstatus=$?
if [ $exitstatus = 0 ]; then
    echo "Port du Nextion :" $PORT
else
    echo "Vous avez annule"
fi

ECRAN=$(whiptail --title "Choix type d'ecran NEXTION" --radiolist \
"Quel Type d'ecran ?" 15 60 4 \
"NX4832K035.tft" "Ecran 3,5 Enhanced" OFF \
"NX4832T035.tft" "Ecran 3,5 Basic" ON 3>&1 1>&2 2>&3)
 
exitstatus=$?
if [ $exitstatus = 0 ]; then
    echo "Type d'écran :" $ECRAN
python /opt/spotnik/spotnik2hmi/nextion/nextion.py '/opt/spotnik/spotnik2hmi_v2/nextion/'$ECRAN '/dev/'$PORT

else
    echo "Vous avez annule"
fi
fi


echo ""
echo "INSTALL TERMINEE AVEC SUCCES"
echo ""
echo " ENJOY ;) TEAM:F0DEI,F5SWB,F8ASB"
echo ""

