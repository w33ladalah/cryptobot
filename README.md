# Crypto Bot

A bot to analyze market and do auto-buying according to analysis result.

## Overview

Crypto Bot is an automated trading bot designed to analyze market data and execute trades based on predefined strategies. It utilizes LLM to detect trends using data from CoinGecko and DexScreener. It supports multiple cryptocurrencies and integrates with various data sources and trading platforms.

## Features

- **Market Analysis**: Fetches and analyzes market data from sources like CoinGecko and DexScreener.
- **Automated Trading**: Executes buy and sell orders on Ethereum using Uniswap.
- **Data Storage**: Stores analysis results and historical data in a database.
- **Web Interface**: Provides a web interface for monitoring and managing the bot.

## Project Structure

```plaintext
crypto-bot/
├── apps/
│   ├── api/
│   │   ├── alembic/
│   │   ├── config/
│   │   ├── repositories/
│   │   ├── routes/
│   │   ├── schema/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   └── requirements.txt
│   ├── webapp/
│   │   ├── src/
│   │   ├── public/
│   │   ├── index.html
│   │   ├── package.json
│   │   └── vite.config.ts
│   ├── worker/
│   │   ├── core/
│   │   ├── tasks/
│   │   ├── __init__.py
│   │   └── requirements.txt
├── docker/
│   ├── environments/
│   ├── services/
│   ├── docker-compose.yaml
├── scripts/
│   ├── generate_compose_file.sh
│   ├── manage_services.sh
├── env_vars/
│   ├── .env.example
└── README.md
```

## Installation

### Prerequisites

- Docker
- Docker Compose
- Python 3.8+
- Node.js 14+

### Setup

1. Clone the repository:

    ```sh
    git clone https://github.com/w33ladalah/crypto-bot.git
    cd crypto-bot
    ```

2. Copy the example environment variables file and configure it:

    ```sh
    cp env_vars/.env.example env_vars/.env
    ```

3. Build and start the Docker containers:

    ```sh
    ./scripts/generate_compose_file.sh
    ./scripts/manage_services.sh
    ```

## Usage

### API

The API is built with FastAPI and provides endpoints for managing platforms, users, wallets, and analysis results.

- **Base URL**: `/api/v1`
- **Documentation**: `/docs`

### Web Interface

The web interface is built with React and Vite. It provides a dashboard for monitoring the bot's activities.

- **URL**: `http://localhost:1421`

### Worker

The worker is responsible for fetching market data, performing analysis, and executing trades. It uses Celery for task management.

## Configuration

Configuration settings are managed through environment variables. Refer to the `.env.example` file for a list of required variables.

## Contributing

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes.
4. Commit your changes (`git commit -am 'Add new feature'`).
5. Push to the branch (`git push origin feature-branch`).
6. Create a new Pull Request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For any inquiries, please contact Hendro Wibowo at [hendrothemail@gmail.com](mailto:hendrothemail@gmail.com).

## Tags

- Crypto Bot
- Automated Trading
- Market Analysis
- FastAPI
- Docker
- Python
- Node.js
- Cryptocurrency
- Trading Bot
- Open Source
