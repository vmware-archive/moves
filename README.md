# Pivotal Real-Time Data Science: Scoring-as-a-Service
## moves

[moves.cfapps.pez.pivotal.io](https://moves.cfapps.pez.pivotal.io)

This application demonstrates real-time model scoring as a service using Pivotal Cloud Foundry (PCF), Pivotal Big Data Suite, Spring Cloud Data Flow, and Python-based open source machine learning. The pipeline applies broadly and would allow us to evaluate and score almost any feed of streaming data - from sensor data to unstructured text data - to drive real-time action.

Take a look at this [blog post](https://blog.pivotal.io/data-science-pivotal/products/scoring-as-a-service-to-operationalize-algorithms-for-real-time) and the [about page](https://moves.cfapps.pez.pivotal.io/about) for more information.

[![Alt text](https://img.youtube.com/vi/j6yiVhm9bhs/0.jpg)](https://www.youtube.com/watch?v=j6yiVhm9bhs)

## Pre-requisites

* Pivotal Cloud Foundry
    * Redis service

## Deploying the app on Pivotal Cloud Foundry

[http://docs.run.pivotal.io/devguide/deploy-apps/deploy-app.html](http://docs.run.pivotal.io/devguide/deploy-apps/deploy-app.html)

    cf create-service p-redis shared-vm moves-redis

    # sensor and dashboard flask app
    cd moves-app
    cf push; cd ..
    
    # flask training app 
    cd train-app
    cf push; cd ..

    #flask scoring app
    cd score-app
    cf push; cd ..
