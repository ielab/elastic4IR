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
from lxml import etree
```

specify location of the Aquaint files.
```python
docPath = "/Volumes/Data/Phd/Data/aquaint_docs/"
```

Open connection to Elasticsearch
```python
es = Elasticsearch(urls='http://localhost', port=9200, timeout=600)
```

Specify bulk size and max documents in a bulk. For faster indexing, we will index documents in bulks.
```python
bulk_size = 4000
bulk_count = 1000
```

Define index name and document type for the aquaint index:
```python
indexName = "aquaint_all"
docType = "aquaint"
```

Construct the index settings and mappings. Variable definition:
* "number_of_shards": 1 --> all documents will be indexed in one shard (i.e. no partitions)
* "number_of_replicas": 0 --> no replica (i.e. no back up index)
* "my_english" --> custom analyzer telling the ES to use "standard" english tokenizer,
lowercase all characters, remove stop words based on custom "terrier_stopwords",
stem using porter stemer.
* "terrier_stopwords" --> custom stopwords definition based on the stopwords/terrier-stop.txt file
* "similarity" --> custom similarity object for each field
* "_source" --> specify to store or not to store the document text in the index (False means not storing the document text)
* "properties" --> field definition. utilize the defined custom similarity and analyzer.

```python
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
                 "analyzer": "my_english"
            },
            "body": {
                "type": "text",
                "similarity": "sim_body",
                "analyzer": "my_english"
            }
        }
      }
    }
}
```

Create index based on the specified settings:
```python
if not es.indices.exists(indexName):
    print ("creating ", indexName, " index, start at ", startTime)
    res = es.indices.create(index=indexName, body=request_body)
    print(" response: '%s'" % res)
```

Traverse all folders, extract the gz files, then index in bulk
```python
# traverse through all folders
sourceFolders = glob.glob(docPath + "/*")
for sourceFold in sourceFolders:
    print("Processing Source: {}".format(sourceFold))
    yearFolders = glob.glob(sourceFold + "/*")
    for yearFold in yearFolders:
        print("Processing Year folder: {}".format(yearFold))
        for f in glob.glob(yearFold + "/*"):
            print("Processing file: {}".format(f))
            with gzip.open(f, mode='rb') as gzf:
                temp = gzf.read()

                temp = re.sub(r'&\w{2,6};', '', str(temp))
                temp = temp.replace("<P>", " ").replace("</P>", " ").replace("\n", " ").replace("\t", " ")
                content = "<ROOT>" + temp + "</ROOT>"
                try:
                    root = etree.fromstring(content)

                    for doc in root.findall('DOC'):
                        docNo = "-"
                        headline = "-"
                        text = "-"

                        docNo = doc.find('DOCNO').text.strip()
                        body = doc.find('BODY')

                        # check if there is any text within the headline tag
                        if body.find('HEADLINE') is not None:
                            headline = body.find('HEADLINE').text

                        # check if there is any text within the body tag
                        if body.find('TEXT') is not None:
                            text = body.find('TEXT').text

                        # prepare bulk content
                        content = headline + text
                        bulk_meta = {
                            "index": {
                                "_index": indexName,
                                "_type": docType,
                                "_id": docNo
                            }
                        }

                        bulk_content = {
                            'title': headline,
                            'body': text
                        }

                        bulk_data.append(bulk_meta)
                        bulk_data.append(bulk_content)
                        totalSize += (sys.getsizeof(content) / 1024)  # convert from bytes to KiloBytes

                        i += 1
                        # check to see if the bulk has hit the max size or max number of files
                        if totalSize > bulk_size or i % bulk_count == 0:
                            res = es.bulk(index=indexName, doc_type=docType, body=bulk_data, refresh=False)
                            bulk_data = []
                            print("{0} Completed, ({1} seconds), current bulk size: {2}".format(str(i),
                                                                                                time.time() - lapTime,
                                                                                                totalSize))
                            lapTime = time.time()
                            totalSize = 0
                except:
                    print("Error in Doc No: {}".format(docNo))
                    raise

# if there is data in the bulk variable then load it.
if len(bulk_data) > 0:
    res = es.bulk(index=indexName, doc_type=docType, body=bulk_data, refresh=False)
    bulk_data = []
    print ("{0} Remainder Completed, ({1} seconds), current bulk size: {2}".format(str(i), time.time() - lapTime,
                                                                            totalSize))
```