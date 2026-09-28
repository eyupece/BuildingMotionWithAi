"""DevFest event packs.

Each module adds one avatar style and one location theme. The backend accepts
every event's keys; the frontend decides which event's cards to show
(VITE_EVENT). To add a new DevFest, copy one module, register it below and
add its two preview images plus an entry in frontend/src/events.ts.
"""

from app.events import kastamonu, trabzon

EVENTS = {
    "kastamonu": kastamonu,
    "trabzon": trabzon,
}
