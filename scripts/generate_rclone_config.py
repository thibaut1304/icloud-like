# config/generate_rclone_config.py
import json
import os
import sys
import argparse
import subprocess

CONFIG_PATH = os.path.expandvars(r"%APPDATA%\rclone\rclone.conf")
CONFIG_JSON = os.path.join(os.path.dirname(__file__), "..", "config", "config.json")

def obscure_password(password):
    try:
        result = subprocess.run(["rclone", "obscure", password], capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        print("❌ Échec lors de l'obfuscation du mot de passe avec rclone.")
        sys.exit(1)

def parse_existing_config():
    if not os.path.exists(CONFIG_PATH):
        return []
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return f.read().strip().splitlines()

def write_config_blocks(config_lines):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(config_lines) + "\n")

def generate_rclone_config(force=False):
    if not os.path.exists(CONFIG_JSON):
        print(f"❌ Le fichier {CONFIG_JSON} est introuvable.")
        sys.exit(1)

    with open(CONFIG_JSON, "r", encoding="utf-8") as f:
        all_remotes = json.load(f)

    if not isinstance(all_remotes, dict):
        print("❌ Le fichier JSON doit contenir un dictionnaire de remotes.")
        sys.exit(1)

    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    config_lines = parse_existing_config()

    for remote_name, data in all_remotes.items():
        new_block = {
            "type": data.get("config_type", "webdav"),
            "url": data["url"],
            "vendor": data.get("vendor", "nextcloud"),
            "user": data["user"],
            "pass": obscure_password(data["password"])
        }

        remote_exists = False
        for line in config_lines:
            if line.strip() == f"[{remote_name}]":
                remote_exists = True
                break

        if remote_exists and not force:
            print(f"⚠️ Le remote '{remote_name}' existe déjà dans {CONFIG_PATH}. Utilisez --force pour l'écraser.")
            continue

        # Supprimer l'ancien bloc si on force
        if remote_exists and force:
            start = config_lines.index(f"[{remote_name}]")
            end = start + 1
            while end < len(config_lines) and not config_lines[end].startswith("["):
                end += 1
            del config_lines[start:end]

        # Ajouter le new
        config_lines.append(f"[{remote_name}]")
        for key, value in new_block.items():
            config_lines.append(f"{key} = {value}")

    write_config_blocks(config_lines)
    print(f"✅ Configuration rclone mise à jour dans : {CONFIG_PATH}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Génère automatiquement le fichier rclone.conf depuis config.json")
    parser.add_argument("--force", action="store_true", help="Écrase la configuration existante si elle existe")
    args = parser.parse_args()

    generate_rclone_config(force=args.force)
