from typing import Optional
from labthings_fastapi.utilities.object_reference_to_object import (
    object_reference_to_object)
import uvicorn
from labthings_fastapi.server import ThingServer, server_from_config
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
import os 

config = {"things":{"/camera/":"labthings_picamera2.thing:StreamingPiCamera2"}}
server = server_from_config(config)

# serve static website 
# get current directory 
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
server.app.mount("/static", StaticFiles(directory=static_dir), name="static")  # serve static files such as the swagger UI
origins = [
    "http://localhost:8001",
    "http://localhost:8000",
    "http://localhost",
    "http://localhost:8080",
    "*"
]
server.app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


uvicorn.run(server.app, host="0.0.0.0", port=5000)
