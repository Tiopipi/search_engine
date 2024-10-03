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


# Función para imprimir el índice invertido con posiciones
def imprimir_indice_invertido_con_posiciones(indice_invertido):
    for word, docs in indice_invertido.items():
        print(f"Palabra '{word}' aparece en:")
        for doc_id, posiciones in docs.items():
            print(f"  Documento {doc_id}: posiciones {posiciones}")


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


