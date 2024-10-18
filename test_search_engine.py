import pytest

from Indexer.tree_indexer import build_inverted_index_with_positions as build_inverted_index_with_positions_tree
from Indexer.tree_indexer import load_books_from_directory as load_books_from_directory_tree
from Indexer.tree_indexer import export_inverted_index_to_json_by_letter
from Indexer.unique_json_indexer import build_inverted_index_with_positions as build_inverted_index_with_positions_json
from Indexer.unique_json_indexer import load_books_from_directory as load_books_from_directory_json
from Indexer.unique_json_indexer import export_inverted_index_json
from Query_Engine.query_engine_tree_data_structure import app as app_tree
from Query_Engine.query_engine_unique_json import app as app_json



@pytest.fixture
def client_json():
    with app_json.test_client() as client_json:
        yield client_json


@pytest.fixture
def client_tree():
    with app_tree.test_client() as client_tree:
        yield client_tree


@pytest.mark.benchmark
def test_execution_time_export_json_inverted_index(benchmark):
    books_directory = 'Datalake/eventstore/Gutenbrg'
    documents = load_books_from_directory_json(books_directory)
    inveted_index = build_inverted_index_with_positions_json(documents)
    directory = 'Datamarts/Inverted Index/word_level.json'
    benchmark.pedantic(export_inverted_index_json, args=(inveted_index, directory,), iterations=1, rounds=1)


@pytest.mark.benchmark
def test_execution_time_export_tree_structure_inverted_index(benchmark):
    books_directory = 'Datalake/eventstore/Gutenbrg'
    documents = load_books_from_directory_tree(books_directory)
    inverted_index = build_inverted_index_with_positions_tree(documents)
    directory = 'Datamarts/Inverted Index/Tree Data Structure'

    benchmark.pedantic(export_inverted_index_to_json_by_letter, args=(inverted_index, directory,), iterations=1, rounds=1)


query = "African"


@pytest.mark.benchmark(group="search_unique_json_inverted")
def test_search_unique_json_data_structure(client_json, benchmark):
    def search_request():
        response = client_json.get(f'/search/word_level?query={query}')
        assert response.status_code == 200

    benchmark.pedantic(search_request, iterations=1, rounds=1)


@pytest.mark.benchmark(group="search_tree_inverted")
def test_search_tree_data_structure(client_tree, benchmark):
    def search_request():
        response = client_tree.get(f'/search/word_level?query={query}')
        assert response.status_code == 200

    benchmark.pedantic(search_request, iterations=1, rounds=1)
