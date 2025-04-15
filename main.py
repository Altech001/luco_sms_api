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
from routes.promos.promo_code import promo_router

Base.metadata.create_all(bind=engine)


app = FastAPI()



origins = [
    "*",
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root(db: Session = Depends(get_db)):
    return {
        "message":"Welcome to the Luco SMS API",
        "version":"1.0.0",
        "author":"Abaasa Albert",
        "description":"This is an API for sending SMS messages and managing user accounts.",
        "documentation":"https://lucosms.com/docs",
        }


app.include_router(router=user_router)
app.include_router(router=router)
app.include_router(router=luco_router)
app.include_router(router=promo_router)