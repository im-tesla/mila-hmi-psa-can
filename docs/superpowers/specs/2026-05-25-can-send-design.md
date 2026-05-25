# CAN Data Sending & Signal Card Interactions

**Date:** 2026-05-25  
**Status:** Approved

---

## Goal

Enable the HMI to write CAN signals back to the bus (or inject into simulation), triggered by tapping a signal card. Fix the broken long-press raw popover.

---

## Signal Card Interactions

### Single click
- Signals with an `enum_map` → open the edit modal
- Numeric-only signals → open the read-only raw info popover (same content as long-press)

### Long press (500 ms hold)
- Always opens the read-only raw info popover (CAN ID, raw bytes, timestamp)
- **Bug fix:** remove `pointerleave` from the cancel listeners in `signal-card.js`. It fires when the pointer drifts slightly on desktop/touch and kills the timer before 500 ms. `pointerup` and `pointercancel` are sufficient.

---

## Edit Modal

File: `frontend/src/components/signal-edit-modal.js` (new)

### Contents
- **Header:** signal name + CAN ID badge
- **Current value:** displayed with existing color coding (`text-ok`, `text-fault`, `text-warn`, `text-primary`)
- **Choice buttons:** one per enum option; active value highlighted; clicking a non-active option sends the change and closes the modal
- **Dismiss:** click backdrop or X button to close without sending

### Data source
Enum options come from `CAN_SIGNALS` in `can-signal-list.js` — already on the frontend, no extra fetch needed.

### Trigger
`signal-card.js` gains a click handler (separate from the long-press timer). If the signal has an enum map, it calls `showSignalEditModal(canId, signalName)`. Otherwise it calls `showRawPopover`.

---

## Backend — WebSocket Write Path

### Message format (frontend → backend)
```json
{ "type": "write", "canId": "0x0F6", "signal": "left_turn", "rawValue": 1 }
```

`rawValue` is the integer raw CAN value (the key in the enum_map), not the display string.

### `_last_frames` dict
A `dict[int, bytearray]` in `main.py` (keyed by integer CAN ID) that stores the most recently seen or sent 8-byte frame for each ID. Updated on every broadcast (both sim and real). Gives the write path full frame context so modifying one signal doesn't zero adjacent signals.

### `encode_signal` helper
New function in `can_parser.py`:

```python
def encode_signal(data: bytearray, byte_off: int, bit_off: int, bit_len: int, raw_value: int) -> None:
```

Mirrors `extract_bits` but writes bits. Modifies `data` in place.

### WebSocket receive loop (updated `main.py`)
`ws.receive_text()` currently discards all incoming data. Change to:
1. Parse JSON; ignore non-`write` messages
2. Resolve signal definition from `CAN_DEFINITIONS`
3. Copy `_last_frames[can_id]` (or zero-padded 8 bytes if not yet seen)
4. Call `encode_signal` to set the bits
5. Update `_last_frames[can_id]`
6. If real serial connected → write frame: `0xAA | id_hi | id_lo | 0x08 | data[0..7]`
7. Parse result with `parse_frame` and broadcast as a normal frame message

### Serial write format
```
0xAA  id_hi  id_lo  0x08  data[0]..data[7]
```
Always sends 8 data bytes (matching the read side's padded frame).

---

## Files Changed

| File | Change |
|------|--------|
| `frontend/src/components/signal-card.js` | Add click handler; fix long-press cancel bug |
| `frontend/src/components/signal-edit-modal.js` | New — edit modal component |
| `can-bridge/can_parser.py` | Add `encode_signal` function |
| `can-bridge/main.py` | Add `_last_frames` dict; update WS receive loop; add serial write |

---

## Out of Scope

- Numeric signal editing (only enum signals are writable)
- Authentication / write protection
- Undo / confirmation step (clicking a choice sends immediately)
