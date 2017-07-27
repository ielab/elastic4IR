import json
from pprint import pprint

from elasticsearch import Elasticsearch

es = Elasticsearch(urls='localhost', port=9200)

query_string = {
    'query': {
        'query_string': {
            'query': 'Searching',
            'fields': ['title^2','summary^1']
        }
    }
}

res = es.search(index='book', doc_type='chapter', body=query_string)

# pprint(res)
print(json.dumps(res,  indent=4))
