# Indexing Aquaint (used in TREC HARD 2005)
This repository describes how to index Aquaint corpus using Elasticsearch 5.x.x.
The index will have two fields: title and body.
Each field will have its own custom simmilarity definition to enable similarity tuning.

Pre-processing applied to both fields including:
* lowercasing
* removing stop words based on terrier stop words list
* steeming using porter stemer

## Pre-requisite
* Elasticsearch 5.x.x
* Python 3
* Elasticsearch python api. can be found from [here](https://elasticsearch-py.readthedocs.io/en/master/)
* Aquaint corpus files

## Preparing the Elasticsearch
Since the terrier stop words list is not included in Elasticsearch 5.1.1,
we need need to make sure that the terrier-stop.txt file is available in /config/stopwords folder within the ElasticSearch folder.


## Indexing using Python
Lets move to python. First, we need to import the necessary libaries:
* gzip: to unzip Aquaint collection files
* time: to measure running time
* glob: to traverse all Aquaint collection files
* re: regular experession to search unwanted phrase (e.g., special characters)
* sys: to measure size of bulk package variable
* elasticsearch: to work with Elasticsearch
* etree: Aquaint files are in XML, so we need this library to work with XML in python

```python
import gzip
import time
import glob
import re
import sys
from elasticsearch import Elasticsearch
import xml.etree.cElementTree as etree
```

specify location of the Aquaint files.
```
docPath = "/Volumes/Data/Phd/Data/aquaint_docs/"
```

Open connection to Elasticsearch
```
es = Elasticsearch(urls='http://localhost', port=9200, timeout=600)
```

Specify bulk size and max documents in a bulk. For faster indexing, we will index documents in bulks.
```
bulk_size = 4000
bulk_count = 1000
```

Define index name and document type for the aquaint index:
```
indexName = "aquaint_all"
docType = "aquaint"
```

Construct the index settings and mappings. Variable definition:
* "number_of_shards": 1 --> all documents will be indexed in one shard (i.e. no partitions)
* "number_of_replicas": 0 --> no replica (i.e. no back up index)
* "my_english" --> custom analyzer telling the ES to use "standard" english tokenizer,
lowercase all characters, remove stop words based on custom "terrier_stopwords",
stem using porter stemer.
* "terrier_stopwors" --> custom stopwords definition based on the stopwords/terrier-stop.txt file






```
request_body = {
    "settings": {
      "number_of_shards": 1,
      "number_of_replicas": 0,
      "analysis": {
        "analyzer": {
            "my_english": {
                "tokenizer": "standard",
                "filter": ["lowercase", "terrier_stopwords", "porter_stem"]
            }
        },
        "filter": {
          "terrier_stopwords": {
              "type": "stop",
              "stopwords_path": "stopwords/terrier-stop.txt"
          }
        }
      },
      "similarity": {
        "sim_title": {
            "type": "BM25",
            "b": 0.75,
            "k1": 1.2
        },
        "sim_body": {
            "type": "BM25",
            "b": 0.75,
            "k1": 1.2
        }
      }
    },
    "mappings": {
      docType: {
        "_source": {
            "enabled": False
            },
        "properties": {
            "title": {
                 "type": "text",
                 "similarity": "sim_title",
                 "analyzer": "my_english",
                 "fields": {
                    "length": {
                        "type": "token_count",
                        "store": "yes",
                        "analyzer": "whitespace"
                    }
                 }
            },
            "body": {
                "type": "text",
                "similarity": "sim_body",
                "analyzer": "my_english",
                "fields": {
                    "length": {
                        "type": "token_count",
                        "store": "yes",
                        "analyzer": "whitespace"
                    }
                }
            }
        }
       }
    }
}
```
