from fastapi import FastAPI
from fastapi_mqtt.fastmqtt import FastMQTT
from fastapi_mqtt.config import MQTTConfig
from pydantic import BaseModel

class Input(BaseModel):
    intent: str

class Intent(BaseModel):
    requestId: str
    inputs: list[Input]

MQTT_SERVER_HOSTNAME = "test.mosquitto.org"
MQTT_PUBLISH_TOPIC = "gdg/test"

app = FastAPI()

mqtt_config = MQTTConfig(host=MQTT_SERVER_HOSTNAME)

fast_mqtt = FastMQTT(config=mqtt_config)

fast_mqtt.init_app(app)

@fast_mqtt.on_connect()
def connect(client, flags, rc, properties):
    print("Connected: ", client, flags, rc, properties)

@fast_mqtt.on_message()
async def message(client, topic, payload, qos, properties):
    print("Received message: ",topic, payload.decode(), qos, properties)
    return 0

@fast_mqtt.on_subscribe()
def subscribe(client, mid, qos, properties):
    print("Subscribed", client, mid, qos, properties)

@fast_mqtt.on_disconnect()
def disconnect(client, packet, exc=None):
    print("Disconnected")

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/lights/{lights_state}")
async def control_lights(lights_state):
    fast_mqtt.publish(MQTT_PUBLISH_TOPIC, {"lights_state": lights_state})
    return {"lights_state": lights_state}

@app.post("/assistant")
async def handle_intents(intent: Intent):
    if intent.inputs[0].intent == "action.devices.SYNC":
        response = {"msg": "Hola senior!"}
    else:
        response = intent
    return response
