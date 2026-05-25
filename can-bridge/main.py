import asyncio
import json
import time
import os
import random
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from serial_reader import SerialReader
from config import load_config, save_config, get_config, Config
import uvicorn

try:
    from can_parser import parse_frame, encode_signal
    from can_definitions import CAN_DEFINITIONS
except ImportError:
    def parse_frame(can_id, data):
        return {}
    def encode_signal(data, byte_offset, bit_offset, bit_length, raw_value):
        pass
    CAN_DEFINITIONS = {}

app = FastAPI()
clients: list[WebSocket] = []
reader = SerialReader()

_loop_task: asyncio.Task | None = None
_connection_status: str = 'simulation'
_connection_error: str = ''
_last_frames: dict[int, bytearray] = {}


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    clients.append(ws)
    try:
        while True:
            text = await ws.receive_text()
            try:
                msg = json.loads(text)
            except Exception:
                continue
            if msg.get("type") == "write":
                await handle_write(msg)
    except WebSocketDisconnect:
        clients.remove(ws)


async def broadcast(frame_json: str):
    for ws in clients[:]:
        try:
            await ws.send_text(frame_json)
        except Exception:
            clients.remove(ws)


async def handle_write(msg: dict) -> None:
    try:
        can_id_str: str = msg["canId"]
        signal_name: str = msg["signal"]
        raw_value: int = int(msg["rawValue"])
    except (KeyError, ValueError, TypeError):
        return

    try:
        can_id_int = int(can_id_str, 16)
    except ValueError:
        return

    if can_id_int not in CAN_DEFINITIONS:
        return

    sig_def = next((s for s in CAN_DEFINITIONS[can_id_int] if s[0] == signal_name), None)
    if sig_def is None:
        return

    _, byte_off, bit_off, bit_len, *_ = sig_def

    frame_data = bytearray(_last_frames.get(can_id_int, bytearray(8)))
    encode_signal(frame_data, byte_off, bit_off, bit_len, raw_value)
    _last_frames[can_id_int] = bytearray(frame_data)

    reader.write_frame(can_id_int, bytes(frame_data))

    parsed = parse_frame(can_id_int, bytes(frame_data))
    reply = {
        "id": can_id_str,
        "ts": time.time(),
        "data": parsed,
        "raw": " ".join(f"{b:02X}" for b in frame_data),
    }
    asyncio.create_task(broadcast(json.dumps(reply)))


# ---------------------------------------------------------------------------
# REST API
# ---------------------------------------------------------------------------

@app.get("/api/ports")
async def list_ports():
    try:
        from serial.tools import list_ports
        return [{"port": p.device, "description": p.description or p.device}
                for p in list_ports.comports()]
    except Exception:
        return []


@app.get("/api/config")
async def get_config_endpoint():
    cfg = get_config()
    return {
        "simulation": cfg.simulation,
        "port": cfg.port,
        "baudrate": cfg.baudrate,
        "status": _connection_status,
        "error": _connection_error,
    }


class ConfigUpdate(BaseModel):
    simulation: bool
    port: str
    baudrate: int


@app.post("/api/config")
async def update_config_endpoint(body: ConfigUpdate):
    global _loop_task, _connection_status, _connection_error

    cfg = Config(simulation=body.simulation, port=body.port, baudrate=body.baudrate)

    # Cancel current loop task
    if _loop_task and not _loop_task.done():
        _loop_task.cancel()
        try:
            await _loop_task
        except asyncio.CancelledError:
            pass

    reader.close()

    if cfg.simulation:
        await asyncio.get_event_loop().run_in_executor(None, save_config, cfg)
        _connection_status = 'simulation'
        _connection_error = ''
        _loop_task = asyncio.create_task(sim_loop())
        effective_simulation = True
    else:
        try:
            reader.open(cfg.port, cfg.baudrate)
            await asyncio.get_event_loop().run_in_executor(None, save_config, cfg)
            _connection_status = 'ok'
            _connection_error = ''
            _loop_task = asyncio.create_task(can_loop())
            effective_simulation = False
        except Exception as e:
            _connection_status = 'error'
            _connection_error = str(e)
            _loop_task = asyncio.create_task(sim_loop())
            effective_simulation = True
            print(f"[WARN] Could not open {cfg.port}: {e} — falling back to simulation")

    return {
        "simulation": effective_simulation,
        "port": cfg.port,
        "baudrate": cfg.baudrate,
        "status": _connection_status,
        "error": _connection_error,
    }


# ---------------------------------------------------------------------------
# Simulation frames
# ---------------------------------------------------------------------------

SIM_FRAMES = {
    0x036: bytes([0x00, 0x00, 0x00, 0x31, 0x01, 0x00, 0x00, 0xA0]),
    0x0B6: bytes([0x03, 0x4A, 0x00, 0x3E, 0x01, 0x6E, 0x44, 0x80]),
    0x0E1: bytes([0x95, 0x10, 0x3F, 0x49, 0x49, 0x9B, 0x00, 0x00]),
    0x0E6: bytes([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]),
    0x0E8: bytes([0x00, 0x00, 0x00, 0x00, 0x20, 0x00, 0x00, 0x00]),
    0x0F6: bytes([0x42, 0x5E, 0x12, 0x34, 0x56, 0x00, 0x12, 0x80]),
    0x10B: bytes([0x80, 0x00, 0x00, 0x06, 0x00, 0x00, 0x00, 0x00]),
    0x120: bytes([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]),
    0x126: bytes([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]),
    0x127: bytes([0x00, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]),
    0x128: bytes([0x00, 0x00, 0x00, 0x00, 0x60, 0x00, 0x0C, 0x00]),
    0x136: bytes([0x00, 0xFA, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]),
    0x161: bytes([0x00, 0x00, 0x50, 0x3C, 0x00, 0x00, 0x60, 0x00]),
    0x167: bytes([0x00, 0x00, 0x01, 0x2C, 0x00, 0x00, 0x00, 0x00]),
    0x168: bytes([0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00]),
    0x1A1: bytes([0x00, 0xFF, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]),
    0x1A8: bytes([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]),
    0x1E3: bytes([0x11, 0x08, 0x10, 0x10, 0x30, 0x30, 0x05, 0x00]),
    0x217: bytes([0x70, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]),
    0x21F: bytes([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]),
    0x220: bytes([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]),
    0x221: bytes([0x00, 0x44, 0x00, 0xA0, 0x02, 0x58, 0x00, 0x00]),
    0x227: bytes([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]),
    0x228: bytes([0x0E, 0x21, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]),
    0x260: bytes([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]),
    0x261: bytes([0x2D, 0x01, 0xF4, 0x00, 0x50, 0x02, 0x00, 0x00]),
    0x297: bytes([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]),
    0x2A1: bytes([0x2A, 0x02, 0xBC, 0x00, 0x48, 0x03, 0x00, 0x00]),
    0x2B6: bytes([0x56, 0x46, 0x33, 0x00, 0x00, 0x00, 0x00, 0x00]),
    0x2E1: bytes([0xFF, 0x55, 0xA9, 0x00, 0x00, 0x00, 0x00, 0x00]),
    0x336: bytes([0x56, 0x46, 0x33, 0x00, 0x00, 0x00, 0x00, 0x00]),
    0x361: bytes([0x01, 0x00, 0x0D, 0x00, 0x00, 0x02, 0x00, 0x00]),
    0x3A7: bytes([0x00, 0x00, 0x00, 0x1F, 0x40, 0x01, 0x2C, 0x00]),
    0x3B6: bytes([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]),
    0x760: bytes([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]),
}


async def sim_loop():
    print("[SIM] Simulation mode active")
    ids = list(SIM_FRAMES.keys())
    i = 0
    while True:
        can_id = ids[i % len(ids)]
        data = bytearray(SIM_FRAMES[can_id])

        if can_id == 0x0B6:
            rpm = 800 + random.randint(-50, 100)
            speed = 50 + random.randint(-5, 15)
            data[0] = (rpm >> 8) & 0xFF
            data[1] = rpm & 0xFF
            data[2] = 0
            data[3] = speed
        if can_id == 0x0F6:
            data[1] = 85 + random.randint(-3, 5)

        parsed = parse_frame(can_id, bytes(data))
        _last_frames[can_id] = bytearray(data)
        msg = {
            "id": f"0x{can_id:03X}",
            "ts": time.time(),
            "data": parsed,
            "raw": " ".join(f"{b:02X}" for b in data[:8]),
        }
        asyncio.create_task(broadcast(json.dumps(msg)))
        i += 1
        await asyncio.sleep(0.15)


async def can_loop():
    """Read CAN frames from serial and broadcast to WebSocket clients."""
    global _loop_task, _connection_status, _connection_error
    loop = asyncio.get_event_loop()
    while True:
        try:
            frame = await loop.run_in_executor(None, reader.read_frame)
        except Exception as e:
            print(f"[CAN] Serial read error: {e}")
            _connection_status = 'error'
            _connection_error = str(e)
            asyncio.create_task(broadcast(json.dumps({"_type": "status", "status": "error", "error": str(e)})))
            _loop_task = asyncio.create_task(sim_loop())
            break
        if frame is not None:
            parsed = parse_frame(frame.can_id, frame.data)
            _last_frames[frame.can_id] = bytearray(frame.data[:8])
            msg = {
                "id": f"0x{frame.can_id:03X}",
                "ts": time.time(),
                "data": parsed,
                "raw": " ".join(f"{b:02X}" for b in frame.data[:frame.dlen]),
            }
            asyncio.create_task(broadcast(json.dumps(msg)))
        await asyncio.sleep(0.001)


# ---------------------------------------------------------------------------
# Startup
# ---------------------------------------------------------------------------

@app.on_event("startup")
async def startup():
    global _loop_task, _connection_status, _connection_error
    cfg = load_config()
    if cfg.simulation or not cfg.port:
        _connection_status = 'simulation'
        _loop_task = asyncio.create_task(sim_loop())
        print("[SIM] Simulation mode active — configure a port in Settings to use real CAN data")
    else:
        try:
            reader.open(cfg.port, cfg.baudrate)
            _connection_status = 'ok'
            _loop_task = asyncio.create_task(can_loop())
            print(f"[CAN] Reading from {cfg.port} at {cfg.baudrate} baud")
        except Exception as e:
            _connection_status = 'error'
            _connection_error = str(e)
            _loop_task = asyncio.create_task(sim_loop())
            print(f"[WARN] Could not open {cfg.port}: {e} — falling back to simulation")


# Serve built frontend static files
static_dir = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'dist')
if os.path.exists(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8765)
