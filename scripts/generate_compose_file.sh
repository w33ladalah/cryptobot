#!/bin/bash

# =============================================================================
# Script Name: generate_compose_file.sh
# Author: Hendro Wibowo <hendrothemail@gmail.com>
# Description: Script to generate docker compose files.
# =============================================================================

# Exit the script on any error
set -e

# Check if the script is running in the root directory
if [ ! -f .root_dir ]; then
  echo "Error: This script must be run from the root directory."
  exit 1
fi

echo "Generating docker compose files..."

# Parse command line arguments
while getopts "e:p:f:h:o" opt; do
  case $opt in
    e) ENV_NAME=$OPTARG ;;
    p) PROJECT_NAME=$OPTARG ;;
    f) ENV_FILE=$OPTARG ;;
    o) OUTPUT_FILE=$OPTARG ;;
    h)
      echo "Usage: $0 [-e environment] [-p project_name] [-f env_file]"
      echo "  -e  Environment name (default: development)"
      echo "  -p  Project name (default: cryptobot-development)"
      echo "  -f  .env file location (default: ./env_vars/.env)"
      exit 0
      ;;
    *) echo "Invalid option: -$OPTARG" >&2; exit 1 ;;
  esac
done

# Prompt the user to enter the environment name if not provided as an argument
if [ -z "$ENV_NAME" ]; then
  echo "Enter the environment (default: development):"
  read -r ENV_NAME
fi

# If no environment name is provided, use 'development' as default
ENV_NAME=${ENV_NAME:-development}

echo "Selected environment: $ENV_NAME"

# Prompt the user for the project name if not provided as an argument
if [ -z "$PROJECT_NAME" ]; then
  default_project_name="cryptobot-development"
  read -r -p "Enter the project name (default: $default_project_name): " PROJECT_NAME
  PROJECT_NAME=${PROJECT_NAME:-$default_project_name}
fi

echo "Selected project name: $PROJECT_NAME"

# Prompt the user for the .env file location if not provided as an argument
if [ -z "$ENV_FILE" ]; then
  default_env_file="./env_vars/.env"
  read -r -p "Enter the .env file location (default: $default_env_file): " ENV_FILE
  ENV_FILE=${ENV_FILE:-$default_env_file}
fi

echo "Selected .env file location: $ENV_FILE"

# Set default output file name based on environment
if [ -n "$ENV_NAME" ]; then
    case $ENV_NAME in
        development)
            echo "Environment: Development"
            services=("api" "db" "adminer" "worker" "frontend")
            default_output_file="./docker/run-development-compose.yaml"
            ;;
        staging)
            echo "Environment: Staging"
            services=("api" "db" "adminer" "worker" "frontend")
            default_output_file="./docker/run-staging-compose.yaml"
            ;;
        production)
            echo "Environment: Production"
            services=("api" "db" "worker" "frontend")
            default_output_file="./docker/run-production-compose.yaml"
            ;;
        custom)
            echo "Environment: Custom"
            services=()
            # Show available services for custom selection
            echo "Available services:"
            echo "1. adminer: Adminer database management tool"
            echo "2. api: The backend API for the bot"
            echo "3. db: The MySQL database"
            echo "4. frontend: web page"
            echo "5. worker: The bot worker"
            echo ""

            # Let the user select services by number
            while true; do
                echo "Enter the service number to add (or type 'done' to finish):"
                read -r service_number
                if [ "$service_number" == "done" ]; then
                    break
                fi
                case $service_number in
                    1) services+=("adminer") ;;
                    2) services+=("api") ;;
                    3) services+=("db") ;;
                    4) services+=("frontend") ;;
                    5) services+=("worker") ;;
                    *) echo "Invalid service number. Please try again." ;;
                esac
            done
            default_output_file="./docker/run-custom-compose.yaml"
            ;;
        *)
            echo "Invalid environment name. Exiting."
            exit 1
            ;;
    esac
else
    # Prompt the user to select an environment
    echo "Select the environment:"
    echo "1. Development (predefined services)"
    echo "2. Staging (predefined services)"
    echo "3. Production (predefined services)"
    echo "4. Custom (choose your own services)"
    read -r -p "Enter the environment (1, 2, 3, or 4) (default: 1): " env_choice
    env_choice=${env_choice:-1}
    case $env_choice in
        1)
            echo "Environment: Development"
            services=("api" "db" "adminer" "worker" "frontend")
            default_output_file="./docker/run-development-compose.yaml"
            ;;
        2)
            echo "Environment: Staging"
            services=("api" "db" "adminer" "worker" "frontend")
            default_output_file="./docker/run-staging-compose.yaml"
            ;;
        3)
            echo "Environment: Production"
            services=("api" "db" "worker" "frontend")
            default_output_file="./docker/run-production-compose.yaml"
            ;;
        4)
            echo "Environment: Custom"
            services=()
            # Show available services for custom selection
            echo "Available services:"
            echo "1. adminer: Adminer database management tool"
            echo "2. api: The backend API for the bot"
            echo "3. db: The MySQL database"
            echo "4. frontend: web page"
            echo "5. worker: The bot worker"
            echo ""

            # Let the user select services by number
            while true; do
                echo "Enter the service number to add (or type 'done' to finish):"
                read -r service_number
                if [ "$service_number" == "done" ]; then
                    break
                fi
                case $service_number in
                    1) services+=("adminer") ;;
                    2) services+=("api") ;;
                    3) services+=("db") ;;
                    4) services+=("frontend") ;;
                    5) services+=("worker") ;;
                    *) echo "Invalid service number. Please try again." ;;
                esac
            done
            default_output_file="./docker/run-custom-compose.yaml"
            ;;
        *)
            echo "Invalid environment choice. Exiting."
            exit 1
            ;;
    esac
fi

if [ -z "$OUTPUT_FILE" ]; then
    # Prompt the user for the output file name (with default based on environment)
    read -r -p "Enter the output file name (default: $default_output_file): " OUTPUT_FILE
    OUTPUT_FILE=${OUTPUT_FILE:-$default_output_file}
fi

# Ensure OUTPUT_FILE has a value
OUTPUT_FILE=${OUTPUT_FILE:-$default_output_file}

# Generate the file list based on selected services
files=""
for service in "${services[@]}"; do
    files="$files -f ./docker/services/$service.yaml"
done

# Generate the final command
base_command="docker compose --project-name $PROJECT_NAME --env-file $ENV_FILE"
final_command="$base_command $files config > $OUTPUT_FILE"

# Display the generated command
echo "Generated command:"
echo "$final_command"

# Optionally, execute the command
echo "Do you want to execute the command? (yes/no)"
read -r -p "Enter your choice (default: yes): " execute_choice
execute_choice=${execute_choice:-yes}

if [ "$execute_choice" == "yes" ]; then
    eval "$final_command"
fi

echo "Docker compose file for environment '$ENV_NAME' generated successfully."
