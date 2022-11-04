# main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from DB import models
from DB.SqlAlchemy import engine
from ROUTES.environment import router as env_router
from ROUTES.map import router as map_router

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.mount('/static', StaticFiles(directory='static'), name='static')
app.include_router(env_router)
app.include_router(map_router)


@app.get("/")
async def root():
    return {"message": "Library API to store maps"}
