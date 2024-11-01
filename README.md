# goit-pythonweb-hw-03

## Basic Web Server with jinja template engine

### Description

Requests to `/` and `/message.html` endpoints returns crafted html pages.
Requets to `/read` endpoint returns rendered template with information from data.json.

### Running the server

Data for the server is stored in `storage/data.json` file. The file is mounted to the server container using a volume on docker-compose.
For simplifying running the server, docker-compose is used. To run the server, execute the following command:

```bash
docker-compose up
```

If you want to run the server without docker-compose, you can use the following commands:

```bash
cd WebServer
docker build . -t olexandrs-webserver
docker run \
    --name olexandrs-webserver \
    --rm \
    -p 3000:3000 \
    -v ./storage:/app/storage \
    olexandrs-webserver 
```
