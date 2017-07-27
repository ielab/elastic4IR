# Elasticsearch KL Divergence Similarity Plug in

These project objective is to implement LM KL Divergence similarity plug in to Elasticsearch 5.1.1. Template used to develop this plug in is: https://github.com/hscells/elasticsearch-similarity-plugin-stub

- download/clone this project to desktop

- define an `ES_PATH` environment variable using terminal/command. for example:

```bash
export ES_PATH=/usr/local/Cellar/elasticsearch/5.1.1
```

- use IntelliJ Idea to import the project as a Gradle project

- modify the build.gradle:
```
group 'com.github.jimmyoentung'

dependencies {
    compile group: 'org.elasticsearch', name: 'elasticsearch', version: '5.1.1'

    testCompile group: 'junit', name: 'junit', version: '4.11'
}

def esPluginPath = Paths.get(esPath, "/modules/${rootProject.name}")
```

- modify the settings.grade:
```
rootProject.name = 'lm-kldivergence'
```

- rename the project package into: com.github.jimmyoentung.eskldivergencesimilarity

- rename MyCustomSimilarity, MyCustomSimilarityPlugin, and MyCustomSimilarityProvider classes to KLDivergenceSimilarity, KLDivergenceSimilarityPlugin, and KLDivergenceSimilarityProvider

- modify the plugin-descriptor.properties:
```
description=ES KL Divergence Similarity Plugin
version=1.0
name=ES KL Divergence Similarity Plugin
classname=com.github.jimmyoentung.eskldivergencesimilarity.KLDivergenceSimilarityPlugin
java.version=1.8
elasticsearch.version=5.1.1
```

- modify the KLDivergenceSimilarityPlugin:
```
private static final String SIMILARITY_NAME = "KLDivergence";
```


At this stage, you should be all set to install the plugin to elasticsearch. A `gradle` task is provided
to do this. It will build and copy the files to wherever `ES_PATH` is set. To run this `gradle` task, in
the same directory as this readme file, run:

```bash
./gradlew installPlugin
```

For elasticsearch to register the plugin as installed, you need to **restart** elasticsearch.
