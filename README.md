# elastic4IR
Resources and documentation for using Elastic for Information Retrieval

Elasticsearch (ES) is written in Java and builds on the top of Lucene. It provides a REST API to the Lucene library and uses JSON as data format. It is part of the Elastic Stack (ELK+), along with Logstash and Kibana. Logstash enables to get data into Elasticsearch (among other functionalities): it is a data processing pipeline that can ingest, transform and filter data before sending data to a stash (typically Elasticsearch). Kibana is an analytics and visualisation platform that lets you analyse data stored in ES; it has pre-coded diagrams and plots, that can be expanded. The Elastic Stack (ELK+) has further more products, like Beats and Xpack. Beats lets you get hold of the data to pass to Logstash or to ES: for example there are Beats for collecting network traffic, system performance, etc. Xpack contains extensions for ES, e.g. security (including LDAP integrations), alerting, monitoring, reporting. 

## Architecture of Elasticsearch
A *node* is a server that stores data, and is part of a cluster - thus a cluster contains one or more nodes. Each node contains some data: the collection of nodes contains all the data for the cluster. Each node participates to the indexing and searching of data. ES coordinates searches betwene multiple nodes, and distributes the data across nodes. Every node can handle (and coordinate) HTTP requests, which then can forward requests to other nodes. Each node can be assigned to be a masternode, which is the node that coordinates the other nodes (e.g. which nodes are part of the cluster, etc). The default name for the cluster is `elasticsearch` and the default name for a node is the unique identifier `uuid`; these can be changed. By default nodes join the cluster `elasticsearch`: thus if you start multiple nodes, they automatically join the cluster `elasticsearch` (thus make sure you change the default cluster name, otherwise other nodes in your network will join the cluster).

You can have as many nodes you want, including just one. The ES architecture is very scalable.

Each data item stored in the cluster is called a *document*: these are JSON objects, which include properties/attributes. Documents are stored into *indeces*. Documents have ids assigned to them (either automatically or manually); indeces are representated by names (unique names that you assing). 

Note that ES used *types* in the past - this is being phased out. It used to be that every document has a `_type` field which could be used for filtering when searching on a specific type. [[https://www.elastic.co/blog/index-vs-type|This resource from the ES team]] explains more on types.

*Sharding* is what makes ES largely scalable: it allows to split the indexes data across nodes (so to address the hardware limits of each node). Each node may contain multiple shards. Sharding allows to deal with volumes of data that are beyond the limits of one single nodes; but it also allows for parallalisation of operations (also within the same node): multiple machines (or cores in one machine) can work on the same query at the same time. The number of shards can be specified at index creation (default is 5). Once an index is created, the number of shards cannot be changed - to increase the shards a new index needs to be created, and data moved across.

ES natively supports *replication* of shards: that is, shards are copied across nodes. The shards that are replicated are claled primary shards, it's replica are called replica shards (note you need multiple nodes for replication). Replication delivers high reliability and increased performance for search queries, because searches can be performed on the replicas in parallel. The number of replicas is defined at indexing. The default is 1: thus by default each node has 5 shards, and 5 replicas - this if a cluster has more than one node.

## Installing Elasticsearch 



## Running Elasticsearch
