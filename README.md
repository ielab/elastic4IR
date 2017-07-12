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

For this you need to have Docker and Docker-compose installed. For a out of the box ES and Kibana installation, download the docker-compose file [docker-compose.yml](https://github.com/codingexplained/complete-guide-to-elasticsearch/blob/master/docker-compose.yml). Then open a terminal in the location where you downloaded and type `docker-compose up`. This will start the dockers (you need to have the Docker engine running). Now an instance of ES is running at [http://localhost:9200](http://localhost:9200) and a version of Kibana is runnign at [http://localhost:5601](http://localhost:5601).

To Check the status of Kibana, we can just go to that address. To check ES, we can interrogate it from the terminal with an HTTP request:

```curl http://localhost:9200```

will return the status of the ES cluster.

Note that this particular docker image creates a folder `data` in the local directory - this will persist some of the ES and Kibana data, so to allow to turn off and then on again the docker without loss of data.

The processes running in Docker can be terminated with the usual `CTRL+C`. `docker-compose down` issued then on the terminal releases all the resources used by Docket. 

ES configurations can be changed by editing the `docker-compose.yml` file.

### Configuring Elasticsearch

Configurations are in `config/elasticsearch.yml`. Note that each node could be configured differently.
It allows to change the port in which the cluster listens. 


## Interacting with Elasticsearch via HTTP requests

You can use Kibana's Dev Tool Console or Postman, among others, to send commands & queries to the cluster as HTTP requests.
Commands are in the form:

``` <REST verb> /<indexname>/<API>```

For example: `GET /myindex/_search`
