import re
import os
import csv
from collections import defaultdict
import spacy

# Load spaCy models for natural language processing
nlp_en = spacy.load('en_core_web_sm')
nlp_es = spacy.load('es_core_news_sm')
nlp_fr = spacy.load('fr_core_news_sm')
nlp_it = spacy.load('it_core_news_sm')
nlp_de = spacy.load('de_core_news_sm')
nlp_pt = spacy.load('pt_core_news_sm')

# SpaCy stopwords
stop_words = set()
stop_words = stop_words.union(nlp_en.Defaults.stop_words)
stop_words = stop_words.union(nlp_es.Defaults.stop_words)
stop_words = stop_words.union(nlp_fr.Defaults.stop_words)
stop_words = stop_words.union(nlp_it.Defaults.stop_words)
stop_words = stop_words.union(nlp_de.Defaults.stop_words)
stop_words = stop_words.union(nlp_pt.Defaults.stop_words)


# Function to clean text by removing punctuation and converting to lowercase
def clean_text(text):
    text = re.sub(r'\W+', ' ', text).lower()
    words = text.split()
    # Filter stopwords
    return [word for word in words if word not in stop_words]


# Function to build an inverted index with positions and frequency
def build_inverted_index_with_positions(documents):
    inverted_index = {}

    for doc_id, text in documents:
        words = clean_text(text)
        word_count = defaultdict(int)  # To count occurrences of each word

        for position, word in enumerate(words):
            word_count[word] += 1  # Count occurrences

            if word not in inverted_index:
                inverted_index[word] = [[], [], []]  # [document_ids, positions, frequencies]

            # Add document ID if not already present
            if doc_id not in inverted_index[word][0]:
                inverted_index[word][0].append(doc_id)
                inverted_index[word][1].append([])  # Create an empty position list for this doc_id
                inverted_index[word][2].append(0)  # Initialize frequency count for this doc_id

            # Add the position corresponding to the word
            doc_index = inverted_index[word][0].index(doc_id)
            inverted_index[word][1][doc_index].append(position)
            inverted_index[word][2][doc_index] += 1  # Increment frequency count

    # Format the output as required
    formatted_inverted_index = {}
    for word, (doc_ids, positions, frequencies) in inverted_index.items():
        formatted_inverted_index[word] = [doc_ids, positions, frequencies]

    return formatted_inverted_index


def build_record_level_inverted_index(documents):
    record_level_inverted_index = {}

    for doc_id, text in documents:
        words = clean_text(text)

        for word in words:
            if word not in record_level_inverted_index:
                record_level_inverted_index[word] = set()  # Usamos un set para evitar duplicados

            # Agregar el documento al conjunto
            record_level_inverted_index[word].add(doc_id)

    # Convertir el set en lista para exportar fácilmente a CSV
    for word in record_level_inverted_index:
        record_level_inverted_index[word] = list(record_level_inverted_index[word])

    return record_level_inverted_index


# Function to extract metadata from text content
def extract_metadata(text):
    text = re.sub(r'\[.*?]', '', text)

    metadata = {}

    # Patterns to extract metadata in various languages
    metadata_patterns = {
        'title': r'(Title|Título|Titre|Titel|Titolo|Título)\s*:\s*(.+)',
        'author': r'(Author|Autor|Auteur|Verfasser|Autore|Contributor)\s*:\s*(.+)',
        'release_date': r'(Release date|Fecha de publicación|Date de publication|Veröffentlichungsdatum|Data di \
        pubblicazione|Data de publicação)\s*:\s*(.+)',
        'language': r'(Language|Idioma|Langue|Sprache|Lingua|Língua)\s*:\s*(.+)',
        'credits': r'(Credits)\s*:\s*(.+)'
    }

    # Search for each metadata
    for key, pattern in metadata_patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            metadata[key] = match.group(2).strip()

    return metadata


# Function to load books from a directory and extract metadata from text
def load_books_from_directory(directory):
    documents = []
    book_metadata = []

    for filename in os.listdir(directory):
        if filename.endswith('.txt'):
            file_path = os.path.join(directory, filename)
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

                # Extract metadata from file content
                metadata = extract_metadata(content)

                # Search for the start of the book content
                start_content = re.search(r'\*\*\* START OF .* \*\*\*', content)
                if start_content:
                    book_content = content[start_content.end():].strip()
                    documents.append((filename, book_content))

                # Add filename to metadata and read file
                metadata['document'] = filename
                book_metadata.append(metadata)

    return documents, book_metadata


# Function to export metadata to a CSV file
def export_metadata_to_csv(metadata, output_file):
    keys = metadata[0].keys()
    with open(output_file, 'w', newline='', encoding='utf-8') as output_csv:
        dict_writer = csv.DictWriter(output_csv, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(metadata)


# Function to export the inverted index to a CSV file with frequencies
def export_inverted_index_to_csv(inverted_index, output_file):
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Word', 'Documents', 'Positions', 'Frequencies'])

        for word, (doc_ids, positions, frequencies) in inverted_index.items():
            # Format the string of documents
            doc_ids_str = '[' + ', '.join(f'{doc_id}' for doc_id in doc_ids) + ']'  # Format: ["001", "002"]

            # Format the positions
            positions_str = '[' + ', '.join(f'[{",".join(map(str, pos))}]' for pos in positions) + ']'  # Format: [[pos1, pos2], [pos3, pos4]]

            # Format the frequencies
            frequencies_str = '[' + ', '.join(map(str, frequencies)) + ']'  # Format: [count1, count2]

            # Write the row in the CSV
            writer.writerow([word, doc_ids_str, positions_str, frequencies_str])


def export_record_level_inverted_index_to_csv(record_level_inverted_index, output_file):
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Word', 'Documents'])

        for word, doc_ids in record_level_inverted_index.items():
            doc_ids_str = '[' + ', '.join(f'{doc_id}' for doc_id in doc_ids) + ']'  # Formato: ["001", "002"]
            writer.writerow([word, doc_ids_str])


# Directory where the books are stored
books_directory = 'Datalake/eventstore/Gutenbrg'

# Load documents and metadata from the directory
documents, metadata = load_books_from_directory(books_directory)

# Build the inverted index with positions
inverted_index = build_inverted_index_with_positions(documents)
record_level_inverted_index = build_record_level_inverted_index(documents)

# Define output file paths for the CSV exports
INVERTED_INDEX_WORD_LEVEL_REPOSITORY = 'Datamarts/Inverted Index/word_level.csv'
INVERTED_INDEX_RECORD_LEVEL_REPOSITORY = 'Datamarts/Inverted Index/record_level.csv'
METADATA_REPOSITORY = 'Datamarts/Metadata Database/book_metadata.csv'

# Create directories if they don't exist
if not os.path.exists('Datamarts/Inverted Index'):
    os.makedirs('Datamarts/Inverted Index')


if not os.path.exists('Datamarts/Metadata Database'):
    os.makedirs('Datamarts/Metadata Database')

# Export metadata to a CSV file
export_metadata_to_csv(metadata, METADATA_REPOSITORY)

# Export the inverted index to a CSV file
export_inverted_index_to_csv(inverted_index, INVERTED_INDEX_WORD_LEVEL_REPOSITORY)

export_record_level_inverted_index_to_csv(record_level_inverted_index, INVERTED_INDEX_RECORD_LEVEL_REPOSITORY)