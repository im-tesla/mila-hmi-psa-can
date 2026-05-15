import asyncio
import json
import time
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from serial_reader import SerialReader
import uvicorn

app = FastAPI()
clients: list[WebSocket] = []
reader = SerialReader()


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    clients.append(ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        clients.remove(ws)


async def broadcast(frame_json: str):
    for ws in clients:
        try:
            await ws.send_text(frame_json)
        except Exception:
            clients.remove(ws)


async def can_loop():
    """Read CAN frames from serial and broadcast to WebSocket clients."""
    reader.open()
    loop = asyncio.get_event_loop()
    while True:
        frame = await loop.run_in_executor(None, reader.read_frame)
        if frame is not None:
            from can_parser import parse_frame
            parsed = parse_frame(frame.can_id, frame.data)
            msg = {
                "id": f"0x{frame.can_id:03X}",
                "ts": time.time(),
                "data": parsed,
                "raw": " ".join(f"{b:02X}" for b in frame.data[:frame.dlen])
            }
            asyncio.create_task(broadcast(json.dumps(msg)))
        await asyncio.sleep(0.001)


@app.on_event("startup")
async def startup():
    asyncio.create_task(can_loop())


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8765)
