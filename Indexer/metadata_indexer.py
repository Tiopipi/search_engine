import os
import re
import csv


def extract_metadata(text):
    text = re.sub(r'\[.*?]', '', text)

    metadata = {}
    metadata_patterns = {
        'title': r'(Title|Título|Titre|Titel|Titolo|Título)\s*:\s*(.+)',
        'author': r'(Author|Autor|Auteur|Verfasser|Autore|Contributor)\s*:\s*(.+)',
        'release_date': r'(Release date|Fecha de publicación|Date de publication|Veröffentlichungsdatum|Data di pubblicazione|Data de publicação)\s*:\s*(.+)',
        'language': r'(Language|Idioma|Langue|Sprache|Lingua|Língua)\s*:\s*(.+)'
    }

    for key, pattern in metadata_patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            metadata[key] = match.group(2).strip()

    return metadata


def load_books_from_directory(directory):
    documents = []
    book_metadata = []

    for filename in os.listdir(directory):
        if filename.endswith('.txt'):
            file_path = os.path.join(directory, filename)
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

                metadata = extract_metadata(content)

                start_content = re.search(r'\*\*\* START OF .* \*\*\*', content)
                if start_content:
                    book_content = content[start_content.end():].strip()
                    documents.append((filename, book_content))

                metadata['document'] = filename
                book_metadata.append(metadata)

    return documents, book_metadata


def export_metadata_to_csv(metadata, output_file):
    keys = metadata[0].keys()
    with open(output_file, 'w', newline='', encoding='utf-8') as output_csv:
        dict_writer = csv.DictWriter(output_csv, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(metadata)


def process_metadata(books_directory, metadata_output_file):
    documents, metadata = load_books_from_directory(books_directory)
    export_metadata_to_csv(metadata, metadata_output_file)


if __name__ == "__main__":

    if not os.path.exists('Datamarts/Metadata Database'):
        os.makedirs('Datamarts/Metadata Database')
    books_directory = 'Datalake/eventstore/Gutenbrg'
    metadata_output_file = 'Datamarts/Metadata Database/book_metadata.csv'

    process_metadata(books_directory, metadata_output_file)
