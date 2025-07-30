# install/install.py
import subprocess
import sys
import shutil
import os
import platform
import urllib.request

REQUIRED_TOOLS = {
    "rclone": "rclone",
    "watchman": "Facebook.Watchman",
    "python": "Python.Python.3.10"
}

APPINSTALLER_URL = "https://aka.ms/getwinget"


def is_windows():
    return platform.system().lower() == "windows"


def is_installed(tool):
    return shutil.which(tool) is not None


def install_with_winget(tool_id):
    try:
        print(f"\n🛠️ Installation de {tool_id} via winget...")
        subprocess.run([
            "winget", "install", "--id", tool_id, "--source", "winget", "--accept-package-agreements", "--accept-source-agreements"
        ], check=True)
        print(f"✅ {tool_id} installé avec succès.\n")
    except subprocess.CalledProcessError:
        print(f"❌ Échec de l'installation de {tool_id}.\n")
        sys.exit(1)


def try_repair_winget():
    print("\n🔄 Tentative de réparation de winget via PowerShell...")
    try:
        subprocess.run([
            "powershell", "-Command",
            "Add-AppxPackage -RegisterByFamilyName -MainPackage Microsoft.DesktopAppInstaller_8wekyb3d8bbwe"
        ], check=True)
        print("✅ Réparation de winget terminée. Veuillez relancer ce script.")
        sys.exit(0)
    except subprocess.CalledProcessError as e:
        print(f"❌ Échec de la réparation de winget : {e}")


def install_winget():
    print("\n🔄 winget non détecté, tentative d'installation d'App Installer depuis le Microsoft Store...")
    try_repair_winget()

    installer_path = os.path.join(os.getenv("TEMP"), "AppInstaller.msixbundle")
    try:
        urllib.request.urlretrieve(APPINSTALLER_URL, installer_path)
        subprocess.run([
            "powershell", "-Command", f"Start-Process ms-appinstaller:?source={APPINSTALLER_URL}"
        ], check=True)
        print("✅ App Installer lancé. Suivez les instructions à l'écran pour terminer l'installation de winget.")
        print("🔁 Relancez ce script après l'installation.")
    except Exception as e:
        print(f"❌ Échec du téléchargement ou de l'installation de winget : {e}")
    sys.exit(1)


def check_winget():
    if shutil.which("winget") is None:
        install_winget()
    else:
        print("✅ winget détecté.")


def main():
    print("\n🔧 Initialisation de l'installation iCloud-like...")

    if not is_windows():
        print("❌ Ce script ne fonctionne que sous Windows.")
        sys.exit(1)

    check_winget()

    for name, winget_id in REQUIRED_TOOLS.items():
        if is_installed(name):
            print(f"✅ {name} est déjà installé.")
        else:
            install_with_winget(winget_id)

    print("\n🚀 Tous les prérequis sont installés. Vous pouvez passer à la configuration.")


if __name__ == "__main__":
    main()
