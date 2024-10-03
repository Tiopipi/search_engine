import spacy
from collections import defaultdict
from langdetect import detect

# Cargar los modelos de lenguaje para cada idioma
nlp_models = {
    "es": spacy.load("es_core_news_sm"),  # Español
    "en": spacy.load("en_core_web_sm"),   # Inglés
    "fr": spacy.load("fr_core_news_sm"),   # Francés
    "de": spacy.load("de_core_news_sm"),   # Alemán
    "it": spacy.load("it_core_news_sm"),   # Italiano
    "pt": spacy.load("pt_core_news_sm"),    # Portugués
}

# Función para construir el índice invertido a nivel de palabra (con posiciones)
def build_indice_invertido_con_posiciones(documentos):
    indice_invertido = defaultdict(lambda: defaultdict(list))

    for doc_id, text in documentos:
        # Detectar el idioma del texto
        lang = detect(text)
        lang = lang if lang in nlp_models else "en"  # Asumir inglés si no está en los modelos

        # Procesar el texto con el modelo correspondiente al idioma
        doc = nlp_models[lang](text)

        for posicion, token in enumerate(doc):
            # Detectar sustantivos, verbos y adjetivos
            if token.pos_ in {"NOUN", "VERB", "ADJ"}:
                indice_invertido[token.text][doc_id].append(posicion)

    return indice_invertido

# Función para imprimir el índice invertido con posiciones
def imprimir_indice_invertido_con_posiciones(indice_invertido):
    for word, docs in indice_invertido.items():
        print(f"Palabra '{word}' aparece en:")
        for doc_id, posiciones in docs.items():
            print(f"  Documento {doc_id}: posiciones {posiciones}")

# Ejemplo de documentos en diferentes idiomas
documentos = [
    ("001", "El coche es bonito y rápido."),        # Español
    ("002", "That car is mine and is amazing."),    # Inglés
    ("003", "La voiture est la meilleure de toutes."), # Francés
    ("004", "Das Auto ist schnell und schön."),     # Alemán
    ("005", "L'auto è veloce e bella."),             # Italiano
    ("006", "O carro é rápido e bonito."),           # Portugués
]

# Construcción del índice invertido con posiciones
indice_invertido = build_indice_invertido_con_posiciones(documentos)

# Imprimir el índice invertido con posiciones
imprimir_indice_invertido_con_posiciones(indice_invertido)
