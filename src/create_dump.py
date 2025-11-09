""" dump (zrzut) danych Meilisearch """
import os
from pathlib import Path
from dotenv import load_dotenv
import meilisearch


MEILI_HOST = "http://localhost:7700"
INDEX_NAME = "wikihum"
env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)
MEILI_MASTER_KEY = os.environ.get("MEILI_MASTER_KEY")
MEILI_API_KEY = os.environ.get('MEILI_API_KEY')


# ------------------------------ FUNCTIONS -------------------------------------
def create_dump_with_sdk():
    """ funkcja tworzy dump indeksu """
    try:
        client = meilisearch.Client(MEILI_HOST, MEILI_API_KEY)

        client.health()
        print("Połączenie z serwerem udane")

        print("Uruchamianie tworzenia zrzutu (dump)...")
        task = client.create_dump()

        print(f"Zadanie uruchomione. UID zadania: {task.task_uid}")
        print("Oczekiwanie na zakończenie zadania (to może potrwać)...")

        # timeout na 1 godzinę
        max_timeout = 3600 * 1000
        final_task = client.wait_for_task(task.task_uid, timeout_in_ms=max_timeout, interval_in_ms=1000)

        if final_task.status == 'succeeded':
            print("✅ Dump został pomyślnie utworzony na serwerze.")

        else:
            print(f"Status zadania: {final_task.status}")
            print(f"Szczegóły błędu: {final_task.error}")

    except Exception as e:
        print(f"Wystąpił nieoczekiwany błąd: {e}")


# ------------------------------ MAIN ------------------------------------------
if __name__ == "__main__":
    create_dump_with_sdk()
