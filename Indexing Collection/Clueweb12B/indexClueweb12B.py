import gzip
import warc
import time
import glob
import lxml.html
import re
import io
import sys
from elasticsearch import Elasticsearch
import multiprocessing

# corpus file location
warcPath = "/Volumes/Data/Phd/Data/clueweb12_diskb/"

# create connection to elasticsearch
es0 = Elasticsearch(urls='http://localhost', port=9200, timeout=600)

# specify bulk size
bulk_size = 4000 #bulk limit in KiloBytes
bulk_count = 1000 #bulk limit in number of files

# index and document type name
indexName = "clueweb12b_test"
docType = "clueweb"

# Create Index
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

# Create index
if not es0.indices.exists(indexName):
    print ("creating ", indexName, " index, start at ", startTime)
    res = es0.indices.create(index=indexName, body=request_body)
    print(" response: '%s'" % res)

docId = "-"


def es_index(fname):
    i = 0
    totalSize = 0
    bulk_data = []
    lapTime = time.time()
    es = Elasticsearch(urls='http://localhost', port=9200, timeout=600)

    print("Processing file: {}".format(fname))
    with gzip.open(fname, mode='rb') as gzf:
        WarcTotalDocuments = 0
        EmptyDocuments = 0
        for record in warc.WARCFile(fileobj=gzf):
            if record.header.get('WARC-Type').lower() == 'warcinfo':
                WarcTotalDocuments = record.header.get('WARC-Number-Of-Documents')

            if record.header.get('WARC-Type').lower() == 'response':
                docId = record.header.get('WARC-Trec-ID')
                docString = record.payload.read()

                htmlStart = docString.find('<html')
                if htmlStart < 1:
                    htmlStart = docString.find('<HTML')
                if htmlStart < 1:
                    htmlStart = docString.find('<Html')

                if htmlStart < 1:
                    EmptyDocuments += 1
                else:
                    # extract and scrub html string
                    htmlString = docString[htmlStart:]
                    htmlString = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\xff]', '', htmlString)
                    htmlString = re.sub(r'&\w{4,6};', '', htmlString)
                    htmlString = htmlString.replace(",", " ").replace("-", " ").replace(".", " ")

                    fContent = io.BytesIO(str(htmlString.decode("utf-8", "ignore")))

                    try:
                        htmlDoc = lxml.html.parse(fContent)

                        # the html.xpath return an array so need to convert it to string with join method
                        title = " ".join(htmlDoc.xpath('//title/text()'))

                        rootClean = htmlDoc.getroot()

                        body = " - "
                        try:
                            body = rootClean.body.text_content()
                            body = ' '.join(word for word in body.split() if word.isalnum())
                        except:
                            pass

                        content = title + body
                        bulk_meta = {
                            "index": {
                                "_index": indexName,
                                "_type": docType,
                                "_id": docId
                            }
                        }

                        bulk_content = {
                            'title': title,
                            'body': body
                        }

                        bulk_data.append(bulk_meta)
                        bulk_data.append(bulk_content)
                        totalSize += (sys.getsizeof(content) / 1024)  # convert from bytes to KiloBytes

                        i += 1
                        if totalSize > bulk_size or i % bulk_count == 0:
                            res = es.bulk(index=indexName, doc_type=docType, body=bulk_data, refresh=False)
                            bulk_data = []
                            totalSize = 0
                    except:
                        print("Error processing document: {}".format(docId))
                        raise

        if len(bulk_data) > 0:
            # index the remainder files
            res = es.bulk(index=indexName, doc_type=docType, body=bulk_data, refresh=False)

        print("File {0} Completed, Duration: {1} sec, Total: {2}, Processed: {3}, Empty: {4}, Variance: {5}".
               format(fname, time.time() - lapTime, WarcTotalDocuments, str(i), str(EmptyDocuments),
                      str(int(WarcTotalDocuments) - i - EmptyDocuments)))


# traverse all folder and parallely process all gzipped warc files
warcFolder = glob.glob(warcPath + "*")
for warcFold in warcFolder:
    folders = glob.glob(warcFold + "/*")
    print("Processing Path: {}".format(warcFold))

    for fold in folders:
        print("Processing folder: {}".format(fold))
        p = multiprocessing.Pool()
        resultString = p.map(es_index, glob.glob(fold + "/*"))
        p.close()
        p.join()
