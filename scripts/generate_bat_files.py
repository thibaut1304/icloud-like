import json
import os
import subprocess
from datetime import datetime

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "config.json")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "bat")

os.makedirs(OUTPUT_DIR, exist_ok=True)

def check_or_create_local_path(local_path):
    if not os.path.exists(local_path):
        choice = input(f"❓ Le dossier local '{local_path}' n'existe pas. Le créer ? (y/n) ").strip().lower()
        if choice == 'y':
            os.makedirs(local_path, exist_ok=True)
            print(f"✅ Dossier local créé : {local_path}")
        else:
            print("⛔ Opération annulée.")
            return False
    return True

def check_or_create_remote_path(remote_name, remote_path):
    try:
        result = subprocess.run(
            ["rclone", "lsf", f"{remote_name}:{remote_path}"],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            choice = input(f"❓ Le dossier distant '{remote_path}' n'existe pas sur le remote '{remote_name}'. Le créer ? (y/n) ").strip().lower()
            if choice == 'y':
                mkdir = subprocess.run(
                    ["rclone", "mkdir", f"{remote_name}:{remote_path}"]
                )
                if mkdir.returncode == 0:
                    print(f"✅ Dossier distant créé : {remote_name}:{remote_path}")
                else:
                    print("❌ Échec de la création du dossier distant.")
                    return False
            else:
                print("⛔ Opération annulée.")
                return False
    except Exception as e:
        print(f"❌ Erreur lors de la vérification du dossier distant : {e}")
        return False
    return True

def rclone_remote_exists(remote_name):
    try:
        result = subprocess.run(["rclone", "listremotes"], capture_output=True, text=True)
        if result.returncode != 0:
            return False
        remotes = result.stdout.strip().splitlines()
        return f"{remote_name}:" in remotes
    except Exception:
        return False

def generate_bat_files():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)

    for remote_name, remote_conf in config.items():
        if "backups" not in remote_conf:
            print(f"⚠️ Aucun champ 'backups' dans la section '{remote_name}', ignoré.")
            continue

        if not rclone_remote_exists(remote_name):
            print(f"❌ Le remote rclone '{remote_name}' n'existe pas. Veuillez d'abord exécuter generate_rclone_config.py.")
            continue

        for backup in remote_conf["backups"]:
            local_path = backup["local"]
            remote_path = backup["remote"]
            bat_name = backup.get("name") or os.path.basename(local_path.rstrip("\\/"))
            log_file = os.path.join(local_path, "icloud_sync.log")

            if not check_or_create_local_path(local_path):
                continue
            if not check_or_create_remote_path(remote_name, remote_path):
                continue

            bat_path = os.path.join(OUTPUT_DIR, f"sync_{bat_name}.bat")
            with open(bat_path, "w", encoding="utf-8") as bat_file:
                bat_file.write("@echo off\n")
                bat_file.write(f"echo [%date% %time%] Synchronisation lancée >> \"{log_file}\"\n")
                bat_file.write(f"rclone sync \"{local_path}\" {remote_name}:\"{remote_path}\" --delete-excluded --copy-links\n")

            print(f"✅ Script .bat généré : {bat_path}")

if __name__ == "__main__":
    generate_bat_files()
