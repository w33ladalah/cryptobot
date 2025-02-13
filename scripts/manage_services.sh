#!/bin/bash

COMPOSE_FILE="${COMPOSE_FILE:-./docker/run-development-compose.yaml}"

docker compose -f "${COMPOSE_FILE}" up
