# Retrieving Field Text & Field Boosting
Using Elasticsearch and the Python api

## Pre-requisite
* Elasticsearch 5.x.x
* Kibana (optional)
* Python 3
* Elasticsearch python api. can be found from [here](https://elasticsearch-py.readthedocs.io/en/master/)


## Preparing a Sample Elasticsearch Index
First, lets create an Elasticsearch index to play with. We want to create an index name "book" and a type "chapter" within the index.
Each document in "chapter" type will have two text fields: title and summary.

Do the following in Kibana:

``` Elasticsearch via Kibana
PUT book
{
  "mappings":
  {
    "chapter":
    {
      "properties":
      {
        "title":
        {
          "type": "text"
        },
        "summary":
        {
          "type": "text"
        }
      }
    }
  }
}
```

To verify that new index structure is as expected:

``` Elasticsearch via Kibana
GET /book/_mapping/chapter
```

Expected results:
``` Output
{
  "book": {
    "mappings": {
      "chapter": {
        "properties": {
          "summary": {
            "type": "text"
          },
          "title": {
            "type": "text"
          }
        }
      }
    }
  }
}
```

At this point, we are ready to populate our index with some data:
```
PUT /book/chapter/1
{
  "title":"Introduction to Elasticsearch",
  "summary": "Basic steps from installing to searching documents using Elasticsearch"
}

PUT /book/chapter/2
{
  "title":"Documents Manipulation",
  "summary": "Procedures to add, update and delete documents in Elasticsearch"
}

PUT /book/chapter/3
{
  "title":"Advance searching",
  "summary": "Configure advance parameters to search documents"
}
```

Now we have three documents indexed in Elasticsearch. Next, we will search for these documents via Python

## Basic Search
Lets move from Kibana to python. First, we need to import the necessary api
```python
from elasticsearch import Elasticsearch
```

then, establish a connection to Elasticsearch
```python
es = Elasticsearch(urls='localhost', port=9200)
```

Next, we need to build the query string:
```python
query_string = {
    'query': {
        'query_string': {
            'query': 'Searching',
            'fields': ['title','summary']
        }
    }
}
```

In the above script, parameter 'query' specifies the terms to search and parameter 'fields' specifies fields to search.
In this example, we would like to search for term 'Searching' within fields 'title' and 'summary':

Lastly, we submit the query string to es:
```python
res = es.search(index='book', doc_type='chapter', body=query_string)
```

The res variable should contain the following results:
```JSON
{
    "hits": {
        "hits": [
            {
                "_type": "chapter",
                "_score": 0.27233246,
                "_index": "book",
                "_id": "1",
                "_source": {
                    "summary": "Basic steps from installing to searching documents using Elasticsearch",
                    "title": "Introduction to Elasticsearch"
                }
            },
            {
                "_type": "chapter",
                "_score": 0.25811607,
                "_index": "book",
                "_id": "3",
                "_source": {
                    "summary": "Configure advance parameters to search documents",
                    "title": "Advance searching"
                }
            }
        ],
        "max_score": 0.27233246,
        "total": 2
    },
    "took": 2,
    "timed_out": false,
    "_shards": {
        "failed": 0,
        "successful": 5,
        "total": 5
    }
}
```

The above results shows that there are two documents with title and summary fields match query term "searching".
In this example, we consider both title and summary fields as equal.

What if one field is more important than other?
Next, we will apply boosting factor to specify each field importance.

## Boosting field
For practice purpose, let's say that the title field is more important than the summary field.
Hence, query match to text in the title field should weighted double than query match to text in the summary field.

To specify field weight / boosting level, we need to add a caret symbol following each field name in the query string
```python
query_string = {
    'query': {
        'query_string': {
            'query': 'Searching',
            'fields': ['title^2','summary^1']
        }
    }
}
```

The above query string will produce the following result:
```JSON
{
    "_shards": {
        "failed": 0,
        "total": 5,
        "successful": 5
    },
    "took": 9,
    "timed_out": false,
    "hits": {
        "total": 2,
        "max_score": 0.51623213,
        "hits": [
            {
                "_type": "chapter",
                "_score": 0.51623213,
                "_index": "book",
                "_source": {
                    "title": "Advance searching",
                    "summary": "Configure advance parameters to search documents"
                },
                "_id": "3"
            },
            {
                "_type": "chapter",
                "_score": 0.27233246,
                "_index": "book",
                "_source": {
                    "title": "Introduction to Elasticsearch",
                    "summary": "Basic steps from installing to searching documents using Elasticsearch"
                },
                "_id": "1"
            }
        ]
    }
}
```

In the last result, document id: 3 is placed at the first place as it contains terms "searching" in the title field.
Document id: 3 only contains one mention of term "searching" in its title field.
Since we boosted the the title field by two the relevance score of document id: 3 to term "searching" is doubled.