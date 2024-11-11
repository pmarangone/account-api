dev:
	fastapi dev src/main.py
prod:
	fastapi run src/main.py
test:
	python3 -m unittest tests/test_db_wrapper.py

uvicorn:
	uvicorn src.main:app --reload --log-level trace
	

### Docker
d-build:
	docker build -t api:v0.1 .
d-run:
	docker run -d --name mycontainer -p 80:80 api:v0.1
d-ps:
	docker ps

### Docker Compose
dc-build:
	docker compose up --detach
dc-watch:
	docker compose up --watch
dc-clean:
	docker compose down --volumes
dc-new:
	docker compose down --volumes && docker compose up --watch
	
### General
rm-unused:
	autoflake --in-place --remove-all-unused-imports --remove-unused-variables -r src/