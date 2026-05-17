import aiosqlite

DB_NAME = "aura.db"

CREATE_USERS = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    public_key TEXT
)
"""

CREATE_MESSAGES = """
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender TEXT,
    receiver TEXT,
    content TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    delivered INTEGER DEFAULT 0,
    synced INTEGER DEFAULT 0
)
"""

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(CREATE_USERS)
        await db.execute(CREATE_MESSAGES)
        await db.commit()

async def save_message(sender, receiver, content):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            """
            INSERT INTO messages
            (sender, receiver, content)
            VALUES (?, ?, ?)
            """,
            (sender, receiver, content)
        )
        await db.commit()

async def load_messages():
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "SELECT sender, content FROM messages"
        )
        return await cursor.fetchall()
import asyncio
import websockets

clients = set()

async def handler(websocket):
    clients.add(websocket)

    try:
        async for message in websocket:

            for client in clients:
                if client != websocket:
                    await client.send(message)

    finally:
        clients.remove(websocket)

async def main():
    async with websockets.serve(
        handler,
        "0.0.0.0",
        8765
    ):
        print("Aura server started")
        await asyncio.Future()

asyncio.run(main())
import asyncio
import websockets

SERVER = "ws://127.0.0.1:8765"

async def send_message(message):
    async with websockets.connect(SERVER) as ws:
        await ws.send(message)

async def receive_messages(callback):

    async with websockets.connect(SERVER) as ws:

        while True:
            msg = await ws.recv()
            callback(msg)
pending_messages = []

def queue_message(msg):
    pending_messages.append(msg)

def get_pending():
    return pending_messages

def clear_pending():
    pending_messages.clear()
import asyncio

from messaging.queue import (
    get_pending,
    clear_pending
)

from networking.client import send_message

async def sync_pending():

    while True:

        pending = get_pending()

        if pending:

            for msg in pending:
                try:
                    await send_message(msg)
                except:
                    break

            clear_pending()

        await asyncio.sleep(5)
from zeroconf import Zeroconf, ServiceInfo
import socket

def register_service():

    zeroconf = Zeroconf()

    info = ServiceInfo(
        "_auralink._tcp.local.",
        "AuraLink._auralink._tcp.local.",
        addresses=[socket.inet_aton("127.0.0.1")],
        port=8765,
        properties={},
    )

    zeroconf.register_service(info)

    return zeroconf
BoxLayout:
    orientation: "vertical"

    ScrollView:

        Label:
            id: messages
            text: ""
            size_hint_y: None
            height: self.texture_size[1]
            text_size: self.width, None

    BoxLayout:
        size_hint_y: None
        height: 50

        TextInput:
            id: input_box

        Button:
            text: "Send"
            on_press: app.send_chat()
import asyncio
import threading

from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock

from database.db import (
    init_db,
    save_message
)

from networking.client import (
    send_message
)

from messaging.queue import queue_message

KV = Builder.load_file("ui/main.kv")

class AuraApp(App):

    def build(self):

        asyncio.run(init_db())

        return KV

    def send_chat(self):

        msg = self.root.ids.input_box.text

        if not msg:
            return

        self.root.ids.messages.text += (
            f"\nYou: {msg}"
        )

        asyncio.run(
            save_message(
                "You",
                "Peer",
                msg
            )
        )

        try:
            asyncio.run(send_message(msg))
        except:
            queue_message(msg)

        self.root.ids.input_box.text = ""

if __name__ == "__main__":
    AuraApp().run()
import asyncio
import websockets

CHUNK = 1024

async def send_file(path):

    async with websockets.connect(
        "ws://127.0.0.1:8765"
    ) as ws:

        with open(path, "rb") as f:

            while chunk := f.read(CHUNK):
                await ws.send(chunk)
async def receive_file(websocket, filename):

    with open(filename, "wb") as f:

        while True:

            chunk = await websocket.recv()

            if chunk == b"EOF":
                break

            f.write(chunk)
from nacl.public import (
    PrivateKey,
    Box
)

private_key = PrivateKey.generate()
public_key = private_key.public_key

def encrypt_message(
    recipient_public,
    message
):

    box = Box(
        private_key,
        recipient_public
    )

    return box.encrypt(
        message.encode()
    )

def decrypt_message(
    sender_public,
    encrypted
):

    box = Box(
        private_key,
        sender_public
    )

    return box.decrypt(
        encrypted
    ).decode()
import pyaudio
import socket

CHUNK = 1024

audio = pyaudio.PyAudio()

stream = audio.open(
    format=pyaudio.paInt16,
    channels=1,
    rate=44100,
    input=True,
    frames_per_buffer=CHUNK
)

sock = socket.socket(
    socket.AF_INET,
    socket.SOCK_DGRAM
)

while True:

    data = stream.read(CHUNK)

    sock.sendto(
        data,
        ("127.0.0.1", 5000)
    )
import cv2
import socket
import pickle

cam = cv2.VideoCapture(0)

sock = socket.socket(
    socket.AF_INET,
    socket.SOCK_DGRAM
)

while True:

    ret, frame = cam.read()

    data = pickle.dumps(frame)

    sock.sendto(
        data,
        ("127.0.0.1", 6000)
    )
from bleak import BleakScanner

async def scan():

    devices = await BleakScanner.discover()

    for d in devices:
        print(d)
from llama_cpp import Llama

llm = Llama(
    model_path="models/tinyllama.gguf"
)

def ask(prompt):

    output = llm(
        prompt,
        max_tokens=64
    )

    return output
pip install buildozer
buildozer init
buildozer android debug
