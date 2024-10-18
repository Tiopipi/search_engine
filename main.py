import subprocess
import threading
import time


def run_crawler():
    print("Running the Crawler...")
    try:
        subprocess.run(["python", "Crawler/crawler.py"], check=True)  # Cambia 'crawler.py' por la ruta correcta de tu archivo Crawler
    except subprocess.CalledProcessError as e:
        print(f"Error running crawler: {e}")


def run_indexer():
    while True:
        print("Running the Indexer...")
        try:
            subprocess.run(["python", "Indexer/tree_indexer.py"], check=True)  # Cambia 'indexer.py' por la ruta correcta de tu archivo Indexer
            subprocess.run(["python", "Indexer/metadata_indexer.py"], check=True)  # Cambia 'indexer.py' por la ruta correcta de tu archivo Indexer
            subprocess.run(["python", "Indexer/unique_json_indexer.py"], check=True)  # Cambia 'indexer.py' por la ruta correcta de tu archivo Indexer
            print("Indexer completed. Waiting for 10 minutes before the next run...")
        except subprocess.CalledProcessError as e:
            print(f"Error running indexer: {e}")

        time.sleep(600)


def run_query_engine_unique_json():
    print("Running Query Engine: Unique JSON...")
    try:
        subprocess.run(["python", "Query_Engine/query_engine_unique_json.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running query_engine_unique_json: {e}")


def run_query_engine_tree():
    print("Running Query Engine: Tree Data Structure...")
    try:
        subprocess.run(["python", "Query_Engine/query_engine_tree_data_structure.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running query_engine_tree_data_structure: {e}")


def run_query_engine():
    # Create two threads for running the two query engines in parallel
    query_engine_json_thread = threading.Thread(target=run_query_engine_unique_json)
    query_engine_tree_thread = threading.Thread(target=run_query_engine_tree)

    # Start both threads
    query_engine_json_thread.start()
    query_engine_tree_thread.start()

    # Wait for both threads to complete
    query_engine_json_thread.join()
    query_engine_tree_thread.join()


def main():
    crawler_thread = threading.Thread(target=run_crawler)
    crawler_thread.start()

    time.sleep(30)
    indexer_thread = threading.Thread(target=run_indexer)
    indexer_thread.start()

    print("Waiting for 20 seconds before running the query engine...")
    time.sleep(10)

    run_query_engine()
    crawler_thread.join()


if __name__ == "__main__":
    main()
