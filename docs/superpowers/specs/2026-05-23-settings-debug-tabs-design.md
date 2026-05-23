# Settings & Debug Tabs — Design Spec
**Date:** 2026-05-23  
**Status:** Approved

## Goal

Add a Settings tab (disable simulation, pick serial port, baud rate) and a Debug tab (live raw CAN frame stream) to the web UI. Deployment target is Raspberry Pi serving a tablet browser. Must also work on macOS for local development.

---

## Architecture

### Backend — `can-bridge/`

**New file: `config.py`**  
Holds a mutable runtime config dataclass: `simulation: bool`, `port: str`, `baudrate: int`.  
Loads from `can-bridge/config.json` on startup; falls back to defaults (`simulation=True`, `port=""`, `baudrate=115200`).  
Exposes `get_config()` and `update_config()` functions used by `main.py`.  
Saves to `config.json` on every update.

**Modified: `serial_reader.py`**  
Remove hardcoded `/dev/ttyUSB0` and `115200` defaults from `__init__`. Accept `port` and `baudrate` as parameters every time `open()` is called so the reader can be restarted with new settings at runtime.

**Modified: `main.py`**  
- Remove `SIMULATION = not os.path.exists('/dev/ttyUSB0')` — replaced by config.
- Load config from `config.py` at startup.
- Hold the current CAN loop task in a module-level variable so it can be cancelled and restarted.
- Add three REST endpoints:
  - `GET /api/ports` — returns `[{port, description}]` using `serial.tools.list_ports.comports()`. Works on Pi (`/dev/ttyUSB*`, `/dev/ttyACM*`), macOS (`/dev/tty.usbserial-*`), and Windows (`COM*`).
  - `GET /api/config` — returns current config + connection status (`ok`, `error`, `simulation`).
  - `POST /api/config` — accepts `{simulation, port, baudrate}`, validates, saves, cancels current loop task, starts new one. Returns updated config + status.
- On serial open failure: set a module-level `connection_error` string; return it in `/api/config` status.
- Keep existing `sim_loop()` and `can_loop()` unchanged in logic; just restart them via task management.

### Frontend — `frontend/src/`

**New file: `components/tab-bar.js`**  
Renders the top bar containing:
- Left: connection LED + status text (moved from `connection-bar.js`)
- Center: tab buttons — DASHBOARD | DEBUG | SETTINGS
- Right: theme toggle (moved from `connection-bar.js`)

Exports `createTabBar(onTabChange)` and `updateTabBarConnection(status)`.  
`connection-bar.js` is retired (its responsibilities move here).

**New file: `components/settings-panel.js`**  
On mount, fetches `GET /api/config` and `GET /api/ports`.  
Renders:
- Simulation toggle (checkbox/switch) — when on, port selector is disabled
- Port dropdown — populated from `/api/ports`; shows port name + description
- Baud rate selector — options: 9600, 19200, 38400, 57600, 115200, 230400, 460800, 921600
- Apply button — `POST /api/config` with current form values
- Status line below Apply: shows "Connected", "Simulation active", or error message in red

**New file: `components/debug-panel.js`**  
Subscribes to WebSocket messages (receives them from `main.js` via a callback).  
Maintains an in-memory ring buffer of the last 500 frames.  
Renders:
- Filter input (by CAN ID, partial match, e.g. "0x0B6" or "B6")
- Pause / Resume button
- Clear button
- Frame counter (`1234 frames`)
- Scrolling table: **Timestamp** (relative ms or HH:MM:SS.mmm) | **ID** | **Raw bytes** | **Signals** (comma-separated parsed key=value)

When paused, buffering continues but the table DOM stops updating.  
Table shows newest frame at top. Max 200 rows rendered at once (virtual window).

**Modified: `main.js`**  
- Replace `createConnectionBar()` with `createTabBar()`.
- Create `settingsPanel` and `debugPanel` alongside `sectionList`.
- Show/hide panels on tab change; only the active panel is visible (`display: none` for inactive).
- Forward every WebSocket message to `debugPanel.onFrame(msg)` in addition to existing signal update logic.

---

## Data Flow

### Settings apply
```
User fills form → clicks Apply
→ POST /api/config {simulation, port, baudrate}
→ backend saves config.json, cancels current asyncio task
→ if simulation=true: starts sim_loop()
→ if simulation=false: opens serial port
  → success: starts can_loop()
  → failure: sets connection_error, returns {status: "error", error: "Cannot open COM3: ..."}
→ frontend shows status line result
```

### Debug tab frame flow
```
CAN frame arrives (real or sim)
→ broadcast() sends JSON over WebSocket to all clients
→ frontend ws-client.js calls onMessage(msg)
→ main.js forwards to debugPanel.onFrame(msg)
→ debug panel pushes to ring buffer
→ if not paused: re-renders table (newest 200 frames matching filter)
```

---

## Error Handling

| Scenario | Handling |
|---|---|
| Port not available | `/api/config` POST returns `{status: "error", error: "..."}`, shown in settings panel |
| Port disconnects mid-session | Existing serial exception handling in `can_loop()` propagates as WS disconnect |
| No ports listed | Dropdown shows "No ports found — enable simulation" |
| Config file missing/corrupt | Falls back to defaults silently |

---

## File Change Summary

| File | Change |
|---|---|
| `can-bridge/config.py` | **New** — runtime config dataclass + load/save |
| `can-bridge/main.py` | Modified — remove hardcoded sim detection, add 3 API endpoints, task restart logic |
| `can-bridge/serial_reader.py` | Modified — remove hardcoded defaults, accept port/baud at open() |
| `frontend/src/components/tab-bar.js` | **New** — top bar with LED, tabs, theme toggle |
| `frontend/src/components/settings-panel.js` | **New** — simulation toggle, port dropdown, baud rate, apply |
| `frontend/src/components/debug-panel.js` | **New** — raw frame table, filter, pause/resume |
| `frontend/src/components/connection-bar.js` | Retired (replaced by tab-bar) |
| `frontend/src/main.js` | Modified — tab switching, wire debug panel, use tab-bar |
