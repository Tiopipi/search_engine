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

    # Formatear el índice invertido para el retorno
    formatted_inverted_index = {}
    for word, (doc_ids, positions, frequencies) in inverted_index.items():
        formatted_inverted_index[word] = [doc_ids, positions, frequencies]

    return formatted_inverted_index




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


def export_inverted_index_to_json_by_letter(inverted_index, base_directory):
    letter_data = {}

    for word, (doc_ids, positions, frequencies) in inverted_index.items():
        first_letter = re.sub(r'[^a-z0-9áéíóúàèìòùäëïöüâêîôûçñ]', '', word[0].lower())

        if not first_letter:
            continue

        if first_letter not in letter_data:
            letter_data[first_letter] = {}

        if word not in letter_data[first_letter]:
            letter_data[first_letter][word] = {}

        for i, doc_id in enumerate(doc_ids):
            book_name = doc_id

            # Reemplazar el contenido en lugar de añadir
            letter_data[first_letter][word][book_name] = {
                "positions": positions[i],
                "frequency": frequencies[i]
            }

    for first_letter, words in letter_data.items():
        letter_directory = os.path.join(base_directory, first_letter)
        if not os.path.exists(letter_directory):
            os.makedirs(letter_directory)

        output_file = os.path.join(letter_directory, f'{first_letter}_words.json')

        # Reemplazar completamente el archivo con el nuevo contenido
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(words, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":

    books_directory = 'Datalake/eventstore/Gutenbrg'

    documents = load_books_from_directory(books_directory)

    inverted_index = build_inverted_index_with_positions(documents)

    INVERTED_INDEX_TREE_STRUCTURE_REPOSITORY = 'Datamarts/Inverted Index/Tree Data Structure'

    if not os.path.exists(INVERTED_INDEX_TREE_STRUCTURE_REPOSITORY):
        os.makedirs(INVERTED_INDEX_TREE_STRUCTURE_REPOSITORY)

    export_inverted_index_to_json_by_letter(inverted_index, INVERTED_INDEX_TREE_STRUCTURE_REPOSITORY)
