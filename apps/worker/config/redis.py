from config.settings import config
import redis


# Initialize Redis client
redis_client = redis.StrictRedis(host=config.REDIS_HOST,
                                 password=config.REDIS_PASSWORD.get_secret_value(), \
                                 port=config.REDIS_PORT,
                                 db=config.REDIS_DB)
