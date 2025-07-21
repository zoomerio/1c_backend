import configparser
import sys
from fastapi import FastAPI, HTTPException

from models import UserRepr
from utils import create_or_update_config_file
from loguru import logger
from KeycloakApi import KeycloakAPI

create_or_update_config_file("config.ini")
config = configparser.ConfigParser()
config.read("config.ini")
log_level = config.get("LOGGER", "log_level")
logger.remove()
logger.add(config["LOGGER"]["log_file"], rotation="256 MB", enqueue=True, format="{time:HH:mm:ss DD.MM.YYYY} | {level} | {message}", level=log_level)
logger.add(sys.stdout, enqueue=True, format="<yellow>{time:HH:mm:ss DD.MM.YYYY}</> | <lvl>{level}</> | <green>{message}</>", level=log_level, colorize=True)

app = FastAPI()
KeycloakAPI = KeycloakAPI("config.ini")

@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.post("/add_user")
async def handle_add_user(user: UserRepr):
    await KeycloakAPI.add_user(user)
