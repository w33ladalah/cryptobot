# Import required libraries
from calendar import c
import os
from celery import Celery
from core.market_data import get_historical_data, get_dexscreener_data, combine_data
from llm.llm_analysis import analyze_with_llm
from config.settings import config

# Initialize Celery app
app = Celery('scheduler', broker=config.CELERY_BROKER_URL, result_backend=config.CELERY_RESULT_BACKEND)

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
