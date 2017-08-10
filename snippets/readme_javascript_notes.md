
## Notes on Angular Service for Elasticsearch search with snippets


----------
#### Purpose
Within the Github repository, in the snipets directory, there is an Angular service file, written in Javascript.  The purpose of this document is to provide background commentary on the file if you choose to implement the service or you just want to understand how it works

#### Elements of the Code file
An Angular Service file can be called from anywhere on an Angular Website and it will hold it's own set of data, in this case Elasticsearch search results.  The purpose of this service is to:
1. Perform the Elasticsearch search, given a query, i.e. one or more search terms
2. Read the search results from Elasticsearch and transfer the data to a holding object called *searchdata.hitdata*
3. Provide convenience functions for calling modules to check to see if more pages of data are present, where a page of search results

