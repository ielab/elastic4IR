

## Common Problems and Questions

### What does the ES cluster status mean, and why is it `yellow`?

The status of an Elasticsearch cluster can either be:

 *  RED: some or all the (primary) shards are not ready.

 * YELLOW: Elasticsearch has allocated all of the primary shards, but some/all of the replicas have not been allocated. This is the default status when we only have one node

 * GREEN: the cluster is fully operational. Elasticsearch is able to allocate all shards and replicas to machines within the cluster.

 For other information on cluster health, see [this](http://chrissimpson.co.uk/elasticsearch-yellow-cluster-status-explained.html) blog post by Chris Simpson.