# IoT-3D-Systems

# Docker-Compose

docker-compose contains both our core flask image and our OSM dockerized image with the Modena province extract from OSM Planet image (OSM Server)

check into the project root path where the `docker-compose.yml` file is located and execute:

## Commands

`docker-compose build` to build a new image

`docker-compose up -d` to run that just built image into a container in a detached mode **(do this)**

`docker-compose up` to run that just built image into a "frontend-ed" container

`docker-compose down` to stop the container

# Docker

## Remote image for server

to execute docker container run:

` docker run -d -p 5000:5000 mick2k1/iotflask:latest `


[Docker hub image](https://hub.docker.com/repository/docker/mick2k1/iotflask)


## Upgrading, Development & Deploy

First of all check into your local WSL/Linux where docker is installed (verify with `which docker`)

`git clone git@github.com:mich2k/IoT-3D-Systems.git`

`cd flaskIOT`

only for the first time run

`sudo chmod a+x boot.sh`



/*


  edit, upgrade and change the flask codebase if needed
  
  
*/


Run the build script for the first time


_NOTE: The first time the process will be quite slow (ETA: 4mins)_

`sudo bash build_and_run.sh`

Now the container is hopefully up & running, hence you will be able to browse into


`http://127.0.0.1:5000/`

and evaluate if is actually running & upgraded according the new codebase


If wou wish to run it in your local host (requirements will be automatically installed in local venv) you can test your code with

`source localboot.sh`

if you want to try the new codebase into the container (strongly suggested) you just have to run again

`sudo bash build_and_run.sh` (ETA: few seconds)

Remember that if works into the container will work for everybody (server included), if works only locally with `source localboot.sh` and not into the container it means it wont run on the server. Before pushing is mandatory to test the new codebase in the docker container.

When you want to "commit", share the new upgraded image and deploy to the server run

`docker push mick2k1/iotflask`

along with

`git add . && git commit -m "{commit message}" && git push`

**Remember to test the code inside the container before pushing**



## Cleaning local host

After N runs or when you are done with this part of the project I suggest cleaning up your host with the delete_all script.

Check into your WSL/LinuxOS and run

`sudo bash delete_all.sh`

You can execute this when you wish, if, after deleting every container & image with this script, you want to commit/deploy again you can; the build script will rebuild the container and download back all the needed images (More time needed on first lunch)


The script is available [here](https://github.com/mich2k/IoT-3D-Systems/blob/main/docker-scripts/delete_all.sh)

# Trello:

## group url

https://trello.com/w/iotproject38


# 3D Model Choices, Design & Diagrams

# Concept:
## reqs:
* Stato del bidone ("sano"/malfunzionante/manutenzione)
* Sensore di riempimento (prossimità)
* Tag NFC per l'accesso (con raccolta dati dell'oggetto APPARTAMENTO)
* Sensore di temperatura
* Sensore di "vandalismo" : accelerometro + tilt sensor, tentativo di manomissione
* Raccolta dati per effettuare predizioni sul futuro livello di riempimento
* Motore che gestisce l'apertura/chiusura del pannello
* Dati salvati in Cloud
* Tempo raccolta pattume (Tempo di riempimento)
* Percorso ottimo basato sul livello di riempimento
* Alimentato ad energia solare + batteria
* Feedback sullo stato del bidone (lato User)
* Schermo

## Sensors/Actuators:
* Temperatura/CO2
* Accelerometro
* Tilt sensor
* Tag NFC
* Motore (Attuatore Lineare)
* Batteria (BMS)/Pannello
