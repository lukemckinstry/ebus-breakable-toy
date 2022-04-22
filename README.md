# Electric Buses - A Breakable Toy

## Description

Collects municipal bus transit routes and facilitates anotation to show adoption of electric vehicles for passenger service 

## Getting Started

### Dependencies

* Docker

### Installing

* Build containers 
```
docker-compose build
```

### Executing program

* Run containers 
```
docker-compose up
```
* Run migrations, create superuser, collect static files
```
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py collectstatic
```
* Download sample gtfs data 

```
docker-compose exec web python manage.py loadfeeds --sample
```
* Download sample gtfs data 

```
docker-compose exec web python manage.py loadfeeds --sample
```
Open [http://localhost:9202](http://localhost:9202) to view it in the browser.