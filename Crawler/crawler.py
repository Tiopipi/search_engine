import os
import requests
from bs4 import BeautifulSoup
import logging
from concurrent.futures import ThreadPoolExecutor
import time



global_counter = 0


def download_book(url_book, file_name):
    try:
        response = requests.get(url_book)
        response.raise_for_status()
        file_path = os.path.join(REPOSITORY_DOCUMENTS, file_name)
        with open(file_path, 'wb') as file:
            file.write(response.content)
        logging.info(f"Book downloaded and saved at: {file_path}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error downloading {url_book}: {e}")


def get_txt_link(book_page_url):
    try:
        book_id = book_page_url.split('/')[-1]
        txt_url = f"https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}.txt"

        response = requests.head(txt_url)
        if response.status_code == 200:
            book_page_response = requests.get(book_page_url)
            book_page_soup = BeautifulSoup(book_page_response.text, 'html.parser')
            title = book_page_soup.find('h1').text.strip()
            return txt_url, title
        else:
            logging.info(f"No text link found for {book_page_url}")
            return None, None
    except requests.exceptions.RequestException as e:
        logging.error(f"Error getting text link: {e}")
        return None, None


def get_book_page_links(category_url):
    book_page_links = []
    current_page = category_url

    while current_page:
        try:
            response = requests.get(current_page)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            for link in soup.find_all('a', href=True):
                href = link['href']

                if href.startswith("/ebooks/") and href[8:].isdigit():
                    full_url = BASE_URL + href
                    book_page_links.append(full_url)

            next_button = soup.find('a', text='Next')
            if next_button and 'href' in next_button.attrs:
                current_page = BASE_URL + next_button['href']
            else:
                current_page = None

        except requests.exceptions.RequestException as e:
            logging.error(f"Error getting book pages: {e}")
            break

    logging.info(f"Links to book pages found: {len(book_page_links)}")
    return book_page_links


def run_crawler(category_url, num_books):
    global global_counter
    logging.info("Starting the crawler...")

    book_page_links = get_book_page_links(category_url)

    if book_page_links:
        logging.info(f"{len(book_page_links)} book pages found.")
        total_books_downloaded = 0
        block_number = 1

        while total_books_downloaded < len(book_page_links):
            logging.info(f"Starting download of block {block_number}.")
            books_downloaded_in_block = 0

            with ThreadPoolExecutor(max_workers=5) as executor:
                for i in range(total_books_downloaded, total_books_downloaded + num_books):
                    if i >= len(book_page_links):
                        break

                    book_page_url = book_page_links[i]
                    txt_link, title = get_txt_link(book_page_url)
                    if txt_link:
                        global_counter += 1

                        formatted_title = title.replace(' ', '_').replace(':', '').replace('/', '_')  # Format the title
                        file_name = f"{formatted_title}_{global_counter}.txt"
                        executor.submit(download_book, txt_link, file_name)
                        books_downloaded_in_block += 1

            total_books_downloaded += books_downloaded_in_block
            logging.info(f"Downloaded {books_downloaded_in_block} books in block {block_number}.")
            block_number += 1

            if total_books_downloaded < len(book_page_links):
                logging.info("Waiting 10 minutes before continuing with the next block of books...")
                time.sleep(600)
    else:
        logging.info("No book pages found to process.")


if __name__ == "__main__":
    logging.basicConfig(filename='crawler.log', level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')

    BASE_URL = "https://www.gutenberg.org/"

    REPOSITORY_DOCUMENTS = "Datalake/eventstore/Gutenbrg"

    if not os.path.exists(REPOSITORY_DOCUMENTS):
        os.makedirs(REPOSITORY_DOCUMENTS)

    bookshelf_num = 5
    max_bookshelf_num = 487
    while bookshelf_num <= max_bookshelf_num:
        category_url = f"https://www.gutenberg.org/ebooks/bookshelf/{bookshelf_num}"
        run_crawler(category_url, num_books=10)
        bookshelf_num += 1


