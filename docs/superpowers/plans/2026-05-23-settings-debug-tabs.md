# Settings & Debug Tabs Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a Settings tab (serial port selection, simulation toggle, baud rate) and a Debug tab (live raw CAN frame stream) to the web HMI, making the system production-ready for in-car Raspberry Pi use while staying testable on macOS.

**Architecture:** Backend adds a runtime config module + three REST endpoints (`/api/ports`, `GET /api/config`, `POST /api/config`) that hot-restart the CAN reader without restarting the server. Frontend replaces the connection bar with a three-tab top bar (DASHBOARD | DEBUG | SETTINGS) wiring the new panels into the existing WebSocket message flow.

**Tech Stack:** Python 3.11+, FastAPI 0.115, pyserial 3.5, pytest; Vanilla JS ES modules, Vite 5, Tailwind CSS.

---

## File Map

| File | Action | Responsibility |
|---|---|---|
| `can-bridge/config.py` | Create | Runtime config dataclass; load/save `config.json` |
| `can-bridge/test_config.py` | Create | Unit tests for config load/save/defaults |
| `can-bridge/serial_reader.py` | Modify | Accept `port`/`baudrate` at `open()` instead of `__init__` |
| `can-bridge/main.py` | Modify | Remove hardcoded sim detection; add 3 API endpoints; hot-restart logic |
| `frontend/src/components/tab-bar.js` | Create | Top bar: LED + tab buttons + theme toggle |
| `frontend/src/components/settings-panel.js` | Create | Simulation toggle, port dropdown, baud rate, apply |
| `frontend/src/components/debug-panel.js` | Create | Live raw frame table, filter, pause/resume, clear |
| `frontend/src/components/connection-bar.js` | Delete | Replaced by tab-bar |
| `frontend/src/main.js` | Modify | Tab switching; forward WS frames to debug panel; use tab-bar |
| `frontend/src/style.css` | Modify | Add tab button active styles |

---

## Task 1: Backend config module

**Files:**
- Create: `can-bridge/config.py`
- Create: `can-bridge/test_config.py`

- [ ] **Step 1: Write the failing tests**

Create `can-bridge/test_config.py`:

```python
import json
import pytest
import config as cfg_module
from config import Config, load_config, save_config, get_config


@pytest.fixture(autouse=True)
def tmp_config(tmp_path, monkeypatch):
    monkeypatch.setattr(cfg_module, 'CONFIG_PATH', str(tmp_path / 'config.json'))


def test_load_defaults_when_no_file():
    c = load_config()
    assert c.simulation is True
    assert c.port == ''
    assert c.baudrate == 115200


def test_get_config_returns_loaded():
    load_config()
    c = get_config()
    assert c.simulation is True


def test_save_and_reload():
    save_config(Config(simulation=False, port='/dev/ttyUSB0', baudrate=230400))
    c = load_config()
    assert c.simulation is False
    assert c.port == '/dev/ttyUSB0'
    assert c.baudrate == 230400


def test_load_tolerates_corrupt_file():
    with open(cfg_module.CONFIG_PATH, 'w') as f:
        f.write('not json')
    c = load_config()
    assert c.simulation is True
    assert c.baudrate == 115200


def test_save_writes_valid_json(tmp_path):
    save_config(Config(simulation=True, port='COM3', baudrate=9600))
    data = json.loads(open(cfg_module.CONFIG_PATH).read())
    assert data == {'simulation': True, 'port': 'COM3', 'baudrate': 9600}
```

- [ ] **Step 2: Run tests — expect failure (module not found)**

```bash
cd can-bridge && python -m pytest test_config.py -v
```
Expected: `ModuleNotFoundError: No module named 'config'`

- [ ] **Step 3: Create `can-bridge/config.py`**

```python
import json
import os
from dataclasses import dataclass, asdict

CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.json')

_DEFAULTS = {'simulation': True, 'port': '', 'baudrate': 115200}

_config: 'Config | None' = None


@dataclass
class Config:
    simulation: bool
    port: str
    baudrate: int


def get_config() -> 'Config':
    return _config


def load_config() -> 'Config':
    global _config
    try:
        with open(CONFIG_PATH) as f:
            data = json.load(f)
        _config = Config(
            simulation=bool(data.get('simulation', _DEFAULTS['simulation'])),
            port=str(data.get('port', _DEFAULTS['port'])),
            baudrate=int(data.get('baudrate', _DEFAULTS['baudrate'])),
        )
    except (FileNotFoundError, json.JSONDecodeError, ValueError, KeyError):
        _config = Config(**_DEFAULTS)
    return _config


def save_config(cfg: 'Config') -> None:
    global _config
    _config = cfg
    with open(CONFIG_PATH, 'w') as f:
        json.dump(asdict(cfg), f, indent=2)
```

- [ ] **Step 4: Run tests — expect all pass**

```bash
cd can-bridge && python -m pytest test_config.py -v
```
Expected: `5 passed`

- [ ] **Step 5: Commit**

```bash
git add can-bridge/config.py can-bridge/test_config.py
git commit -m "feat: add runtime config module with load/save"
```

---

## Task 2: Update SerialReader

**Files:**
- Modify: `can-bridge/serial_reader.py`

- [ ] **Step 1: Update `serial_reader.py` — remove hardcoded defaults from `__init__`, accept params in `open()`**

Replace the full file content with:

```python
from collections import namedtuple

CanFrame = namedtuple('CanFrame', ['can_id', 'data', 'dlen'])


class SerialReader:
    """Reads binary CAN frames from UART. Non-blocking."""

    def __init__(self):
        self._ser = None

    def open(self, port: str, baudrate: int = 115200):
        import serial
        self._ser = serial.Serial(port, baudrate, timeout=0.01)

    def close(self):
        if self._ser:
            try:
                self._ser.close()
            except Exception:
                pass
            self._ser = None

    def read_frame(self):
        """Read one CAN frame. Returns CanFrame or None if no data."""
        if self._ser is None:
            return None
        header = self._ser.read(3)
        if len(header) < 3:
            return None

        can_id = (header[0] << 8) | header[1]
        dlen = header[2] & 0x0F
        if dlen > 8:
            dlen = 8

        data = self._ser.read(dlen)
        if len(data) < dlen:
            return None

        padded = bytearray(8)
        padded[:len(data)] = data
        return CanFrame(can_id=can_id, data=bytes(padded), dlen=dlen)
```

- [ ] **Step 2: Verify existing parser tests still pass (no regression)**

```bash
cd can-bridge && python -m pytest test_parser.py test_config.py -v
```
Expected: all tests pass (serial_reader isn't imported by the parser tests)

- [ ] **Step 3: Commit**

```bash
git add can-bridge/serial_reader.py
git commit -m "feat: make SerialReader.open() accept port and baudrate at runtime"
```

---

## Task 3: Backend REST API + hot-restart

**Files:**
- Modify: `can-bridge/main.py`

- [ ] **Step 1: Replace `can-bridge/main.py` with the updated version**

```python
import asyncio
import json
import time
import os
import random
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from serial_reader import SerialReader
from config import load_config, save_config, get_config, Config
import uvicorn

try:
    from can_parser import parse_frame
except ImportError:
    def parse_frame(can_id, data):
        return {}

app = FastAPI()
clients: list[WebSocket] = []
reader = SerialReader()

_loop_task: asyncio.Task | None = None
_connection_status: str = 'simulation'
_connection_error: str = ''


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
    for ws in clients[:]:
        try:
            await ws.send_text(frame_json)
        except Exception:
            clients.remove(ws)


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
    save_config(cfg)

    # Cancel current loop task
    if _loop_task and not _loop_task.done():
        _loop_task.cancel()
        try:
            await _loop_task
        except asyncio.CancelledError:
            pass

    reader.close()

    if cfg.simulation:
        _connection_status = 'simulation'
        _connection_error = ''
        _loop_task = asyncio.create_task(sim_loop())
    else:
        try:
            reader.open(cfg.port, cfg.baudrate)
            _connection_status = 'ok'
            _connection_error = ''
            _loop_task = asyncio.create_task(can_loop())
        except Exception as e:
            _connection_status = 'error'
            _connection_error = str(e)
            # Fall back to sim so the UI stays alive
            _loop_task = asyncio.create_task(sim_loop())

    return {
        "simulation": cfg.simulation,
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
    loop = asyncio.get_event_loop()
    while True:
        try:
            frame = await loop.run_in_executor(None, reader.read_frame)
        except Exception as e:
            print(f"[CAN] Serial read error: {e}")
            break
        if frame is not None:
            parsed = parse_frame(frame.can_id, frame.data)
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
```

- [ ] **Step 2: Run all backend tests to confirm no regressions**

```bash
cd can-bridge && python -m pytest test_parser.py test_config.py -v
```
Expected: all pass

- [ ] **Step 3: Manually verify the API is reachable**

Start the server: `cd can-bridge && python main.py`  
In another terminal:
```bash
curl http://localhost:8765/api/config
# Expected: {"simulation":true,"port":"","baudrate":115200,"status":"simulation","error":""}

curl http://localhost:8765/api/ports
# Expected: [] on a machine with no serial adapter, or a list of port objects
```
Stop the server with Ctrl+C.

- [ ] **Step 4: Commit**

```bash
git add can-bridge/main.py
git commit -m "feat: add /api/ports, /api/config REST endpoints with hot-restart"
```

---

## Task 4: Frontend tab-bar component

**Files:**
- Create: `frontend/src/components/tab-bar.js`
- Modify: `frontend/src/style.css`

- [ ] **Step 1: Create `frontend/src/components/tab-bar.js`**

```javascript
export function createTabBar({ onTabChange }) {
  const el = document.createElement('div');
  el.id = 'tab-bar';
  el.className = 'flex items-center justify-between h-10 px-4 text-xs font-mono bg-card border-b border-base select-none shrink-0';
  el.innerHTML = `
    <div class="flex items-center gap-2 w-32">
      <span id="conn-dot" class="led-dot mute"></span>
      <span id="conn-text" class="text-dim uppercase tracking-wider text-[10px]">OFFLINE</span>
    </div>
    <div class="flex items-center gap-1">
      <button data-tab="dashboard" class="tab-btn active-tab px-3 py-1 text-[10px] uppercase tracking-wider rounded transition-colors">Dashboard</button>
      <button data-tab="debug" class="tab-btn px-3 py-1 text-[10px] uppercase tracking-wider rounded transition-colors">Debug</button>
      <button data-tab="settings" class="tab-btn px-3 py-1 text-[10px] uppercase tracking-wider rounded transition-colors">Settings</button>
    </div>
    <div class="w-32 flex justify-end">
      <button id="theme-toggle" class="min-h-touch px-3 text-dim hover:text-accent transition-colors">
        <svg id="theme-sun" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
          <circle cx="12" cy="12" r="5"/>
          <line x1="12" y1="1" x2="12" y2="3"/>
          <line x1="12" y1="21" x2="12" y2="23"/>
          <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/>
          <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
          <line x1="1" y1="12" x2="3" y2="12"/>
          <line x1="21" y1="12" x2="23" y2="12"/>
          <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/>
          <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
        </svg>
        <svg id="theme-moon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" class="hidden">
          <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
        </svg>
      </button>
    </div>
  `;

  const tabs = el.querySelectorAll('.tab-btn');
  tabs.forEach(btn => {
    btn.addEventListener('click', () => {
      tabs.forEach(t => t.classList.remove('active-tab'));
      btn.classList.add('active-tab');
      onTabChange(btn.dataset.tab);
    });
  });

  return el;
}

export function updateTabBarConnection(status) {
  const dot = document.getElementById('conn-dot');
  const text = document.getElementById('conn-text');
  if (!dot || !text) return;
  const states = {
    connected:    { cls: 'ok',         label: 'CONNECTED',    textCls: 'text-ok' },
    connecting:   { cls: 'warn',        label: 'CONNECTING',   textCls: 'text-warn' },
    reconnecting: { cls: 'warn pulse',  label: 'RECONNECTING', textCls: 'text-warn' },
    disconnected: { cls: 'fault',       label: 'OFFLINE',      textCls: 'text-fault' },
  };
  const s = states[status] || states.disconnected;
  dot.className = `led-dot ${s.cls}`;
  text.className = `uppercase tracking-wider text-[10px] ${s.textCls}`;
  text.textContent = s.label;
}
```

- [ ] **Step 2: Add tab button styles to `frontend/src/style.css`**

Append to the end of `frontend/src/style.css`:

```css
/* Tab navigation */
.tab-btn {
  color: var(--text-dim);
  border-bottom: 2px solid transparent;
  border-radius: 0;
}
.tab-btn:hover { color: var(--text-primary); }
.tab-btn.active-tab {
  color: var(--accent);
  border-bottom: 2px solid var(--accent);
}
```

- [ ] **Step 3: Start the dev server and verify the tab bar renders**

```bash
cd frontend && npm run dev
```
Open `http://localhost:5173` — you should see the existing app unchanged (tab-bar isn't wired in yet, connection-bar still shows). Just confirm the JS file has no syntax errors by checking the browser console. Stop the server.

- [ ] **Step 4: Commit**

```bash
git add frontend/src/components/tab-bar.js frontend/src/style.css
git commit -m "feat: add tab-bar component with LED, tabs, and theme toggle"
```

---

## Task 5: Frontend settings panel

**Files:**
- Create: `frontend/src/components/settings-panel.js`

- [ ] **Step 1: Create `frontend/src/components/settings-panel.js`**

```javascript
const BAUDRATES = [9600, 19200, 38400, 57600, 115200, 230400, 460800, 921600];

export function createSettingsPanel() {
  const el = document.createElement('div');
  el.className = 'p-6 max-w-lg mx-auto';
  el.innerHTML = `
    <h2 class="text-accent font-mono text-sm uppercase tracking-widest mb-6">Connection Settings</h2>

    <div class="bg-card border border-base rounded p-4 mb-3 flex items-center justify-between">
      <div>
        <div class="text-primary text-xs font-mono uppercase tracking-wider">Simulation Mode</div>
        <div class="text-dim text-[10px] font-mono mt-0.5">Generate fake CAN data (no hardware needed)</div>
      </div>
      <label class="relative inline-flex items-center cursor-pointer ml-4">
        <input type="checkbox" id="sim-toggle" class="sr-only peer" />
        <div class="w-10 h-5 bg-raised rounded-full peer
          peer-checked:after:translate-x-5
          after:content-[''] after:absolute after:top-0.5 after:left-0.5
          after:bg-white after:rounded-full after:h-4 after:w-4
          after:transition-all peer-checked:bg-accent border border-base"></div>
      </label>
    </div>

    <div class="bg-card border border-base rounded p-4 mb-3" id="port-section">
      <div class="text-primary text-xs font-mono uppercase tracking-wider mb-3">Serial Port</div>
      <select id="port-select"
        class="w-full bg-raised border border-base rounded px-3 py-2 text-primary font-mono text-xs focus:outline-none focus:border-accent">
        <option value="">Loading...</option>
      </select>
      <button id="refresh-ports" class="mt-2 text-[10px] font-mono text-dim hover:text-accent transition-colors uppercase tracking-wider">
        Refresh port list
      </button>
    </div>

    <div class="bg-card border border-base rounded p-4 mb-6" id="baud-section">
      <div class="text-primary text-xs font-mono uppercase tracking-wider mb-3">Baud Rate</div>
      <select id="baud-select"
        class="w-full bg-raised border border-base rounded px-3 py-2 text-primary font-mono text-xs focus:outline-none focus:border-accent">
        ${BAUDRATES.map(b => `<option value="${b}"${b === 115200 ? ' selected' : ''}>${b.toLocaleString()}</option>`).join('')}
      </select>
    </div>

    <button id="apply-btn"
      class="w-full py-2.5 bg-raised border border-accent text-accent font-mono text-xs uppercase tracking-widest rounded hover:bg-[var(--accent-dim)] transition-colors">
      Apply
    </button>
    <div id="settings-status" class="mt-3 text-[10px] font-mono text-center h-4"></div>
  `;

  const simToggle = el.querySelector('#sim-toggle');
  const portSelect = el.querySelector('#port-select');
  const baudSelect = el.querySelector('#baud-select');
  const applyBtn = el.querySelector('#apply-btn');
  const statusEl = el.querySelector('#settings-status');
  const portSection = el.querySelector('#port-section');
  const baudSection = el.querySelector('#baud-section');
  const refreshBtn = el.querySelector('#refresh-ports');

  function setHardwareSectionEnabled(enabled) {
    portSelect.disabled = !enabled;
    baudSelect.disabled = !enabled;
    portSection.style.opacity = enabled ? '1' : '0.4';
    baudSection.style.opacity = enabled ? '1' : '0.4';
  }

  simToggle.addEventListener('change', () => {
    setHardwareSectionEnabled(!simToggle.checked);
  });

  async function loadPorts(selectedPort) {
    try {
      const res = await fetch('/api/ports');
      const ports = await res.json();
      portSelect.innerHTML = ports.length
        ? ports.map(p =>
            `<option value="${p.port}"${p.port === selectedPort ? ' selected' : ''}>${p.port} — ${p.description}</option>`
          ).join('')
        : '<option value="">No ports found — enable simulation</option>';
    } catch {
      portSelect.innerHTML = '<option value="">Could not load ports</option>';
    }
  }

  async function loadConfig() {
    try {
      const res = await fetch('/api/config');
      const cfg = await res.json();
      simToggle.checked = cfg.simulation;
      baudSelect.value = String(cfg.baudrate);
      await loadPorts(cfg.port);
      setHardwareSectionEnabled(!cfg.simulation);
      showStatus(cfg);
    } catch {
      showStatusText('Failed to load config', 'text-fault');
    }
  }

  refreshBtn.addEventListener('click', () => loadPorts(portSelect.value));

  applyBtn.addEventListener('click', async () => {
    applyBtn.disabled = true;
    applyBtn.textContent = 'Applying…';
    statusEl.textContent = '';
    try {
      const res = await fetch('/api/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          simulation: simToggle.checked,
          port: portSelect.value,
          baudrate: parseInt(baudSelect.value, 10),
        }),
      });
      const result = await res.json();
      showStatus(result);
    } catch {
      showStatusText('Request failed — is the server running?', 'text-fault');
    } finally {
      applyBtn.disabled = false;
      applyBtn.textContent = 'Apply';
    }
  });

  function showStatus(cfg) {
    if (cfg.status === 'error') {
      showStatusText(`Error: ${cfg.error}`, 'text-fault');
    } else if (cfg.status === 'simulation') {
      showStatusText('Simulation active', 'text-warn');
    } else if (cfg.status === 'ok') {
      showStatusText(`Connected to ${cfg.port}`, 'text-ok');
    }
  }

  function showStatusText(msg, cls) {
    statusEl.textContent = msg;
    statusEl.className = `mt-3 text-[10px] font-mono text-center h-4 ${cls}`;
  }

  loadConfig();

  return el;
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/components/settings-panel.js
git commit -m "feat: add settings panel with simulation toggle, port picker, baud rate"
```

---

## Task 6: Frontend debug panel

**Files:**
- Create: `frontend/src/components/debug-panel.js`

- [ ] **Step 1: Create `frontend/src/components/debug-panel.js`**

```javascript
const MAX_BUFFER = 500;
const MAX_ROWS = 200;

export function createDebugPanel() {
  const el = document.createElement('div');
  el.className = 'flex flex-col overflow-hidden';
  el.style.height = 'calc(100vh - 40px)';
  el.innerHTML = `
    <div class="flex items-center gap-3 px-4 py-2 bg-card border-b border-base shrink-0">
      <input id="debug-filter" type="text" placeholder="Filter ID (e.g. 0B6)"
        class="bg-raised border border-base rounded px-2 py-1 text-primary font-mono text-[10px] w-36
               focus:outline-none focus:border-accent uppercase tracking-wider" />
      <button id="debug-pause"
        class="px-3 py-1 text-[10px] font-mono uppercase tracking-wider bg-raised border border-base rounded text-primary hover:border-accent transition-colors">
        Pause
      </button>
      <button id="debug-clear"
        class="px-3 py-1 text-[10px] font-mono uppercase tracking-wider bg-raised border border-base rounded text-primary hover:border-accent transition-colors">
        Clear
      </button>
      <span id="debug-count" class="text-dim text-[10px] font-mono ml-auto">0 frames</span>
    </div>
    <div class="flex-1 overflow-auto">
      <table class="w-full border-collapse font-mono text-[10px]">
        <thead class="sticky top-0 bg-card border-b border-base z-10">
          <tr>
            <th class="text-left px-3 py-1.5 text-dim uppercase tracking-wider font-normal w-24">Time</th>
            <th class="text-left px-3 py-1.5 text-dim uppercase tracking-wider font-normal w-20">ID</th>
            <th class="text-left px-3 py-1.5 text-dim uppercase tracking-wider font-normal w-52">Raw (hex)</th>
            <th class="text-left px-3 py-1.5 text-dim uppercase tracking-wider font-normal">Signals</th>
          </tr>
        </thead>
        <tbody id="debug-tbody"></tbody>
      </table>
      <div id="debug-empty" class="text-dim text-center py-16 font-mono text-xs">
        Waiting for CAN frames…
      </div>
    </div>
  `;

  const filterInput = el.querySelector('#debug-filter');
  const pauseBtn = el.querySelector('#debug-pause');
  const clearBtn = el.querySelector('#debug-clear');
  const countEl = el.querySelector('#debug-count');
  const tbody = el.querySelector('#debug-tbody');
  const emptyEl = el.querySelector('#debug-empty');

  let buffer = [];
  let paused = false;
  let filterStr = '';
  let startTime = Date.now();
  let totalFrames = 0;

  filterInput.addEventListener('input', () => {
    filterStr = filterInput.value.trim().toUpperCase();
    render();
  });

  pauseBtn.addEventListener('click', () => {
    paused = !paused;
    pauseBtn.textContent = paused ? 'Resume' : 'Pause';
    pauseBtn.classList.toggle('text-warn', paused);
    if (!paused) render();
  });

  clearBtn.addEventListener('click', () => {
    buffer = [];
    totalFrames = 0;
    startTime = Date.now();
    countEl.textContent = '0 frames';
    render();
  });

  function onFrame(msg) {
    buffer.push(msg);
    totalFrames++;
    if (buffer.length > MAX_BUFFER) buffer.shift();
    countEl.textContent = `${totalFrames.toLocaleString()} frames`;
    if (!paused) render();
  }

  function render() {
    const filtered = filterStr
      ? buffer.filter(f => f.id.toUpperCase().replace('0X', '').includes(filterStr.replace('0X', '')))
      : buffer;

    emptyEl.style.display = filtered.length === 0 ? '' : 'none';

    const rows = filtered.slice(-MAX_ROWS).reverse();
    tbody.innerHTML = rows.map(f => {
      const relMs = Math.round(f.ts * 1000 - startTime);
      const signals = f.data
        ? Object.entries(f.data)
            .filter(([k]) => k !== '_unknown')
            .map(([k, v]) => `${k}=<span class="text-primary">${v}</span>`)
            .join(' <span class="text-dim">·</span> ')
        : '';
      return `<tr class="border-b border-base hover:bg-raised">
        <td class="px-3 py-1 text-dim tabular-nums">${relMs}ms</td>
        <td class="px-3 py-1 text-accent font-semibold">${f.id}</td>
        <td class="px-3 py-1 text-secondary tracking-wider">${f.raw || '—'}</td>
        <td class="px-3 py-1 text-secondary leading-relaxed">${signals}</td>
      </tr>`;
    }).join('');
  }

  return { element: el, onFrame };
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/components/debug-panel.js
git commit -m "feat: add debug panel with live frame table, filter, pause, and clear"
```

---

## Task 7: Wire main.js + cleanup

**Files:**
- Modify: `frontend/src/main.js`
- Delete: `frontend/src/components/connection-bar.js`

- [ ] **Step 1: Replace `frontend/src/main.js` with the new wired version**

```javascript
import './style.css';
import { initTheme, toggleTheme } from './theme.js';
import { createWsClient } from './ws-client.js';
import { updateSignal } from './state.js';
import { createTabBar, updateTabBarConnection } from './components/tab-bar.js';
import { createSearchBar } from './components/search-bar.js';
import { createSectionList } from './components/section-list.js';
import { createSettingsPanel } from './components/settings-panel.js';
import { createDebugPanel } from './components/debug-panel.js';

initTheme();

const app = document.getElementById('app');
app.innerHTML = '';
app.style.display = 'flex';
app.style.flexDirection = 'column';
app.style.height = '100vh';
app.style.overflow = 'hidden';

// Tab bar
const tabBar = createTabBar({ onTabChange: switchTab });
app.appendChild(tabBar);
document.getElementById('theme-toggle').addEventListener('click', toggleTheme);

// --- Dashboard panel ---
const dashboardPanel = document.createElement('div');
dashboardPanel.id = 'panel-dashboard';
dashboardPanel.className = 'flex-1 overflow-auto';

let currentSearch = '';
let currentCategory = null;

const searchBar = createSearchBar({
  onSearch: (query) => { currentSearch = query; applyFilters(); },
  onCategoryChange: (section) => { currentCategory = section; applyFilters(); },
});
dashboardPanel.appendChild(searchBar);

const { container: sectionList, sections } = createSectionList();
dashboardPanel.appendChild(sectionList);
app.appendChild(dashboardPanel);

// --- Debug panel ---
const { element: debugEl, onFrame } = createDebugPanel();
debugEl.id = 'panel-debug';
debugEl.style.display = 'none';
app.appendChild(debugEl);

// --- Settings panel ---
const settingsEl = createSettingsPanel();
settingsEl.id = 'panel-settings';
settingsEl.style.display = 'none';
settingsEl.style.flex = '1';
settingsEl.style.overflowY = 'auto';
app.appendChild(settingsEl);

// --- Tab switching ---
function switchTab(tab) {
  dashboardPanel.style.display = tab === 'dashboard' ? '' : 'none';
  debugEl.style.display = tab === 'debug' ? '' : 'none';
  settingsEl.style.display = tab === 'settings' ? '' : 'none';
}

// --- WebSocket ---
const wsClient = createWsClient({
  onStatusChange: (status) => updateTabBarConnection(status),
  onMessage: (msg) => {
    onFrame(msg);
    if (msg.data) {
      const { id: canId, ts, raw } = msg;
      for (const [name, value] of Object.entries(msg.data)) {
        updateSignal(canId, name, value, ts, raw);
      }
    }
  },
});

wsClient.connect();

// --- Filter logic ---
function applyFilters() {
  for (const { def, element } of sections) {
    const matchesCategory = !currentCategory || def.name === currentCategory.name;
    const hasSearchMatch = !currentSearch || sectionMatchesSearch(def, currentSearch);
    element.style.display = (matchesCategory && hasSearchMatch) ? '' : 'none';
  }
}

function sectionMatchesSearch(sectionDef, query) {
  if (sectionDef.name.toLowerCase().includes(query)) return true;
  for (const canId of sectionDef.canIds) {
    if (canId.toLowerCase().includes(query)) return true;
  }
  return false;
}
```

- [ ] **Step 2: Delete the retired connection-bar**

```bash
rm frontend/src/components/connection-bar.js
```

- [ ] **Step 3: Build the frontend and verify no errors**

```bash
cd frontend && npm run build
```
Expected: build succeeds with no errors. If there's an import error mentioning `connection-bar`, check that `main.js` no longer imports it.

- [ ] **Step 4: Start both backend and frontend dev server and do a full UI check**

Terminal 1 (backend):
```bash
cd can-bridge && python main.py
```

Terminal 2 (frontend):
```bash
cd frontend && npm run dev
```

Open `http://localhost:5173` and verify:
- [ ] Tab bar shows at top with LED dot + DASHBOARD / DEBUG / SETTINGS tabs
- [ ] Dashboard tab shows all signal sections (same as before)
- [ ] Debug tab shows frame table filling with rows; filter input works; Pause stops updates; Clear resets
- [ ] Settings tab shows simulation toggle (checked), greyed-out port/baud sections, and status "Simulation active"
- [ ] Clicking Apply on Settings with simulation=on keeps simulation running
- [ ] Theme toggle still works

- [ ] **Step 5: Commit**

```bash
git add frontend/src/main.js
git rm frontend/src/components/connection-bar.js
git commit -m "feat: wire tabs — dashboard, debug panel, settings panel"
```

---

## Task 8: Build final dist and end-to-end verification

- [ ] **Step 1: Build production frontend**

```bash
cd frontend && npm run build
```

- [ ] **Step 2: Start backend serving the built dist**

```bash
cd can-bridge && python main.py
```

Open `http://localhost:8765` — the full app should load from the built static files.

- [ ] **Step 3: Verify Settings → real port flow (if a serial adapter is available)**

Go to Settings tab → uncheck Simulation → pick your port → click Apply.  
Expected: status shows "Connected to /dev/ttyXXX" (or error if no device attached).  
If error: verify status shows "Error: [Port name]: No such file" and the UI stays usable.

- [ ] **Step 4: Verify Debug tab data quality**

Switch to Debug tab while in simulation.  
- Frame IDs like `0x0B6`, `0x0F6` appear in the ID column
- Raw hex bytes appear (e.g. `03 4A 00 3E 01 6E 44 80`)
- Signal column shows `rpm=842 · speed=6.2` style decoded data
- Filter by `0B6` shows only matching rows
- Pause stops new rows appearing; Resume catches up

- [ ] **Step 5: Run all backend tests one final time**

```bash
cd can-bridge && python -m pytest test_parser.py test_config.py -v
```
Expected: all pass

- [ ] **Step 6: Final commit**

```bash
git add frontend/dist
git commit -m "feat: settings and debug tabs — production build"
```
