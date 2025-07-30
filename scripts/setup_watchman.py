# scripts/setup_watchman.py
import json
import os
import subprocess

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "config.json")
BATS_DIR = os.path.join(os.path.dirname(__file__), "..", "bat")

def remove_existing_trigger(local_path, trigger_name):
    try:
        result = subprocess.run(
            ["watchman", "trigger-del", local_path, trigger_name],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            print(f"🗑️ Ancien déclencheur supprimé : {trigger_name}")
    except Exception as e:
        print(f"⚠️ Erreur lors de la suppression de l'ancien trigger : {e}")

def remove_existing_watch(local_path):
    try:
        result = subprocess.run(
            ["watchman", "watch-del", local_path],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            print(f"🗑️ Ancienne surveillance supprimée : {local_path}")
    except Exception as e:
        print(f"⚠️ Erreur lors de la suppression de la surveillance : {e}")

def setup_watchman():
	if not os.path.exists(CONFIG_PATH):
		print(f"❌ Fichier de configuration introuvable : {CONFIG_PATH}")
		return

	with open(CONFIG_PATH, "r", encoding="utf-8") as f:
		config = json.load(f)

	for remote_name, remote_config in config.items():
		backups = remote_config.get("backups", [])
		for backup in backups:
			local_path = backup["local"]
			bat_name = backup.get("name") or os.path.basename(local_path.rstrip("\\/"))
			bat_path = os.path.abspath(os.path.join(BATS_DIR, f"sync_{bat_name}.bat"))

			if not os.path.exists(bat_path):
				print(f"⚠️ Script .bat introuvable pour {bat_name}, ignoré.")
				continue

			print(f"🔧 Configuration de Watchman pour : {local_path}")

			# Supprimer les ancienne config !
			trigger_name = f"rclone_sync_{bat_name}"
			remove_existing_trigger(local_path, trigger_name)
			remove_existing_watch(local_path)

			# Réenregistrer le dossier à surveiller
			try:
				subprocess.run(["watchman", "watch", local_path], check=True)
			except subprocess.CalledProcessError as e:
				print(f"❌ Échec lors du watch sur {local_path} : {e}")
				continue


			# Définir trigger pour tout fichier dans le dossier watch
			trigger_definition = [
				"trigger",
				local_path,
				{
					"name": trigger_name,
					"expression": ["true"],
					"command": ["cmd.exe", "/c", bat_path]
				}
			]

			subprocess.run(
				["watchman", "-j"],
				input=json.dumps(trigger_definition),
				text=True,
				check=True
			)
			print(f"✅ Déclencheur Watchman configuré pour {bat_name}.")

if __name__ == "__main__":
    setup_watchman()
