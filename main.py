from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database.db_connection import get_db
from database import schema
from database.db_connection import engine, Base, get_db
from fastapi.middleware.cors import CORSMiddleware
from typing import Annotated
from api.user_api import router
from routes.luco_user import user_router
from routes.luco_sms import luco_router

Base.metadata.create_all(bind=engine)


app = FastAPI()



origins = [
    "",
    "",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router=user_router)
app.include_router(router=router)
app.include_router(router=luco_router)