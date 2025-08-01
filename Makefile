dev:
	docker-compose --env-file .env -f docker/docker-compose.dev.yml -p dev up --build

prod:
	docker-compose --env-file .env -f docker/docker-compose.prod.yml -p prod up -d --build

down-dev:
	docker-compose -f docker/docker-compose.dev.yml down

down-prod:
	docker-compose -f docker/docker-compose.prod.yml down
