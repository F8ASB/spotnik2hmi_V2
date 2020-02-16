![alt tag](http://blog.f8asb.com/wp-content/uploads/2018/12/spotnik2hmilogo.png)
## UNIQUEMENT POUR ECRAN NEXTION 3,5" Version K NX4832K035_011

Software for Nextion and Spotnik Hamradio RRF Network

![alt tag](http://blog.f8asb.com/wp-content/uploads/2019/01/bootV2.jpg)


## HISTORIQUE

Le projet est née sur une idée de Dimitri F5SWB, Toufik F0DEI est venu aider Dimitri en proposant
les premiers scripts pour communiquer avec l’écran Nextion.
Le projet était d’ajouter un écran Nextion à la distribution du Spotnik distribuée par F5NLG.
Je me suis ajouté au groupe afin de donner un coup de main pour finaliser le projet.
Une belle experience d’un travail collaboratif, qui au bout de 2 semaines proposait déjà 90% des fonctionnalités finales.

Spotnik2hmi permet de gérer un ecran de type Nextion sur un Spotnik (Hotspot analogique sur reseau RRF)
Pour plus d'informations se rendre sur: <https://f5nlg.wordpress.com/category/hotspot/>

ENJOY ;)

## LA TEAM 
![alt tag](http://blog.f8asb.com/wp-content/uploads/2019/01/La-team-dev-spotnik2hmi.jpg "TEAM")

## LE CABLAGE
#### Câblage Raspberry Pi:
![alt tag](http://blog.f8asb.com/wp-content/uploads/2019/01/branchementUARTRPi.png "Câblage Raspberry Pi")
#### Câblage Orange Pi Zero sur Uart1:
![alt tag](http://blog.f8asb.com/wp-content/uploads/2019/01/branchementUART1.png "Câblage Orange Pi Zero")

Il y a 2 pin avec du 5V à vous de choisir celui que vous souhaitez utiliser
#### Sur port Usb:
![alt tag](http://blog.f8asb.com/wp-content/uploads/2019/01/hmi_usb.jpg "Sur port Usb")
#### Sur carte SVXCARD:
![alt tag](http://blog.f8asb.com/wp-content/uploads/2019/01/svcard_nextion.jpg "Sur carte SVXCARD")

## INSTALLATION LOGICIEL


Cette documentation considère que vous partez de l'installation d’une image du **Spotnik 1.9** disponible sur le site de F5NLG et fonctionnelle sur Raspberry ou Orange Pi. Penser à etendre la carte SD par le menu raspi-config et selectionner 7 - Advanced option puis A1 Expand filesystem

En mode Root

Procéder à la mise à jour du système si necessaire:
```
apt-get update
apt-get upgrade
```

Télécharger le fichier **install.sh**

```
wget https://raw.githubusercontent.com/F8ASB/spotnik2hmi_V2/master/install.sh
```

Le rendre exécutable avec la commande:


```
chmod +x install.sh
```

taper:
```
 ./install.sh
```

Il ne reste plus qu'a vous laissez guider, pour choisir, utiliser les flèches et la barre espace pour sélectionner puis la touche entrée pour valider.

Première partie installation du script:
Choisissez SPOTNIK2HMI avec la barre espace et valider en appuyant sur la touche tabulation pour sélectionner Ok puis la touche Entrée.
L'installation du script s'effectura.

Relancer le ./install.sh et cette fois ci choisir NEXTION

Le choix Nextion permet de programmer l'écran Nextion directement depuis le script, le chargement dure environ 20min. Le protocole simple utilisé pour le transfert de fichier peut entrainer des coupures de transmission.
Vous pouvez également choisir de mettre le fichier .tft directement dans une carte SD et la mettre sur le lecteur de l'écran.
<https://github.com/F8ASB/spotnik2hmi_V2/raw/master/nextion/NX4832K035.tft>

Il faut absolument connaitre le port sur lequel est relié l'écran et disposer d'un ecran avec comme reference NX4832K035.

Une fois que tout est fini faire un reboot du système en tapant:
```
reboot
```
Rendez-vous sur le GUI, pour entrer votre indicatif.

## INTERFACE LOGICIEL D'INSTALLATION
![alt tag](http://blog.f8asb.com/wp-content/uploads/2019/01/choix_install.png)
![alt tag](http://blog.f8asb.com/wp-content/uploads/2019/01/type_ecranV3.png)
![alt tag](http://blog.f8asb.com/wp-content/uploads/2019/01/choix_port.png)

## FAQ

#### Ca ne marche pas.
Lisez avec attention, les lignes qui suivent sont faites pour vous, comprenez bien qu'avec seulement ses trois mots, il nous sera difficile de vous aider.
#### Lors de l'installation, j'ai une information qui m'annonce que je n'ai pas assez de place disponible.
Vérifier que vous avez bien étendu l'image: taper raspi-config -&gt; choix 7 advanced option -&gt;1 expand Filesystem. Utiliser une carte SD appropriée.
#### Mon écran reste toujours sur la première page boot.
Vérifier dans le fichier /etc/rc.local (fichier de démarrage) que le lancement du script y est bien présente. 
Lancer le script à la main pour voir si la communication est opérationnelle.

```
sudo python3 /opt/spotnik/spotnik2hmi_V2/spotnik2hmi.py (choix du com) (vitesse)
```
#### Comment vérifier quelle est l'erreur qui entraine l'arrêt du script spotnik2hmi?
Il faut lancer le script en manuel en ssh depuis une console.
Taper la commande 
```
sudo python3 /opt/spotnik/spotnik2hmi_V2/spotnik2hmi.py (choix du com) (vitesse)
```
Vous aurez toutes les commandes en monitoring.

#### Je rentre les informations par le menu ssh mais elles n'apparaissent pas dans le Nextion ou elles sont différentes.
Les informations affichées sur le Nextion sont reprises de ce qui est entré dans l'interface web GUI de la distribution spotnik.
### Le script plante ou ne fonctionne pas quand je change de salon (tec/fon):
Vérifier que les dashboard sont fonctionnels:

* RRF:<http://rrf.f5nlg.ovh>

### Quelle est le temps de chargement du fichier sur l'écran Nextion?
Si on utilise le menu le temps de chargement est d'environ 10min selon le type d'écran.L'interêt de cette installation c'est qu'elle est simple et qu'elle vous permet de valider que l'écran communique bien avec votre système.
Pour gagner du temps, il est possible de copier le fichier .tft sur une carte micro sd et l'insérer sur le lecteur de carte. L'installation démarrera automatiquement.Les fichiers .tft se trouvent dans le répertoire /opt/spotnik/spotnik2hmi/nextion/ après installation.Vous pouvez aussi les retrouver sur Github ou le projet y est hébergé(répertoire nextion).
### Mon écran ne réagit pas ou les commandes sont pas prises en compte?
Il peut y avoir un problème de script, rebooter votre installation.<br />Le moyen simple est de regarder l'heure sur la page, le script l'actualise, si celle-ci n'est pas en phase, c'est que le script est arrêté.
### Je suis sur un Raspberry Pi 3B ou B+ et je n'arrive pas à programmer l'écran malgré que tous les câblages soient bons.
Utiliser la commande raspi-config aller dans le menu5 Interfacing Option valider par Enter, choisir P6 Serial valider par Enter, repondre Non à la premiere question puis Oui à la deuxieme question.

Il y a également le bluetooth qui prend la main sur la liaison et empêche l'utilisation du port. Il faut désactivé  le bluetooth.
Voici la commande:
```
sudo echo "dtoverlay=pi3-disable-bt" >> /boot/config.txt 
```
suivi d'un 
```
sudo reboot
```
### Je suis sur Orange Pi Zero, l'écran a bien été programmé, mais il reste sur la page de démarrage
Il est probable que le problème soit lié au fait que le GUI n'est pas lancé.Dans le doute, saisissez les commandes suivantes:
```
cd /opt/spotnik/gui
make restart
```
### Je lance le script à la main et je reçois une erreur

![alt tag](http://blog.f8asb.com/wp-content/uploads/2019/01/erreur-lancement.png")

Quand vous lancer le script le port et la vitesse sont des variables qui doivent être indiquées. le port peut être ttyS0 (Orange Pi) ou ttyAMA0 (Raspberry Pi) ou ttyUSB0 (adaptateur USB/série ). Un exemple dans l'image ci-dessus pour le lancement sur Raspberry câblage sur&nbsp;GPIO.</em></p>



### Comment mettre à jour mon script spotnik2hmi et mon écran?
Sur cette nouvelle version, vous pouvez faire les mise à jour directement depuis l'écran. Depuis l'ecran, cliquer sur le Smetre en haut à gauche,puis sur l'icone système (engrenage sur la droite), puis sur update. L'écran vous donnera les mise à jour disponibles. Un reboot sera lancer automatiquement après.

### Je constate une latence avant que l'indicatif s'affiche sur l'écran.
Le script va lire la page du Dashboard pour extraire l'indicatif, votre qualité de connexion internet et le temps de traitement explique cette latence</p>
### J'ai une erreur lors de la mise à jour du Raspberry
W: Une erreur s'est produite lors du contrôle de la signature. Le dépôt n'est pas mis à jour et les fichiers d'index précédents seront utilisés. Erreur de GPG : https://packages.sury.org jessie InRelease : Les signatures suivantes n'ont pas pu être vérifiées car la clé publique n'est pas disponible : NO_PUBKEY B188E2B695BD4743

Lancer la commande suivante:

sudo wget -O /etc/apt/trusted.gpg.d/php.gpg https://packages.sury.org/php/apt.gpg--2019-03-18 21:28:18 https://packages.sury.org/php/apt.gpg
