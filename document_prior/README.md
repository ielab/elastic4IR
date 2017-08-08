# Using Document Prior in Elasticsearch 5.1.1
This repository explain how to consider document priors (e.g. Page rank, spam rank, etc) as a boosting factor in Elasticsearch.

## Pre-requisite
* Elasticsearch 5.x.x
* Kibana (optional)





## Preparing a Sample Elasticsearch Index
First, lets create an Elasticsearch index to work with. We want to create an index name "book" and a type "chapter" within the index.
Each document in "chapter" type will have two text fields (title and summary) and pageRank field.
The pageRank will be used as example of document prior.

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
        },
        "pagerank":
        {
          "type": "float"
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
          "pagerank": {
            "type": "float"
          },
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
``` Elasticsearch via Kibana
PUT /book/chapter/1
{
  "title":"Introduction to Elasticsearch",
  "summary": "Basic steps from installing to searching documents using Elasticsearch",
  "pagerank": 0.0003
}

PUT /book/chapter/2
{
  "title":"Documents Manipulation",
  "summary": "Procedures to add, update and delete documents in Elasticsearch",
  "pagerank": 0.5
}

PUT /book/chapter/3
{
  "title":"Advance searching",
  "summary": "Configure advance parameters to search documents",
  "pagerank": 0.1
}
```

Now that we have three documents indexed in Elasticsearch, we can use Elasticsearch to search for the documents.
First, lets say we want to simply search for book chapter that contain term "Searching"
``` Elasticsearch via Kibana
GET /book/chapter/_search
{
    "query": {
        "query_string": {
            "query": "Searching",
            "fields": ["title","summary"]
        }
    }
}
```

Results:
```JSON
{
  "took": 3,
  "timed_out": false,
  "_shards": {
    "total": 5,
    "successful": 5,
    "failed": 0
  },
  "hits": {
    "total": 2,
    "max_score": 0.27233246,
    "hits": [
      {
        "_index": "book",
        "_type": "chapter",
        "_id": "1",
        "_score": 0.27233246,
        "_source": {
          "title": "Introduction to Elasticsearch",
          "summary": "Basic steps from installing to searching documents using Elasticsearch",
          "pagerank": 0.0003
        }
      },
      {
        "_index": "book",
        "_type": "chapter",
        "_id": "3",
        "_score": 0.25811607,
        "_source": {
          "title": "Advance searching",
          "summary": "Configure advance parameters to search documents",
          "pagerank": 0.1
        }
      }
    ]
  }
}
```

Note that document id 1 is ranked on top.

Next, let us consider the pagerank to boost document with higher pagerank score.
``` Elasticsearch via Kibana
GET /book/chapter/_search
{
  "query":{
    "function_score": {
      "query": {
        "query_string": {
            "query": "Searching",
            "fields": ["title","summary"]
        }
      },
      "functions": [
        {
          "field_value_factor": {
            "field": "pagerank"
          }
        }
      ],
      "score_mode": "multiply"
    }
  }
}
```

results:
``` JSON
{
  "took": 2,
  "timed_out": false,
  "_shards": {
    "total": 5,
    "successful": 5,
    "failed": 0
  },
  "hits": {
    "total": 2,
    "max_score": 0.025811607,
    "hits": [
      {
        "_index": "book",
        "_type": "chapter",
        "_id": "3",
        "_score": 0.025811607,
        "_source": {
          "title": "Advance searching",
          "summary": "Configure advance parameters to search documents",
          "pagerank": 0.1
        }
      },
      {
        "_index": "book",
        "_type": "chapter",
        "_id": "1",
        "_score": 0.00008169974,
        "_source": {
          "title": "Introduction to Elasticsearch",
          "summary": "Basic steps from installing to searching documents using Elasticsearch",
          "pagerank": 0.0003
        }
      }
    ]
  }
}
```

Note that the score in the last results is equal to score from the previous result multiplied by the pagerank value.
Since document id: 3 has much higher pagerank value, document id 3 is boosted way higher than document id 1 and is now on top.
