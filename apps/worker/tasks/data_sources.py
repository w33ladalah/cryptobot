import traceback
from turtle import ht
from celery import shared_task
from config.settings import config
from devtools import debug
import httpx


@shared_task(name='pull_coins_from_coingecko')
def pull_platform_from_coingecko():
    try:
        response = httpx.get(f"{config.COINGECKO_API}/coins/list?include_platform=true")
        response.raise_for_status()
        data = response.json()

        tokens = []
        for item in data:
            try:
                platforms = []
                if item.get("platforms"):
                    for name, platform in item["platforms"].items():
                        platforms.append({
                            "name": name,
                            "address": platform
                        })
                item["platforms"] = platforms

                token_data = {
                    "alias_id": item["id"],
                    "name": item["name"],
                    "symbol": item["symbol"],
                    "platforms": item["platforms"]
                }

                debug(token_data)

                token = httpx.post(f"{config.API_URL}/tokens/", headers={
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                    }, json=token_data)
                token.raise_for_status()
                token_response = token.json()
                tokens.append(token_response)
            except Exception as e:
                debug(e)

        return tokens
    except Exception as e:
        debug(e)
        traceback.print_exc()
        return None
