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
  "title":"Searching using Elasticsearch",
  "summary": "Basic steps from installing to searching documents using Elasticsearch"
}

PUT /book/chapter/2
{
  "title":"Documents Manipulation",
  "summary": "Procedures to add, update and delete documents in Elasticsearch"
}

PUT /book/chapter/3
{
  "title":"Advance search",
  "summary": "Configure searching parameters"
}
```

Now we have three documents indexed in Elasticsearch. Next, we will search for these documents via Python

## Basic Search

First, we need to import the necessary api
```python
from elasticsearch import Elasticsearch
```

