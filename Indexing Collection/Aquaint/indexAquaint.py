import gzip
import time
import glob
import re
import sys
from elasticsearch import Elasticsearch
from lxml import etree

docPath = "/Volumes/Data/Phd/Data/aquaint_docs/"

es = Elasticsearch(urls='http://localhost', port=9200, timeout=600)
bulk_size = 4000 #bulk limit in KiloBytes
bulk_count = 1000 #bulk limit in number of files

# Define index name and document type
indexName = "aquaint_all"
docType = "aquaint"


# Define index structure
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

startTime = time.time()
bulk_data = []
lapTime = time.time()
indexTime = time.time()

# Delete index if its already exist
if es.indices.exists(indexName):
    print("deleting '%s' index..." % indexName)
    res = es.indices.delete(index=indexName)
    print(" response: '%s'" % res)

# Create index
if not es.indices.exists(indexName):
    print ("creating ", indexName, " index, start at ", startTime)
    res = es.indices.create(index=indexName, body=request_body)
    print(" response: '%s'" % res)

i = 0
totalSize = 0
docNo = ""
headline = ""
text = ""

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

