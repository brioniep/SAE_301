import os
import sys
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess

class ReloadHandler(FileSystemEventHandler):
    def on_modified(self, event):
        # Vérifie si le fichier modifié est un fichier Python ou un fichier KV
        if event.src_path.endswith('.py') or event.src_path.endswith('.kv'):
            print(f"Modification détectée dans {event.src_path}, redémarrage de l'application...")
            os.execv(sys.executable, ['python'] + sys.argv)

if __name__ == "__main__":
    path = r"C:\Users\leona\OneDrive\Bureau\SAE_301"  # Chemin à surveiller
    event_handler = ReloadHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)  # Surveille le répertoire et ses sous-répertoires
    observer.start()

    try:
        subprocess.run(["python", "main.py"])  # Lancer votre application ici
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
