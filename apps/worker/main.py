from devtools import debug
from celery import Celery
from core.market_data import get_historical_data, get_dexscreener_data, combine_data
from llm.llm_analysis import analyze_with_llm
from config.settings import config
import httpx

# Initialize Celery app
app = Celery(
    'crypto_bot',
    broker=config.CELERY_BROKER_URL,
    result_backend=config.CELERY_RESULT_BACKEND
)

# Define a task using the @shared_task decorator
@app.task(name='perform_analysis')
def perform_analysis(token_id, chain, pair_address):
    # Fetch data
    historical_data = get_historical_data(token_id, days=30)
    real_time_data = get_dexscreener_data(chain, pair_address)

    # Process data
    combined_data = combine_data(historical_data, real_time_data)

    # LLM-based analysis
    analysis_result = analyze_with_llm(token_id, chain, pair_address, combined_data)

    return analysis_result


@app.task(name='pull_coins_from_coingecko')
def pull_platform_from_coingecko():
    response = httpx.get(f"{config.COINGECKO_API}/coins/list?include_platform=true")
    response.raise_for_status()
    data = response.json()
    platforms = []
    for item in data:
        if item['platforms']:
            for platform_name, address in item.get("platforms", {}).items():
                try:
                    platform_response = httpx.post(f"{config.API_URL}/platforms/", json={
                        "name": platform_name,
                        "address": address})
                    platform_response.raise_for_status()
                    platform_data = platform_response.json()
                    platforms.append(platform_data)
                except Exception as e:
                    debug(f"An error occurred: {e}")

    return platforms
