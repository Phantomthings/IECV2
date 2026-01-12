from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
from starlette.requests import Request
from fastapi.responses import HTMLResponse
import logging

from opcua_client import OPCUAClient
from config import OPCUA_SERVER_URL
from routers import sequences, exploitation, communication, system, synoptique

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

opcua_client = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global opcua_client
    opcua_client = OPCUAClient(OPCUA_SERVER_URL)
    await opcua_client.connect()
    yield
    await opcua_client.disconnect()

app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.include_router(sequences.router)
app.include_router(exploitation.router)
app.include_router(communication.router)
app.include_router(system.router)
app.include_router(synoptique.router)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("sequences.html", {"request": request})

def get_opcua_client():
    return opcua_client