from llm.adapter.llama import LlamaAdapter


def analyze_sentiment(twitter_text, discord_text):
    prompt = f"""
    Analyze the sentiment of the following crypto-related messages:
    - Twitter: {twitter_text}
    - Discord: {discord_text}

    Provide a score (-1: Bearish, 0: Neutral, +1: Bullish).
    """
    ollama = LlamaAdapter(model="llama3", system_prompt="You are a sentiment analysis AI.")
    return ollama.chat(model="llama3", messages=[{"role": "user", "content": prompt}])['message']['content']


if __name__ == "__main__":
    print(analyze_sentiment("Bitcoin is going to the moon!", "Market looking strong."))
