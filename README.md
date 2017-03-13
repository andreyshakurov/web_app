# Flask web app

Uses docker-compose with a python flask microservice and mongodb instance to make a social network application that stores profile information.
# Tools involved
Docker, docker-compose, python, flask microframework
- How to install Docker <https://docs.docker.com/engine/installation/linux/ubuntu/>
- How to install Docker-Compose <https://docs.docker.com/compose/install/>
### Installation

Dillinger requires Docker and Docker-Compose pre-installed.

Enter into downloaded folder.

```sh
$ cd web_app-master
```

And run the microservice
```sh
$ sudo docker-compose build
$ sudo docker-compose up -d 
```
Now the website should be running in the background.
You can verify the deployment by  navigating to your server address in your preferred browser.

```sh
0.0.0.0:5000
```
