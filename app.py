""" app (flask) - WikiHumSearch """
import os
from pathlib import Path
from flask import Flask, jsonify, request, send_from_directory
import meilisearch
from meilisearch.errors import MeilisearchApiError
from dotenv import load_dotenv


MEILI_HOST = "http://localhost:7700"
INDEX_NAME = "wikihum"
env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)
MEILI_API_KEY = os.environ.get('MEILI_API_KEY')

client = meilisearch.Client(MEILI_HOST, MEILI_API_KEY)
app = Flask(__name__, static_folder='static')


# ------------------------------ API ENDPOINTS ---------------------------------
@app.route("/")
def serve_index():
    """funkcja serwuje główny plik HTML"""
    return send_from_directory(app.static_folder, 'index.html')

@app.route("/search")
def search():
    """obsługa zapytań wyszukiwania z frontendu"""
    query = request.args.get('q')

    FIXED_SEMANTIC_RATIO = 0.9

    if not query:
        return jsonify({"error": "Parametr 'q' jest wymagany"}), 400

    search_params = {
            "locales": ["pol"],
            "attributesToCrop": ["description:75"],
            'attributesToHighlight': ['*'],
            'showRankingScore': True,
            'hybrid': {
                "semanticRatio": FIXED_SEMANTIC_RATIO,
                "embedder": "openai"
            }
        }

    print(f"⚡️ Wykonuję wyszukiwanie hybrydowe ze stałym ratio: {FIXED_SEMANTIC_RATIO}")

    index = client.index(INDEX_NAME)
    try:
        search_results = index.search(query, search_params)
        return jsonify(search_results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/entry/<entry_id>")
def get_entry(entry_id):
    """ pobiera i zwraca dane jednego dokumentu na podstawie jego ID."""
    try:
        index = client.index(INDEX_NAME)
        entry = index.get_document(entry_id)
        return jsonify(dict(entry))
    except MeilisearchApiError as e:
        if e.code == 'document_not_found':
            return jsonify({"error": "Nie znaleziono hasła o podanym identyfikatorze."}), 404
        return jsonify({"error": str(e)}), 500


# -------------------------------- MAIN ----------------------------------------
if __name__ == '__main__':
    app.run(port=8081, debug=True)
