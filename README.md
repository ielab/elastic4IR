# elastic4IR
Resources and documentation for using Elastic for Information Retrieval

Elasticsearch (ES) is written in Java and builds on the top of Lucene. It provides a REST API to the Lucene library and uses JSON as data format. It is part of the Elastic Stack (ELK+), along with Logstash and Kibana. Logstash enables to get data into Elasticsearch (among other functionalities): it is a data processing pipeline that can ingest, transform and filter data before sending data to a stash (typically Elasticsearch). Kibana is an analytics and visualisation platform that lets you analyse data stored in ES; it has pre-coded diagrams and plots, that can be expanded. The Elastic Stack (ELK+) has further more products, like Beats and Xpack. Beats lets you get hold of the data to pass to Logstash or to ES: for example there are Beats for collecting network traffic, system performance, etc. Xpack contains extensions for ES, e.g. security (including LDAP integrations), alerting, monitoring, reporting. 

## Architecture of Elasticsearch
A *node* is a server that stores data, and is part of a cluster - thus a cluster contains one or more nodes. Each node contains some data: the collection of nodes contains all the data for the cluster. Each node participates to the indexing and searching of data. ES coordinates searches betwene multiple nodes, and distributes the data across nodes. Every node can handle (and coordinate) HTTP requests, which then can forward requests to other nodes. Each node can be assigned to be a masternode, which is the node that coordinates the other nodes (e.g. which nodes are part of the cluster, etc). The default name for the cluster is `elasticsearch` and the default name for a node is the unique identifier `uuid`; these can be changed. By default nodes join the cluster `elasticsearch`: thus if you start multiple nodes, they automatically join the cluster `elasticsearch` (thus make sure you change the default cluster name, otherwise other nodes in your network will join the cluster).

You can have as many nodes you want, including just one. The ES architecture is very scalable.

Each data item stored in the cluster is called a *document*: these are JSON objects, which include properties/attributes. Documents are stored into *indeces*. Documents have ids assigned to them (either automatically or manually); indeces are representated by names (unique names that you assing). 

Note that ES used *types* in the past - this is being phased out. It used to be that every document has a `_type` field which could be used for filtering when searching on a specific type. [This resource from the ES team](https://www.elastic.co/blog/index-vs-type) explains more on types.

*Sharding* is what makes ES largely scalable: it allows to split the indexes data across nodes (so to address the hardware limits of each node). Each node may contain multiple shards. Sharding allows to deal with volumes of data that are beyond the limits of one single nodes; but it also allows for parallalisation of operations (also within the same node): multiple machines (or cores in one machine) can work on the same query at the same time. The number of shards can be specified at index creation (default is 5). Once an index is created, the number of shards cannot be changed - to increase the shards a new index needs to be created, and data moved across.

ES natively supports *replication* of shards: that is, shards are copied across nodes. The shards that are replicated are claled primary shards, it's replica are called replica shards (note you need multiple nodes for replication). Replication delivers high reliability and increased performance for search queries, because searches can be performed on the replicas in parallel. The number of replicas is defined at indexing. The default is 1: thus by default each node has 5 shards, and 5 replicas (thus 10 shards in total) - this if a cluster has more than one node. 

ES uses primary backup for replication: all operations that affect the index are sent to the primary shard, which is responsible for validating the request. When accepted, the operation is performed locally; when it is completed it is forwarded to the replicas, where it is performed in parallel.

Routing is used to determine in which shard new documents should be stored. To decide on sharding, ES computes:

shard = hash(doc_id) % total_primary_shards

However, ES allows to specify a costum sharding function.



## Installing Elasticsearch 

### Running ES in Mac/Unix

This is as simple as downloading ES and running it from the bin. Note, Java is required.


### Using Docker to run ES

Docker is a popular container technology (like a lightweight virtual machine). 

For this you need to have Docker installed. For an out of the box Elasticsearch, Kibana and Logtash installation, you can use the docker image at [https://hub.docker.com/r/hscells/elastic4ir/](https://hub.docker.com/r/hscells/elastic4ir/). You can simply open a terminal and type `docker run -p 9200:9200 -e "http.host=0.0.0.0" -e "transport.host=127.0.0.1" -e "xpack.security.enabled=false" hscells/elastic4ir`. This will start the dockers (you need to have the Docker engine running). Now an instance of ES is running at [http://localhost:9200](http://localhost:9200) and a version of Kibana is runnign at [http://localhost:5601](http://localhost:5601).

To Check the status of Kibana, we can just go to that address. To check ES, we can interrogate it from the terminal with an HTTP request:

```curl http://localhost:9200```

will return the status of the ES cluster.

Note that this particular docker image creates a folder `data` in the local directory - this will persist some of the ES and Kibana data, so to allow to turn off and then on again the docker without loss of data. (*not in the current Docker image*)

The processes running in Docker can be terminated with the usual `CTRL+C`. 

(11/08/2017: note, the docker image at the moment does not contain Kibana and Logtash - we will update this soon. For now you need Kibana and Logtash on your machine, if you want to use those functionalities)

### Configuring Elasticsearch

Configurations are in `config/elasticsearch.yml`. Note that each node could be configured differently.
It allows to change the port in which the cluster listens. 


## Interacting with Elasticsearch via HTTP requests

You can use Kibana's Dev Tool Console or Postman, among others, to send commands & queries to the cluster as HTTP requests.
Commands are in the form:

``` <REST verb> /<indexname>/<API>```

For example: `GET /myindex/_search`. This would work in Kibana. If using `curl` (or other REST interfaces), then this would become: `curl -XGET "http://localhost:9200/my_index/_search"`.

Note, if you are using the Docker installation, then instead of `localhost`, you should use `elasticsearch`, as that has bene setup as the hostname of the Docker virtual machine.
Also, when not using Kibana and the request has a payload (or request body), then we need to specify a request body (json).
In the following, we report commands as Kibana commands.

### Creating an index and interacting with it.

To create an empty index:

```
PUT /indexname
{
}
```

The `_cat` API allows to retrieve information about the cluster in human readable format.

```
GET /_cat/indeces?v
```

The `v` parameter specifies the output should be verbose. The result shows information of indeces in the cluster.
The yellow health for an index means that some replicas have not been allocated.

## Small Demos

 - [Start Elasticsearch, Index & Query](https://gist.github.com/hscells/774e112d14e3f249e8960d7147d61353)
 - [Elasticsearch - Accessing a Term Vector](https://gist.github.com/hscells/4d52456b000220fd2fcf2b480c125052)
 - [Logstash pubmed pipeline](https://gist.github.com/hscells/f08be357aec1757b231031dead3eba35)

## The Elasticsearch query language

## Using Elasticsearch programmatically for IR experiments

This section shows code snippets detailing how to perform common operations used when implementing IR experiments or new retrieval models.

### [Creating a TREC run with Elasticsearch](https://github.com/ielab/elastic4IR/blob/master/trec_run/Elasticsearch%20TREC%20Run.ipynb)

### [Accessing a Term Vector](https://github.com/ielab/elastic4IR/blob/master/term_vector/Accessing%20a%20Term%20Vector.ipynb)

### [Implement a new Retrieval Model (Custom Similarity Plug-in)](https://github.com/ielab/elastic4IR/blob/master/custom_scoring)

### [Boolean Retrieval in Elasticsearch](https://github.com/ielab/elastic4IR/blob/master/boolean_retrieval/Boolean%20Retrieval.ipynb)

### [Using Document Priors via Boosting](https://github.com/ielab/elastic4IR/blob/master/document_prior)

### [Field Retrieval & Field Boosting](https://github.com/ielab/elastic4IR/tree/master/field_retrieval)

### [Getting Snippet Text for Query Results](https://github.com/ielab/elastic4IR/tree/master/snippets)


## [Common Problems and Solutions with Elasticsearch](https://github.com/ielab/elastic4IR/tree/master/faq)

