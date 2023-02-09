import os
from elasticsearch import Elasticsearch

def index_files(es, root_folder):
    for root, dirs, files in os.walk(root_folder):
        for file in files:
            file_path = os.path.join(root, file)
            with open(file_path, 'r') as f:
                file_content = f.read()
            es.index(index='files', doc_type='file', body={
                'path': file_path,
                'content': file_content
            })

def search_files(es, query):
    results = es.search(index='files', body={
        'query': {
            'match': {
                'content': query
            }
        }
    })
    return [hit['_source']['path'] for hit in results['hits']['hits']]

if __name__ == '__main__':
    es = Elasticsearch()
    folder = input("Enter the root folder path: ")
    index_files(es, folder)
    query = input("Enter the search query: ")
    results = search_files(es, query)
    for result in results:
        print(result)


## This script assumes that you have Elasticsearch installed and running on the same machine where this script is executed. You can install Elasticsearch using the instructions provided on their official website.
