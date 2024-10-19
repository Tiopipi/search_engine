import subprocess
import threading
import time


def run_crawler():
    print("Running the Crawler...")
    try:
        subprocess.run(["python", "Crawler/crawler.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running crawler: {e}")


def run_indexer():
    while True:
        print("Running the Indexer...")
        try:
            subprocess.run(["python", "Indexer/tree_indexer.py"], check=True)
            subprocess.run(["python", "Indexer/metadata_indexer.py"], check=True)
            subprocess.run(["python", "Indexer/unique_json_indexer.py"], check=True)
            print("Indexer completed. Waiting for 30 minutes before the next run...")
        except subprocess.CalledProcessError as e:
            print(f"Error running indexer: {e}")

        time.sleep(1800)


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
    query_engine_json_thread = threading.Thread(target=run_query_engine_unique_json)
    query_engine_tree_thread = threading.Thread(target=run_query_engine_tree)

    query_engine_json_thread.start()
    query_engine_tree_thread.start()

    query_engine_json_thread.join()
    query_engine_tree_thread.join()


def main():
    crawler_thread = threading.Thread(target=run_crawler)
    crawler_thread.start()

    time.sleep(30)
    indexer_thread = threading.Thread(target=run_indexer)
    indexer_thread.start()

    print("Waiting for 20 seconds before running the query engine...")
    time.sleep(20)

    run_query_engine()
    crawler_thread.join()


if __name__ == "__main__":
    main()
