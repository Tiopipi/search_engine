import json
import re
import os
from collections import defaultdict
import spacy

nlp_en = spacy.load('en_core_web_sm')
nlp_es = spacy.load('es_core_news_sm')
nlp_fr = spacy.load('fr_core_news_sm')
nlp_it = spacy.load('it_core_news_sm')
nlp_de = spacy.load('de_core_news_sm')
nlp_pt = spacy.load('pt_core_news_sm')

stop_words = set()
stop_words = stop_words.union(nlp_en.Defaults.stop_words)
stop_words = stop_words.union(nlp_es.Defaults.stop_words)
stop_words = stop_words.union(nlp_fr.Defaults.stop_words)
stop_words = stop_words.union(nlp_it.Defaults.stop_words)
stop_words = stop_words.union(nlp_de.Defaults.stop_words)
stop_words = stop_words.union(nlp_pt.Defaults.stop_words)


def clean_text(text):
    text = re.sub(r'\W+', ' ', text).lower()
    words = text.split()
    return [word for word in words if word not in stop_words]


def build_inverted_index_with_positions(documents):
    inverted_index = {}

    for doc_id, text in documents:
        original_words = text.split()  # Texto original para encontrar las posiciones reales
        pos = 0  # Posición actual en el texto original

        # Mapeamos las palabras originales a sus posiciones, omitiendo las stop words para el índice
        for word in original_words:
            clean_word = re.sub(r'\W+', '', word).lower()  # Limpiar y normalizar la palabra
            is_stop_word = clean_word in stop_words  # Verificamos si es stop word

            if not is_stop_word and clean_word:  # Solo añadimos las no stop words al índice invertido
                if clean_word not in inverted_index:
                    inverted_index[clean_word] = [[], [], []]  # [document_ids, positions, frequencies]

                # Si el documento no está ya presente en el índice para esta palabra, lo añadimos
                if doc_id not in inverted_index[clean_word][0]:
                    inverted_index[clean_word][0].append(doc_id)
                    inverted_index[clean_word][1].append([])  # Lista vacía para las posiciones en este documento
                    inverted_index[clean_word][2].append(0)  # Inicializamos la frecuencia en 0

                doc_index = inverted_index[clean_word][0].index(doc_id)  # Encontrar la posición del doc_id
                inverted_index[clean_word][1][doc_index].append(pos)  # Añadir la posición
                inverted_index[clean_word][2][doc_index] += 1  # Aumentar la frecuencia en 1

            # Incrementamos la posición actual del texto original, incluso si es una stop word
            pos += 1

    return inverted_index


def load_books_from_directory(directory):
    documents = []

    for filename in os.listdir(directory):
        if filename.endswith('.txt'):
            file_path = os.path.join(directory, filename)
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

                start_content = re.search(r'\*\*\* START OF .* \*\*\*', content)
                if start_content:
                    book_content = content[start_content.end():].strip()
                    documents.append((filename, book_content))

    return documents


def export_inverted_index_json(inverted_index, directory):
    formatted_inverted_index = {}

    for word, (doc_ids, positions, frequencies) in inverted_index.items():
        formatted_inverted_index[word] = {}

        for i, doc_id in enumerate(doc_ids):
            formatted_inverted_index[word][doc_id] = {
                "positions": positions[i],
                "frequency": frequencies[i]
            }

    with open(directory, 'w', encoding='utf-8') as f:
        json.dump(formatted_inverted_index, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    books_directory = 'Datalake/eventstore/Gutenbrg'

    documents = load_books_from_directory(books_directory)

    inverted_index = build_inverted_index_with_positions(documents)

    INVERTED_INDEX_WORD_LEVEL_REPOSITORY = 'Datamarts/Inverted Index/word_level.json'

    if not os.path.exists('Datamarts/Inverted Index'):
        os.makedirs('Datamarts/Inverted Index')

    export_inverted_index_json(inverted_index, INVERTED_INDEX_WORD_LEVEL_REPOSITORY)

