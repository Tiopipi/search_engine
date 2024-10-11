import re
from collections import defaultdict
import spacy


nlp = spacy.load('es_core_news_sm')

#stop_words = set(stop_words_en + stop_words_es + stop_words_de + stop_words_it + stop_words_pr + stop_words_fr)


# Función para limpiar texto, eliminando signos de puntuación y pasando a minúsculas
def clean_text(text):
    text = re.sub(r'\W+', ' ', text).lower()
    words = text.split()
    # Filtrar stopwords
    return [word for word in words if word not in nlp]


# Función para construir el índice invertido a nivel de word (con posiciones)
def build_indice_invertido_con_posiciones(documentos):
    indice_invertido = defaultdict(lambda: defaultdict(list))

    for doc_id, text in documentos:
        words = clean_text(text).split()

        for posicion, word in enumerate(words):
            indice_invertido[word][doc_id].append(posicion)

    return indice_invertido


# Función para extraer metadatos desde el contenido del texto
def extraer_metadatos(texto):
    texto = re.sub(r'\[.*?\]', '', texto)

    metadatos = {}

    # Patrones para extraer metadatos en varios idiomas
    patrones_metadatos = {
        'title': r'(Title|Título|Titre|Titel|Titolo|Título)\s*:\s*(.+)',
        'author': r'(Author|Autor|Auteur|Verfasser|Autore|Contributor)\s*:\s*(.+)',
        'release_date': r'(Release date|Fecha de publicación|Date de publication|Veröffentlichungsdatum|Data di pubblicazione|Data de publicação)\s*:\s*(.+)',
        'language': r'(Language|Idioma|Langue|Sprache|Lingua|Língua)\s*:\s*(.+)',
        'credits': r'(Credits)\s*:\s*(.+)'
    }

    # Buscar cada metadato
    for clave, patron in patrones_metadatos.items():
        match = re.search(patron, texto, re.IGNORECASE)
        if match:
            metadatos[clave] = match.group(2).strip()

    return metadatos


# Función para extraer libros de un directorio, y buscar metadatos dentro del texto
def cargar_libros_de_directorio(directorio):
    documentos = []
    metadatos_libros = []

    for filename in os.listdir(directorio):
        if filename.endswith('.txt'):
            file_path = os.path.join(directorio, filename)
            with open(file_path, 'r', encoding='utf-8') as f:
                contenido = f.read()

                # Extraer metadatos del contenido del archivo
                metadatos = extraer_metadatos(contenido)

                # Buscar el comienzo del contenido del libro
                start_contenido = re.search(r'\*\*\* START OF .* \*\*\*', contenido)
                if start_contenido:
                    contenido_libro = contenido[start_contenido.end():].strip()
                    documentos.append((filename, contenido_libro))

                # Agregar nombre del archivo a los metadatos y archivo leido
                metadatos['document'] = filename
                metadatos_libros.append(metadatos)

    return documentos, metadatos_libros


# Función para exportar metadatos a un archivo CSV
def exportar_metadatos_a_csv(metadatos, output_file):
    keys = metadatos[0].keys()
    with open(output_file, 'w', newline='', encoding='utf-8') as output_csv:
        dict_writer = csv.DictWriter(output_csv, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(metadatos)


# Función para exportar índice invertido a un archivo CSV
def exportar_indice_invertido_a_csv(indice_invertido, output_file):
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Palabra', 'Documento', 'Posiciones'])

        for word, docs in indice_invertido.items():
            for doc_id, posiciones in docs.items():
                writer.writerow([word, doc_id, ','.join(map(str, posiciones))])


# Ejemplo de documentos
documentos = [
    ("001", "the car is nice a"),
    ("002", "that car is mine"),
    ("003", "the car is the best")
]

# Construcción del índice invertido con posiciones
indice_invertido = build_indice_invertido_con_posiciones(documentos)

# Imprimir el índice invertido con posiciones
imprimir_indice_invertido_con_posiciones(indice_invertido)


