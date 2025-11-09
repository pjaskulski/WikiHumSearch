""" tworzenie indeksu meilisearch na podstawie danych w pliku json """
import os
import json
import time
from pathlib import Path
from dotenv import load_dotenv
import meilisearch
from meilisearch.errors import MeilisearchApiError
import stopwordsiso as stopwords


MEILI_HOST = "http://localhost:7700"
INDEX_NAME = "wikihum"
env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)
MEILI_API_KEY = os.environ.get('MEILI_API_KEY')
OPENAI_ORG_ID = os.environ.get('OPENAI_ORG_ID')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

client = meilisearch.Client(MEILI_HOST, MEILI_API_KEY)


# -------------------------------- FUNCTIONS -----------------------------------
def setup_index_and_documents():
    """ utworzenie indeksu Meilisearch """

    print("Konfiguracja indeksu...")
    try:
        task = client.delete_index(INDEX_NAME)
        client.wait_for_task(task.task_uid, timeout_in_ms=50000)
        print(f"Indeks '{INDEX_NAME}' został usunięty.")
    except MeilisearchApiError as e:
        if e.code == 'index_not_found':
            print(f"Indeks '{INDEX_NAME}' nie istniał, tworzę nowy.")
        else:
            raise e

    client.create_index(uid=INDEX_NAME, options={'primaryKey': 'id'})
    index = client.index(INDEX_NAME)

    template = (
        "{% for field in fields %} {% if field.is_searchable and field.value != nil %}{{ field.name }}: {{ field.value|truncatewords: 100 }} {% endif %} {% endfor %}"
    )

    stop_words_pl = stopwords.stopwords('pl')

    settings = {
        'searchableAttributes': ['label', 'alias', 'description', 'property', 'class', 'geo'],
        'filterableAttributes': ['class'],
        'sortableAttributes': ['label', 'class'],
        'rankingRules': [
            'words',
            'typo',
            'proximity',
            'attribute',
            'sort',
            'exactness'
        ],
        'stopWords': list(stop_words_pl),
        'localizedAttributes': [
            {'attributePatterns': ['*'], 'locales': ['pol']}
        ],
        'embedders': {
            "openai": {
                "source": "openAi",
                "model": "text-embedding-3-small",
                "apiKey": OPENAI_API_KEY,
                "documentTemplate": template
            }
        }
    }

    print("Aktualizacja ustawień indeksu...")
    task = index.update_settings(settings)
    client.wait_for_task(task.task_uid, timeout_in_ms=50000)

    # import danych z plików json
    print("Dodawanie dokumentów do indeksu...")
    wikihum_json_path_1 = Path('..') / 'json' / 'wikihum_pl_1.json'
    with open(wikihum_json_path_1, 'r', encoding='utf-8') as f:
        wiki_data_1 = json.load(f)

    wikihum_json_path_2 = Path('..') / 'json' / 'wikihum_pl_2.json'
    with open(wikihum_json_path_2, 'r', encoding='utf-8') as f:
        wiki_data_2 = json.load(f)

    max_timeout = 3600 *1000

    # część 1
    print("Dodawanie pierwszej części dokumentów do indeksu ...")
    task = index.add_documents(wiki_data_1)

    print(f"Wysłano wszystkie dokumenty. Oczekiwanie na zakończenie zadania (UID: {task.task_uid})...")
    client.wait_for_task(task.task_uid, timeout_in_ms=max_timeout)
    print("✅ Wszystkie dokumenty z pierwszej części dodane i zaindeksowane.")

    # część 2
    print("Dodawanie drugiej części dokumentów do indeksu ...")
    task2 = index.add_documents(wiki_data_2)

    print(f"Wysłano wszystkie dokumenty. Oczekiwanie na zakończenie zadania (UID: {task2.task_uid})...")
    client.wait_for_task(task2.task_uid, timeout_in_ms=max_timeout)
    print("✅ Wszystkie dokumenty z drugiej części dodane i zaindeksowane.")

    print("✅ Konfiguracja indeksu Meilisearch zakończona pomyślnie.")


# ------------------------------- MAIN -----------------------------------------
if __name__ == '__main__':
    # pomiar czasu wykonania
    start_time = time.time()

    setup_index_and_documents()

    # czas wykonania programu
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f'Czas wykonania programu: {time.strftime("%H:%M:%S", time.gmtime(elapsed_time))} s.')
