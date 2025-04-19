from fastapi import FastAPI, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from database.db_connection import get_db
from database import schema
from database.db_connection import engine, Base, get_db
from fastapi.middleware.cors import CORSMiddleware
from typing import Annotated
from api.user_api import router
from routes.luco_user import user_router
from routes.luco_send_sms.sms_send import sms_router
from routes.luco_sms import luco_router
from routes.promos.promo_code import promo_router
from controller.auto_delete import auto_delete_router
import asyncio
import httpx
import logging
import os
from contextlib import asynccontextmanager


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


APP_URL = os.environ.get("APP_URL", "https://luco-sms-api.onrender.com/docs")

# Keep-alive ping interval in seconds (10 minutes = 600 seconds)
# Set this lower than the 14-minute shutdown time
PING_INTERVAL = 600

Base.metadata.create_all(bind=engine)


async def keep_alive():
    """Task that pings the app URL periodically to keep it alive."""
    async with httpx.AsyncClient() as client:
        while True:
            try:
                logger.info(f"Sending keep-alive ping to {APP_URL}/health")
                response = await client.get(f"{APP_URL}/health")
                logger.info(f"Keep-alive response: {response.status_code}")
            except Exception as e:
                logger.error(f"Keep-alive ping failed: {str(e)}")
            
            
            await asyncio.sleep(PING_INTERVAL)

@asynccontextmanager
async def lifespan(app: FastAPI):
    
    task = asyncio.create_task(keep_alive())
    yield
    
    task.cancel()

# Create the FastAPI app with lifespan
app = FastAPI(lifespan=lifespan)

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

# Add a health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok"}

app.include_router(router=user_router)
app.include_router(router=sms_router)
app.include_router(router=router)
app.include_router(router=luco_router)
app.include_router(router=promo_router)
app.include_router(router=auto_delete_router)
