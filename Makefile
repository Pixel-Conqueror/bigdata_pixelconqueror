PROJECT_NAME=bigdata-env

build:
	docker build -t $(PROJECT_NAME) .

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f
	
clean:
	docker-compose down --rmi all --volumes --remove-orphans
	docker system prune -af

shell:
	docker exec -it bigdata-container bash