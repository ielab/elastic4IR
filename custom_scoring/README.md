# Implement Custom Similarity Plug In to Elasticsearch
This channel describe procedure to implement a custom similarity plug in to Elasticsearch 5.1.1.
A language model KL-Divergence will be implemented as a case study.

This channel is derived from https://github.com/jimmyoentung/ES-KLDivergenceSimilarity.

## Implementation
- download/clone this project to your local machine

- define an `ES_PATH` environment variable using terminal/command. for example:

```bash
export ES_PATH=/usr/local/Cellar/elasticsearch/5.1.1
```

- use IntelliJ Idea or other IDE to import the project as a Gradle project

- specify elastic version used by modifying the build.gradle:
```java
group 'com.github.jimmyoentung'

dependencies {
    compile group: 'org.elasticsearch', name: 'elasticsearch', version: '5.1.1'

    testCompile group: 'junit', name: 'junit', version: '4.11'
}

def esPluginPath = Paths.get(esPath, "/modules/${rootProject.name}")
```

- modify the settings.grade:
```java
rootProject.name = 'lm-kldivergence'
```

- rename the project package into your github channel. This example use may channel: com.github.jimmyoentung.eskldivergencesimilarity

- modify the plugin-descriptor.properties:
```java
description=ES KL Divergence Similarity Plugin
version=1.0
name=ES KL Divergence Similarity Plugin
classname=com.github.jimmyoentung.eskldivergencesimilarity.KLDivergenceSimilarityPlugin
java.version=1.8
elasticsearch.version=5.1.1
```

- implement the custom similarity in KLDivergenceSimilarity.java
```java
public class KLDivergenceSimilarity extends LMSimilarity {
    /** The &mu; parameter. */
    private final float mu;

    /** The alphaD parameter. */
    private final float ad;

    /** Instantiates the similarity with the provided &mu; and alphaD parameter. */
    public KLDivergenceSimilarity(CollectionModel collectionModel, float mu, float ad) {
        super(collectionModel);
        this.mu = mu;
        this.ad = ad;
    }

    /** Instantiates the similarity with the provided &mu; parameter. */
    public KLDivergenceSimilarity(float mu, float ad) {
        this.mu = mu;
        this.ad = ad;
    }

    /** Instantiates the similarity with the default &mu; value of 2000.
     * alphaD default value is 700 based on the average of CluewebB body field length*/
    public KLDivergenceSimilarity(CollectionModel collectionModel) {
        this(collectionModel, 2000, 700);

    }

    /** Instantiates the similarity with the default &mu; value of 2000.
     *  alphaD default value is 700 based on the average of CluewebB body field length*/
    public KLDivergenceSimilarity() {
        this(2000, 700);
    }

    @Override
    protected float score(BasicStats stats, float freq, float docLen) {
        
        float score = stats.getBoost() *
                (float)(Math.log(((freq + mu * ((LMStats)stats).getCollectionProbability()) / (mu + docLen)) /
                (ad * ((LMStats)stats).getCollectionProbability())) +
                Math.log(ad));

        return score > 0.0f ? score : 0.0f;
    }

    @Override
    protected void explain(List<Explanation> subs, BasicStats stats, int doc,
                           float freq, float docLen) {
        if (stats.getBoost() != 1.0f) {
            subs.add(Explanation.match(stats.getBoost(), "boost"));
        }

        subs.add(Explanation.match(mu, "mu"));
        Explanation weightExpl = Explanation.match(
                (float)Math.log(1 + freq /
                        (mu * ((LMStats)stats).getCollectionProbability())),
                "term weight");
        subs.add(weightExpl);
        subs.add(Explanation.match(
                (float)Math.log(mu / (docLen + mu)), "document norm"));
        super.explain(subs, stats, doc, freq, docLen);
    }

    /** Returns the &mu; parameter. */
    public float getMu() {
        return mu;
    }

    @Override
    public String getName() {
        return String.format(Locale.ROOT, "KL Divergence(%f)", getMu());
    }
}
```

Note that on the above script we have two data members: mu and ad which represent the KL Divergence parameters.
These two parameters should be configurable and thus we should put it as parameter.
Modify the KLDivergenceSimilarityProvider.java to register the two parameters and their default value

```java
package com.github.jimmyoentung.eskldivergencesimilarity;

import org.apache.lucene.search.similarities.Similarity;
import org.elasticsearch.common.settings.Settings;
import org.elasticsearch.index.similarity.AbstractSimilarityProvider;

public class KLDivergenceSimilarityProvider extends AbstractSimilarityProvider {

    private final KLDivergenceSimilarity similarity;

    public KLDivergenceSimilarityProvider(String name, Settings settings) {
        super(name);
        float mu = settings.getAsFloat("mu", 2000f);
        float ad = settings.getAsFloat("ad", 700f);

        this.similarity = new KLDivergenceSimilarity(mu, ad);
    }

    /**
     * {@inheritDoc}
     */
    @Override
    public Similarity get() {
        return similarity;
    }
}
```

Lastly, we need to register our new similarity plugin "KLDivergence" using the KLDivergenceSimilarityPlugin.java
```java
package com.github.jimmyoentung.eskldivergencesimilarity;

import org.elasticsearch.index.IndexModule;
import org.elasticsearch.plugins.Plugin;

public class KLDivergenceSimilarityPlugin extends Plugin {

    private static final String SIMILARITY_NAME = "KLDivergence";

    @Override
    public void onIndexModule(IndexModule indexModule) {
        super.onIndexModule(indexModule);
        indexModule.addSimilarity(SIMILARITY_NAME, KLDivergenceSimilarityProvider::new);
    }
}
```

At this stage, you should be all set to install the plugin to elasticsearch. A `gradle` task is provided
to do this. It will build and copy the files to wherever `ES_PATH` is set. To run this `gradle` task, in
the same directory as this readme file, run:

```bash
./gradlew installPlugin
```

For elasticsearch to register the plugin as installed, you need to **restart** elasticsearch.
If new plugin is loaded succesfully, you will see the following message within the Elasticsearch log
```
[2017-07-27T13:51:33,444][INFO ][o.e.p.PluginsService     ] [J-8Q2RU] loaded module [ES KL Divergence Similarity]
```


## using the custom similarity module
Now that we have load the KL Divergence similarity module, we can use it in our index.
From kibana, create an index using the KL Divergence with default parameter values (mu=2000, ad=700)
```kibana
PUT books
{
  "settings":
  {
    "similarity": {
      "sim_title": {
          "type": "KLDivergence",
          "mu": 2000,
          "ad": 700
      },
      "sim_body": {
          "type": "KLDivergence",
          "mu": 2000,
          "ad": 700
      }
    }
  },
  "mappings":
  {
    "chapter":
    {
      "properties":
      {
        "title":
        {
          "type": "text",
          "similarity": "sim_title"
        },
        "summary":
        {
          "type": "text",
          "similarity": "sim_body"
        }
      }
    }
  }
}
```

Note on the above script, we create on similarity for each field.
This is a good practice as it allows us to apply varied simmilarity parameter value for all fields.

To check if the KLDivergence is used in the "books" index settings, execute the following in Kibana:
```Kibana
GET /books/_settings
```

expected output:
```json
{
  "books": {
    "settings": {
      "index": {
        "number_of_shards": "5",
        "provided_name": "books",
        "similarity": {
          "sim_body": {
            "mu": "2000",
            "type": "KLDivergence",
            "ad": "700"
          },
          "sim_title": {
            "mu": "2000",
            "type": "KLDivergence",
            "ad": "700"
          }
        },
        "creation_date": "1501203229432",
        "number_of_replicas": "1",
        "uuid": "PNv8PN4yTBiaAV8dSScVsw",
        "version": {
          "created": "5010199"
        }
      }
    }
  }
}
```

Next, we need to check if the similarity settings have been assigned properly. In Kibana:
```kibana
GET /books/_mapping/chapter
```

expected output:
```json
{
  "books": {
    "mappings": {
      "chapter": {
        "properties": {
          "summary": {
            "type": "text",
            "similarity": "sim_body"
          },
          "title": {
            "type": "text",
            "similarity": "sim_title"
          }
        }
      }
    }
  }
}
```