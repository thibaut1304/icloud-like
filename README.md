# ☁️ iCloud-like Local Backup to Nextcloud

Ce projet permet de mettre en place une **sauvegarde unidirectionnelle automatique** de n’importe quel dossier local Windows vers une instance **Nextcloud**, sans utiliser de client lourd.

> 📦 Inspiré d’iCloud, mais libre et auto-hébergé et sur n'importe quel os !

## 🔧 Technologies utilisées

- **Python 3** : Pour executer ces script
- **rclone** : pour synchroniser le dossier local vers Nextcloud
- **watchman** : pour détecter les changements en temps réel
- **.bat** : pour exécuter la synchro à chaque événement
- **winget** : pour tout installer automatiquement

---

## 📝 Prérequis

- Windows 10/11 avec [winget](https://learn.microsoft.com/en-us/windows/package-manager/winget/) Installation dans install.py
- Un compte Nextcloud avec WebDAV activé
- Python3 -> Installatrion dans install.py

---

## 🚀 Installation automatique

```bash
python main.py
```


TODO:
Suppression trigger watchman -> OK Suppression des anciens trigger et ancien dossier surveiller pour nouvelle config ou modification !
