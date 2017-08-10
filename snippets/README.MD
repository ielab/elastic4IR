

Getting Snippet Text for Query Results
--------------------------------------

A snippet is the short summary extracted from the source file which usually emphasises the query terms found in that source document. For the search given below, the snippets are provided beneath each blue heading.  Note the boldface font given to the same or similar search terms

![enter image description here](https://lh3.googleusercontent.com/-eVYfNBaaRmw/WYvVgexMTGI/AAAAAAAACFc/62enoP_6a38nUNAOPv6IFL6C4RxMmduuQCLcBGAs/s0/googleSERP.png "googleSERP.png")

## Snippets in Elasticsearch
----------
Elasticsearch provides an easy method for accessing the snippets from returned search results.  The Easticsearch method is called **highlighting**. In this section we will construct a short example to demonstrate highlighting from the MAC console, followed by some sample Javascript code to show you how to access from a JS client.

## Snippet Example from the MAC Console

###Pre Requisites
This example assumes you have Elasticsearch 5.x.x installed and running on your MAC. 

### Setup Steps


