#!/bin/bash

COMPOSE_FILE="${COMPOSE_FILE:-./docker/run-development-compose.yaml}"

docker compose -f "${COMPOSE_FILE}" down
docker rmi -f cryptobot-development-worker
docker compose -f "${COMPOSE_FILE}" up -d
docker compose -f "${COMPOSE_FILE}" logs -f
