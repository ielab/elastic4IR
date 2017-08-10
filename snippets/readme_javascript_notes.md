
## Notes on Angular Service for Elasticsearch search with snippets


----------
#### Purpose of this Document
Within the Github repository, in the snipets directory, there is an Angular service file, written in Javascript.  The purpose of this document is to provide background commentary on the file if you choose to implement the service or you just want to understand how it works

#### Purpose of the Code file
An Angular Service file can be called from anywhere on an Angular Website and it will hold its own set of data, in this case Elasticsearch search results.  The purpose of this service is to:
1. Perform the Elasticsearch search, given a query, i.e. one or more search terms
2. Read the search results from Elasticsearch and transfer the data to a holding object called *searchdata.hitdata*
3. Provide convenience functions for calling modules to check to see if more pages of data are present, where a page of search results is set as *searchdata.snippetsPerPage_CONST = 10*
4. Return a specific source document, given the document ID
5. Keep track of the current page number within the search results

#### Performing the Elasticsearch search
A calling module can make a call to the service using:

     function searchWithQuery(query,pageNumber){

The query should be in the form of "term1 term2 ...termN"
The pageNumber is required where a Search Engine Results Page has the facility to move forwards and backwards to new/old pages of search results.  The first search performed will be page 1 and then a *MoveNext* action by the user would require a call using the same query, but to page 2 of the search results.

The search request body is constructed using the query:

       var searchBody = {
          query:{
            match:{
              abstract: query
            }  
          },
          highlight:{
            fields:{
              abstract:{}
            }
          }
        };

You could replace your searchBody with whatever search you require. In this instance we are searching using 'match' within the 'abstract' field of each document using the 'query' terms.  

In addition, snippets have been requested using the 'highlight' object.  They are also to be derived from the abstract field.

A separate Elasticsearch service is called which performs the actual URL call.  The function call is asynchronous and it waits for the search results.  The call is:

     .factory('ESSearch', function($http,RESOURCE_ELASTICSEARCH_ADDRESS) {
    
          var searchResponse = function(searchBody, wantARange,numberOfHits,fromHitNum){
            var sizeURLText = '?pretty';
            if (wantARange==true)
              sizeURLText = '?size=' + numberOfHits + '&from=' + fromHitNum;
    
            return $http.post(RESOURCE_ELASTICSEARCH_ADDRESS+'_search' + sizeURLText,searchBody).success(function(data, status) {
              console.log('status is:' + angular.toJson(status));
              console.log('we have search data OK');
                return data;
             })
            .error(function(data, status) {
                console.log("Error getting ES data with status:" + angular.toJson(status) + ' and data: ' + angular.toJson(data) );
                return null;
            })
    
          };
          return { searchResponse: searchResponse };
      });

Note the calling parameters:
1. The elasticsearch URL address (stored in a constants file)
2. The _search command
3. The number of search items (hits) required and from which search result item do you want the results to start, i.e. from 10 onwards
4. The search body, which contains the specified search and highlight


#### Handling the Elasticsearch search results
The search results are returned to the searchWithQuery() function in the following code:

    var log = [];
                var hits =[];
                var hitSources = [];
                var allHits;
                var hitcount = 0;
                
     
                angular.forEach(result.data, function(value, key) {
                  this.push(key + ': ' + value);
                  if (key=="hits"){
                    allHits = value;
    
                    if (pageNumber==1) // get the total hits for the first page, after that we get ranges
                      searchData.totalHits = allHits.total;
                    console.log('total hits are:' + searchData.totalHits);
    
                    angular.forEach(allHits,function(value2,key2){
                      if (key2=="hits"){
                        angular.forEach(value2,function(hit){
                            hitcount++;
                            hits.push(hit);
                            //this is where the type fields are selected from ES
                            //USE BODY-> hitSources.push(getHitData(hit._id,hit._source["journal-title"],hit._source["pub-date"],hit._source["article-title"],hit.highlight,hit._source["HTML_BODY"],hitcount,hit._source["abstract"]));
                            hitSources.push(getHitData(hit._id,hit._source["journal-title"],hit._source["pub-date"],hit._source["article-title"],hit.highlight,hit._source["HTML_ALL"],hitcount,hit._source["abstract"]));
                        });
                      }
    
                    })
                  }

