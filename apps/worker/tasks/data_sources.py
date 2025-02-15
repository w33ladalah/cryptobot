from celery import shared_task
from config.settings import config
from devtools import debug
import httpx


@shared_task(name='pull_coins_from_coingecko')
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
