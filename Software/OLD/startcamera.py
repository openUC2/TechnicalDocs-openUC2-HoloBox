from typing import Optional
from labthings_fastapi.utilities.object_reference_to_object import (
    object_reference_to_object)
import uvicorn
from labthings_fastapi.server import ThingServer, server_from_config

config = {"things":{"/camera/":"labthings_picamera2.thing:StreamingPiCamera2"}}
server = server_from_config(config)
uvicorn.run(server.app, host="0.0.0.0", port=5000)
