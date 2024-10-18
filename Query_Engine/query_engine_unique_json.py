import json
import re
from datetime import datetime

from flask import Flask, request, jsonify, send_from_directory
import csv
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)


def find_context_in_datalake(query_result):
    for text in query_result:
        text_id = text
        for word in query_result[text]:
            pos = query_result[text][word]["positions"][0]
            paragraph = ""
            with open(f"Datalake/eventstore/Gutenbrg/{text_id}", "r") as file:
                document = file.read()
            start_content = re.search(r'\*\*\* START OF .* \*\*\*', document)
            if start_content:
                start_text = start_content.end()
                content_later = document[start_text:].strip()

                words = content_later.split()
                if 0 <= pos < len(words):
                    # Si la posición es una de las primeras 10
                    if pos < 10:
                        start = 0  # No hay suficientes palabras antes
                        end = min(len(words), pos + 10)  # Hasta 10 palabras después
                    else:
                        # Rango normal: 10 palabras antes y 10 después
                        start = max(0, pos - 10)
                        end = min(len(words), pos + 20 + 1)

                    paragraph = words[start:end]
                    paragraph = " ".join(paragraph)

            query_result[text][word]["paragraph"] = paragraph
    return query_result

def load_inverted_index_from_json(json_file):
    with open(json_file, 'r', encoding='utf-8') as f:
        inverted_index = json.load(f)
    return inverted_index


def load_metadata(file_path):
    metadata = []
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            row['release_date'] = convert_date(row['release_date'])
            metadata.append(row)
    return metadata

def convert_date(date_str):
    """ Convierte una fecha en formato 'Mes Día, Año' a 'YYYY-MM-DD' """
    try:
        date_obj = datetime.strptime(date_str, "%B %d, %Y")
        return date_obj.strftime("%Y-%m-%d")
    except ValueError:
        return ''


def search_inverted_index(query, inverted_index):
    words = query.lower().split()

    if len(words) == 0:
        return {"error": "Please provide at least one word in the query."}

    first_word = words[0]
    if first_word not in inverted_index:
        return {"message": f"No results found for '{first_word}'"}

    common_docs = set(inverted_index[first_word].keys())

    for word in words[1:]:
        if word not in inverted_index:
            return {"message": f"No results found for '{word}'"}

        current_docs = set(inverted_index[word].keys())
        common_docs = common_docs.intersection(current_docs)

        if not common_docs:
            return {"message": f"No documents contain all the words: {', '.join(words)}"}

    results = {}
    for doc in common_docs:
        results[doc] = {}
        for word in words:
            results[doc][word] = {
                "frequency": inverted_index[word][doc]["frequency"],
                "positions": inverted_index[word][doc]["positions"]
            }

    return results


def search_metadata(filters, metadata):
    results = []

    title_filter = filters.get('title', '').lower()
    author_filter = filters.get('author', '').lower()  # Nuevo filtro para el autor
    year_filter = filters.get('year', '').strip()
    month_filter = filters.get('month', '').strip()
    day_filter = filters.get('day', '').strip()
    language_filter = filters.get('language', '').lower()

    for entry in metadata:
        title_matches = title_filter in entry.get('title', '').lower() if title_filter else True

        author_matches = author_filter in entry.get('author', '').lower() if author_filter else True

        language_matches = language_filter in entry.get('language', '').lower() if language_filter else True

        entry_date = entry.get('release_date', '').strip()
        try:
            # Extraer año, mes y día de la fecha en formato 'YYYY-MM-DD'
            entry_date_obj = datetime.strptime(entry_date, "%Y-%m-%d")
            entry_year = str(entry_date_obj.year)
            entry_month = str(entry_date_obj.month).zfill(2)
            entry_day = str(entry_date_obj.day).zfill(2)
        except ValueError:
            continue

        year_matches = (year_filter == entry_year) if year_filter else True
        month_matches = (month_filter == entry_month) if month_filter else True
        day_matches = (day_filter == entry_day) if day_filter else True

        date_matches = year_matches and month_matches and day_matches

        if title_matches and author_matches and date_matches and language_matches:
            results.append(entry)

    return results


inverted_index = load_inverted_index_from_json('Datamarts/Inverted Index/word_level.json')
metadata = load_metadata('Datamarts/Metadata Database/book_metadata.csv')


@app.route('/search/word_level', methods=['GET'])
def search_unique_json_inverted():
    query = request.args.get('query', '').strip()
    if not query:
        return jsonify({"error": "No search query provided"}), 400

    # Llamar a la función de búsqueda
    results = search_inverted_index(query, inverted_index)
    results = find_context_in_datalake(results)
    return jsonify(results)


# Ruta para realizar la búsqueda en los metadatos
@app.route('/search/metadata', methods=['GET'])
def search_meta():
    # Parsear los parámetros de la consulta
    title = request.args.get('title', '').strip()
    author = request.args.get('author', '').strip()  # Nuevo parámetro de autor
    year = request.args.get('year', '').strip()
    month = request.args.get('month', '').strip()
    day = request.args.get('day', '').strip()
    language = request.args.get('language', '').strip()

    # Crear un diccionario con los filtros
    filters = {
        'title': title,
        'author': author,
        'year': year,
        'month': month,
        'day': day,
        'language': language
    }

    # Realizar la búsqueda con los filtros
    results = search_metadata(filters, metadata)
    return jsonify(results)


# Ruta para servir los libros
@app.route('/libros/<path:filename>')
def serve_book(filename):
    datalake_directory = os.path.join(os.getcwd(), 'Datalake', 'eventstore', 'Gutenbrg')  # Ajusta esta línea si es necesario
    try:
        return send_from_directory(datalake_directory, filename)
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404


# Iniciar la aplicación
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5002)