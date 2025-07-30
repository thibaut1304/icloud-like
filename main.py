# main.py
import subprocess
import json

ACTIONS = [
	{
		"label": "📦 Installer les outils nécessaires (rclone, watchman, python)",
		"command": ["python", "install/install.py"]
	},
	{
		"label": "⚙️  Générer la configuration rclone (generate_rclone_config.py)",
		"command": ["python", "scripts/generate_rclone_config.py"]
	},
	{
		"label": "📝 Générer les scripts .bat pour chaque partage",
		"command": ["python", "scripts/generate_bat_files.py"]
	},
	{
		"label": "👀 Configurer Watchman pour surveiller les dossiers locaux",
		"command": ["python", "scripts/setup_watchman.py"]
	},
	{
		"label": "🔎 Vérifier les déclencheurs Watchman actifs",
		"custom": True
}
]


def prompt_and_run():
    for step in ACTIONS:
        answer = input(f"\n➡️ {step['label']} ? (y/n) ").strip().lower()
        if answer == "y":
            print(f"\n⏳ Exécution : {step['label']}")
            try:
                if step.get("custom"):
                    # Commande spéciale : watchman trigger-list sur tous les répertoires
                    result = subprocess.run(["watchman", "watch-list"], capture_output=True, text=True)
                    dirs = json.loads(result.stdout).get("roots", [])
                    for d in dirs:
                        print(f"\n📂 Déclencheurs pour : {d}")
                        subprocess.run(["watchman", "trigger-list", d])
                else:
                    subprocess.run(step["command"], check=True)
            except subprocess.CalledProcessError:
                print("❌ Une erreur est survenue pendant l’exécution de cette étape.")
        else:
            print("⏩ Étape ignorée.")



if __name__ == "__main__":
    print("🔧 Assistant de configuration iCloud-like Backup\n")
    prompt_and_run()
    print("\n✅ Configuration terminée.")
