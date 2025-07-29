dev:
	docker-compose --env-file .env -f docker/docker-compose.dev.yml up --build

prod:
	docker-compose --env-file .env -f docker/docker-compose.prod.yml up -d --build

down-dev:
	docker-compose -f docker/docker-compose.dev.yml down

down-prod:
	docker-compose -f docker/docker-compose.prod.yml down
