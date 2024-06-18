dev:
	fastapi dev src/main.py
prod:
	fastapi run src/main.py
	

### Docker
d-build:
	docker build -t api:v0.1 .
d-run:
	docker run -d --name mycontainer -p 80:80 api:v0.1
d-ps:
	docker ps