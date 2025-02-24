from fastapi import FastAPI
from routes import TokenPairRouters, \
                    TokenRouters, \
                    PlatformRouters, \
                    DataSourceRouters, \
                    AnalysisRouters
from config.settings import config


app = FastAPI(root_path=config.API_PREFIX_URL)
app.version = config.API_VERSION
app.title = "Cryptobot API"
app.description = "An API for Cryptobot."


@app.get("/", status_code=200)
async def index():
    return {"message": "Hello World!"}


app.include_router(TokenRouters)
app.include_router(TokenPairRouters)
app.include_router(PlatformRouters)
app.include_router(DataSourceRouters)
app.include_router(AnalysisRouters)
