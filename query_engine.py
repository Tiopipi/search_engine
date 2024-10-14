from flask import Flask, request, jsonify
import csv
import ast
import re
app = Flask(__name__)

def load_inverted_index(file_path):
    inverted_index = {}

    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # Omitir el encabezado

        for row in reader:
            word = row[0]
            # Procesar doc_ids manteniendo comas en los nombres
            doc_ids_str = row[1].strip('"').strip('[]')
            doc_ids = [doc.strip() for doc in doc_ids_str.split(', ')]  # Separar por coma y espacio
            positions_str = "[" + row[2].strip('"').strip('[]') + "]"
            frequencies_str = row[3].strip('"').strip('[]')

            # Procesar posiciones
            positions_list = []
            if positions_str:  # Verificar que la cadena no esté vacía
                # Separar por las listas anidadas
                positions_groups = positions_str.split('],[')
                for group in positions_groups:
                    # Limpiar caracteres no deseados y dividir
                    adjusted_group = f"[{group}]"
                    positions_list = ast.literal_eval(adjusted_group)


            # Procesar frecuencias
            frequency_list = list(map(int, frequencies_str.split(','))) if frequencies_str else []

            # Crear el índice invertido
            if word not in inverted_index:
                inverted_index[word] = {}

            # Asignar posiciones y frecuencias al documento correspondiente
            for i, doc_id in enumerate(doc_ids):
                inverted_index[word][doc_id] = (
                    positions_list[i] if i < len(positions_list) else [],
                    frequency_list[i] if i < len(frequency_list) else 0
                )

    return inverted_index


def load_record_level(file_path):
    record_level = {}
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # Omitir el encabezado

        for row in reader:
            word = row[0]
            # Procesar doc_ids manteniendo comas en los nombres
            doc_ids_str = row[1].strip('"').strip('[]')
            doc_ids = [doc.strip() for doc in doc_ids_str.split(', ')]  # Separar por coma y espacio

            # Crear el índice invertido solo con la palabra y el documento
            if word not in record_level:
                record_level[word] = set()  # Usamos un set para evitar duplicados

            # Añadir los documentos correspondientes
            for doc_id in doc_ids:
                record_level[word].add(doc_id)

    return record_level





# Cargar los metadatos desde un archivo CSV
def load_metadata(file_path):
    metadata = []
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            metadata.append(row)
    return metadata


# Función para buscar términos en el índice invertido
def search_inverted_index(query, inverted_index):
    query_terms = query.lower().split()
    results = {}

    for term in query_terms:
        if term in inverted_index:
            # Inicializar el diccionario para la palabra si no existe
            if term not in results:
                results[term] = {}

            for doc_id, (positions, frequency) in inverted_index[term].items():
                results[term][doc_id] = {
                    "frequency": frequency,
                    "positions": positions
                }

    return results

def search_record_level(query, record_level):
    query_terms = query.lower().split()
    results = {}

    for term in query_terms:
        if term in record_level:
            # Asignar la lista de libros al término
            results[term] = list(record_level[term])  # Convertir a lista si es necesario

    return results



# Función para buscar en los metadatos
def search_metadata(query, metadata):
    query_lower = query.lower()
    results = []

    for entry in metadata:
        # Buscar en los campos de metadatos
        for key, value in entry.items():
            if query_lower in value.lower():
                results.append(entry)
                break  # Si ya se encontró en un campo, no es necesario buscar en los demás

    return results


# Cargar el índice invertido y los metadatos
inverted_index = load_inverted_index('Datamarts/Inverted Index/word_level.csv')
metadata = load_metadata('Datamarts/Metadata Database/book_metadata.csv')
record_level = load_record_level('Datamarts/Inverted Index/record_level.csv')


# Ruta para realizar la búsqueda en el índice invertido
@app.route('/search/word_level', methods=['GET'])
def search_inverted():
    query = request.args.get('query', '').strip()
    if not query:
        return jsonify({"error": "No search query provided"}), 400

    # Buscar en el índice invertido
    results = search_inverted_index(query, inverted_index)

    # Devolver los resultados en formato JSON
    return jsonify(results)


# Ruta para realizar la búsqueda en los metadatos
@app.route('/search/metadata', methods=['GET'])
def search_meta():
    query = request.args.get('query', '').strip()
    if not query:
        return jsonify({"error": "No search query provided"}), 400

    # Buscar en los metadatos
    results = search_metadata(query, metadata)

    # Devolver los resultados en formato JSON
    return jsonify(results)


@app.route('/search/record_level', methods=['GET'])
def search_record():
    query = request.args.get('query', '').strip()
    if not query:
        return jsonify({"error": "No search query provided"}), 400

    # Buscar en los metadatos
    results = search_record_level(query, record_level)

    # Devolver los resultados en formato JSON
    return jsonify(results)

# Iniciar la aplicación
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
