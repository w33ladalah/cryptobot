from fastapi import FastAPI

from routes import TokenPairRouters
from routes import TokenRouters
from routes import PlatformRouters

app = FastAPI(path="/")
app.version = "0.0.1"
app.title = "Cryptobot API"
app.description += "An API for Cryptobot."

@app.get("/", status_code=200)
async def index():
    return {"message": "Hello World!"}

app.include_router(TokenRouters)
app.include_router(TokenPairRouters)
app.include_router(PlatformRouters)
