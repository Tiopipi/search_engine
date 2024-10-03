import os
import requests
from bs4 import BeautifulSoup
import schedule
import time

# URL base de Gutenberg
BASE_URL = "https://www.gutenberg.org/"

# Directorio para almacenar los libros descargados
REPOSITORIO_DOCUMENTOS = "document_repository"

# Crear el repositorio si no existe
if not os.path.exists(REPOSITORIO_DOCUMENTOS):
    os.makedirs(REPOSITORIO_DOCUMENTOS)


# Función para descargar un libro y guardarlo en el repositorio
def descargar_libro(url_libro, nombre_archivo):
    try:
        response = requests.get(url_libro)
        if response.status_code == 200:
            ruta_archivo = os.path.join(REPOSITORIO_DOCUMENTOS, nombre_archivo)
            with open(ruta_archivo, 'wb') as file:
                file.write(response.content)
            print(f"Libro descargado y guardado en: {ruta_archivo}")
        else:
            print(f"Error al descargar {url_libro}: {response.status_code}")
    except Exception as e:
        print(f"Excepción al descargar el libro: {e}")


# Función para obtener enlaces de libros desde una página de Gutenberg
def obtener_enlaces_libros(url_categoria):
    try:
        response = requests.get(url_categoria)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Buscar enlaces que contienen libros en formato texto (txt)
        enlaces_libros = []
        for enlace in soup.find_all('a', href=True):
            href = enlace['href']
            if href.endswith('.txt'):
                enlaces_libros.append(BASE_URL + href)
        return enlaces_libros
    except Exception as e:
        print(f"Error al obtener los enlaces de libros: {e}")
        return []


# Función principal del crawler
def crawler():
    print("Iniciando el crawler...")

    # Ejemplo: Página de libros de ficción
    url_categoria = "https://www.gutenberg.org/ebooks/bookshelf/22"

    # Obtener enlaces de libros
    enlaces_libros = obtener_enlaces_libros(url_categoria)

    # Descargar los primeros 5 libros como ejemplo
    for i, url_libro in enumerate(enlaces_libros[:5]):
        nombre_archivo = f"libro_{i + 1}.txt"
        descargar_libro(url_libro, nombre_archivo)


# Programar el crawler para que corra cada día (puedes ajustar la frecuencia)
schedule.every().day.at("10:00").do(crawler)

# Mantener el crawler corriendo periódicamente
while True:
    schedule.run_pending()
    time.sleep(60)
