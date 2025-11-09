""" konwersja plików txt na pliki zbiorczy json """
import os
import json
from pathlib import Path


INPUT_DIR = Path('..') / 'data_pl'
# dane mają około 130 mb, do importu pliki powinny mieć do 100 mb 
OUTPUT_FILE_1 = Path('..') / 'json' / 'wikihum_pl_1.json'
OUTPUT_FILE_2 = Path('..') / 'json' / 'wikihum_pl_2.json'


# ---------------------------- FUNCTIONS ---------------------------------------
def parse_file(file_path):
    """ Przetwarza pojedynczy plik .txt i konwertuje go na słownik (obiekt JSON)."""
    record = {
        'id': None,
        'label': None,
        'time': None,
        'link': None
    }

    property_list = []

    filename = os.path.basename(file_path)
    record['id'] = os.path.splitext(filename)[0]

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()

                if not line:
                    continue

                if line.startswith('label: '):
                    record['label'] = line.split('label: ', 1)[1]
                elif line.startswith('time: '):
                    record['time'] = line.split('time: ', 1)[1]
                elif line.startswith('link: '):
                    record['link'] = line.split('link: ', 1)[1]
                elif line.startswith('alias: '):
                    lista = line.split('alias: ', 1)[1].split(',')
                    record['alias'] = ', '.join(lista)
                elif line.startswith('opis: '):
                    record['description'] = line.split('opis: ', 1)[1]
                else:
                    if '- jest to:' in line:
                        line = line.replace('- jest to:','').strip()
                        if '(' in line:
                            pos = line.find('(')
                            line = line[:pos].strip()
                        record['class'] = line
                    elif '- współrzędne geograficzne:' in line:
                        property_list.append(line)
                        line = line.replace('- współrzędne geograficzne:','').strip()
                        if '(' in line:
                            pos = line.find('(')
                            line = line[:pos].strip()
                        record['geo'] = line
                    else:
                        property_list.append(line)

        record['property'] = "\n".join(property_list)

        if record['label'] is None and record['time'] is None and record['link'] is None:
            print(f"Ostrzeżenie: Plik {filename} wygląda na pusty lub nie zawierał pasujących pól. Pomijam.")
            return None

        return record

    except Exception as e:
        print(f"Błąd podczas przetwarzania pliku {file_path}: {e}")
        return None


def main():
    """ funkcja znajduje pliki, przetwarza je i zapisuje do JSON. """
    all_data = []

    print(f"Przetwarzanie plików z folderu: {INPUT_DIR}...")

    file_count = 0
    processed_count = 0

    for filename in os.listdir(INPUT_DIR):
        if filename.endswith('.txt'):
            file_count += 1
            file_path = os.path.join(INPUT_DIR, filename)

            record = parse_file(file_path)

            if record:
                all_data.append(record)
                processed_count += 1

            if processed_count % 5000 == 0 and processed_count > 0:
                print(f"Przetworzono {processed_count} plików...")
            
            # zapis pierwszego pliku dla ok. 50% zawartosci
            if processed_count == 110000:
                try:
                    with open(OUTPUT_FILE_1, 'w', encoding='utf-8') as f:
                        json.dump(all_data, f, ensure_ascii=False, indent=2)
                        all_data = []
                except Exception as e:
                    print(f"Błąd krytyczny podczas zapisu do pliku JSON: {e}")


    print(f"Zakończono skanowanie. Znaleziono {file_count} plików .txt.")
    print(f"Pomyślnie przetworzono {processed_count} plików.")

    try:
        # zapis drugiego pliku
        print(f"Zapisywanie danych do pliku: {OUTPUT_FILE_2}...")
        with open(OUTPUT_FILE_2, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)
        print(f"Pomyślnie zapisano {processed_count} rekordów do {OUTPUT_FILE_2}.")
    except Exception as e:
        print(f"Błąd krytyczny podczas zapisu do pliku JSON: {e}")


# ---------------------------------- MAIN --------------------------------------
if __name__ == "__main__":
    main()
