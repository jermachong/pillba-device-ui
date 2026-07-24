# Pillba — PyQt5 Conversion Brief

This document is a complete specification for converting the Pillba React prototype into a production PyQt5 application running on a Raspberry Pi with a 320×480 touchscreen. Read every section before writing any code.

---

## Project overview

**Pillba** is a touchscreen UI for an automated pill dispenser. It runs on a Raspberry Pi (any model with GPIO) connected to a 320×480 portrait LCD. A microcontroller (Arduino/STM32) drives the dispenser motors, load cell, lid sensors, and battery monitor. The Pi and MCU communicate over hardware UART at 115200 baud.

The app has **6 screens** navigated from a home hub. No persistent sidebar — sub-screens show a back button (top-left) that returns to Home (or the parent screen for Add Medication → Schedule).

---

## Tech stack

| Concern | Choice |
|---|---|
| GUI framework | PyQt5 |
| Charts | pyqtgraph (preferred) or matplotlib embedded in QWidget |
| Serial comms | pyserial — read in a QThread, emit signals to main thread |
| Camera (scan step) | OpenCV (`cv2`) captured into a QLabel via QTimer |
| Font | Nunito — bundle the TTF, load with `QFontDatabase.addApplicationFont` |
| Styling | Qt StyleSheets (QSS) — centralised in `styles.qss` |
| Data persistence | SQLite via Python `sqlite3` — medications, log entries, settings |

---

## Target environment

- **Resolution**: 320 × 480 px, portrait
- **Touch**: single-touch resistive or capacitive; no hover states needed
- **OS**: Raspberry Pi OS (Bookworm or Bullseye)
- **Python**: 3.10+
- **UART device**: `/dev/ttyAMA0` or `/dev/ttyUSB0` at 115200 8N1

---

## Color tokens

Map these throughout `styles.qss`. All values are hex.

| Token | Value | Usage |
|---|---|---|
| `background` | `#F8FAFC` | App/page background |
| `foreground` | `#0F172A` | Default text |
| `card` | `#FFFFFF` | Card/panel background |
| `card-border` | `rgba(15,23,42,0.10)` | Card border (use `#E2E8F0` in QSS) |
| `primary` | `#0D9488` | Teal — buttons, active states, progress bars |
| `primary-fg` | `#FFFFFF` | Text on primary |
| `accent` | `#14B8A6` | Bright teal — Online badge, highlights |
| `muted` | `#E2E8F0` | Subdued surfaces, disabled buttons |
| `muted-fg` | `#64748B` | Labels, captions, secondary text |
| `sidebar` | `#0F172A` | Top bar and Home header background |
| `sidebar-fg` | `#F8FAFC` | Text/icons on top bar |
| `sidebar-accent` | `#1E293B` | Top bar button hover |
| `amber` | `#F59E0B` | Warning colour |
| `amber-bg` | `#FFFBEB` | Warning banner background |
| `amber-border` | `#FDE68A` | Warning banner border |
| `destructive` | `#EF4444` | Red — errors, factory reset |
| `destructive-bg` | `#FEF2F2` | Red surface |
| `green` | `#22C55E` | Full/success state on fill bar |
| `chart-teal` | `#0D9488` | Taken bars/area |
| `chart-red` | `#EF4444` | Missed bars |
| `switch-off` | `#CBD5E1` | Toggle switch when inactive |

---

## Typography

Font: **Nunito** (bundle `Nunito-Regular.ttf`, `Nunito-SemiBold.ttf`, `Nunito-Bold.ttf`).  
Base font size: **14px** (matches the 320px-wide screen).

| Role | Size | Weight | QSS class |
|---|---|---|---|
| Clock display | 28px | Bold | `.clock` |
| Page title (top bar) | 14px | SemiBold | `.page-title` |
| Card title | 12px | Bold | `.card-title` |
| Body / label | 12px | Regular | `.body` |
| Caption / subtext | 11px | Regular | `.caption` |
| Micro label | 10px | Bold | `.micro-label` |

---

## App structure (recommended file layout)

```
pillba/
├── main.py                  # QApplication entry point, sets window 320×480
├── styles.qss               # All QSS styling
├── fonts/
│   └── Nunito-*.ttf
├── assets/
│   └── icons/               # SVG or PNG icons (see icon map below)
├── schema/
│   ├── uart_protocol.py     # UART frame encode/decode + message dataclasses
│   └── uart_protocol.h      # C header mirror for MCU firmware
├── serial_worker.py         # QThread that reads UART, emits Qt signals
├── db.py                    # SQLite helpers — medications, log, settings
├── pages/
│   ├── home.py              # HomeWidget
│   ├── schedule.py          # ScheduleWidget
│   ├── add_medication.py    # AddMedicationWidget (4-step wizard)
│   ├── dispense.py          # DispenseWidget
│   ├── log.py               # LogWidget
│   └── settings.py          # SettingsWidget
└── widgets/
    ├── top_bar.py           # Reusable TopBar widget
    ├── toggle_switch.py     # Animated QAbstractButton toggle switch
    ├── card.py              # Rounded card container QFrame
    └── chart_widgets.py     # Wrapped pyqtgraph charts
```

---

## Navigation model

Use a `QStackedWidget` as the root container inside a `QMainWindow` (fixed size 320×480, no window chrome on Pi — use `setWindowFlags(Qt.FramelessWindowHint)`).

```
QStackedWidget
├── index 0 — HomeWidget
├── index 1 — ScheduleWidget
├── index 2 — AddMedicationWidget
├── index 3 — DispenseWidget
├── index 4 — LogWidget
└── index 5 — SettingsWidget
```

Navigation:
- Home nav cards → `stack.setCurrentIndex(n)`
- All sub-page back buttons → `stack.setCurrentIndex(0)` except Add Medication → `stack.setCurrentIndex(1)`
- No animation required; instant switch is fine for a touchscreen

---

## Screen 1 — Home (`HomeWidget`)

### Layout (QVBoxLayout, no spacing)

**Header section** (fixed height 96px, `background: #0F172A`):
- Left column (QVBoxLayout):
  - "Pillba" label — 10px, Bold, `#F8FAFC` at 50% opacity, uppercase, letter-spacing 2px
  - Live clock label — 28px, Bold, `#FFFFFF` — update every second via `QTimer(interval=1000)`
  - Date label — 11px, `#F8FAFC` at 60% opacity — e.g. "Tue, Jul 22"
- Right column (QVBoxLayout, right-aligned):
  - Online badge pill — small rounded QLabel, teal dot + "Online" text, `background: rgba(13,148,136,0.2); color: #14B8A6; border-radius: 10px; padding: 2px 8px`
  - Next dose label — 11px, `#F8FAFC` at 50% opacity — e.g. "Next: 14:00"

**Navigation cards grid** (QGridLayout 2×2, margins 12px, spacing 10px):

Each card is a `QPushButton` subclass with `border-radius: 12px`, fixed height ~100px. Cards use these background colors:

| Card | Background | Icon |
|---|---|---|
| View Schedule | `#0D9488` | calendar-clock |
| Manual Dispense | `#F59E0B` | pill |
| View Log | `#3B82F6` | clipboard-list |
| Device Settings | `#475569` | settings |

Card internal layout (top→bottom):
1. Icon container: 36×36px, `border-radius: 8px; background: rgba(255,255,255,0.2)` — icon SVG 18×18px white
2. Title label: 12px Bold, white
3. Subtitle label: 11px, `rgba(255,255,255,0.7)`
4. Right-align chevron icon: 12px, `rgba(255,255,255,0.6)` — push to bottom-right with a spacer

**Footer** (fixed height 30px, border-top `#E2E8F0`):
- "Compartments: X/8 filled" label — 11px, `#64748B`
- Populate X from the last `DEVICE_STATUS` UART message (`compartments_filled` field)

---

## Screen 2 — Schedule (`ScheduleWidget`)

### Layout

**TopBar** (see Reusable Widgets) with title "Schedule", back → Home.

**Scrollable content** (`QScrollArea`, no scrollbar visible — `setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)`):

1. **Weekly adherence card** (white card, 12px radius):
   - "WEEKLY ADHERENCE" micro-label
   - `pyqtgraph.PlotWidget` (height 64px): area chart, 7 data points (Mon–Sun), teal fill with 30% alpha gradient, no axes, no grid
   - Data source: query SQLite `log` table for last 7 days, group by day, count taken/missed

2. **Medication rows** — for each medication in DB:
   - White card row (border-radius 12px, border `#E2E8F0`):
     - Left: 32×32px teal-tinted icon container + Pill icon
     - Center: name (12px Bold) + dose · time (11px muted)
     - Right: `ToggleSwitchWidget` (see Reusable Widgets)
   - Toggle state change → update `medications` table, send `SCHEDULE_SET` UART message

3. **"Add Medication" button** — full-width, `background: #0D9488`, white text, 12px radius, 40px height — navigates to AddMedication screen

---

## Screen 3 — Add Medication (`AddMedicationWidget`)

4-step wizard. Keep a `current_step: int` (0–3). Render a step indicator bar at top.

**Step indicator** (fixed height 40px, white bg, bottom border):
- 4 circles (20×20px, border-radius 10px) connected by 32px lines
- Active step: `background: #0D9488; color: white`
- Completed step: `background: rgba(13,148,136,0.2); color: #0D9488`; show "✓" instead of number
- Future step: `background: #E2E8F0; color: #64748B`

### Step 0 — Scan

- Instruction label: "Point camera at prescription bottle"
- **Camera viewport** (QLabel, 280×180px, `border-radius: 12px`, `background: #0F172A`):
  - Use OpenCV `cv2.VideoCapture(0)` in a `QThread`
  - Convert frame to `QImage` → `QPixmap` → set on QLabel via signal every ~100ms
  - Overlay corner bracket decorations using `QPainter` or overlay QLabels with teal borders
  - Animated scan line: a 1px-tall QFrame with `background: rgba(13,148,136,0.8)`, animated Y position via `QPropertyAnimation` bouncing between top and bottom of the viewport (duration 1500ms, loop forever, `QEasingCurve.Linear`)
  - Progress bar (bottom of viewport, height 4px): `QProgressBar` with teal fill, updates as scan progresses
  - On detection (mock after 3s, or real OCR result): stop scan line, show detection overlay (success icon + medication name)
- Detection card (hidden until scan completes): teal-tinted card showing identified med name, dose, assigned compartment
- "Continue" button: disabled (grey) until scan detected, then `background: #0D9488`

**OCR note**: For real use, capture frame → pass to `pytesseract` or a simple regex pattern matcher for "Rx" labels. For prototype, auto-detect after 3 seconds using a `QTimer.singleShot(3000, ...)`.

### Step 1 — Open Lid

- Instruction label: "Open the correct compartment lid"
- **Compartment diagram card**:
  - `QGridLayout` 4 columns × 2 rows — 8 compartment cells
  - Each cell: `QPushButton` or `QFrame`, 64×48px, border-radius 8px
  - Target compartment: `background: #0D9488; color: white; border: 2px solid #0D9488`
  - Other compartments: `background: #E2E8F0; color: #64748B; border: 2px solid #E2E8F0`
  - Below grid: instruction row "Lift open Compartment N" with open-box icon, teal tint background
- Warning banner (amber): "Only open Compartment N. Do not open other lids while the dispenser is active."
- "Lid is open — Start filling" button: advances to Step 2
  - In production: button becomes active only when `LID_STATUS` UART message received with `compartment=N, state=1`

### Step 2 — Filling

- Instruction: "Pour {name} pills into Compartment N"
- **Pill container graphic** (white card, centered):
  - Custom `QWidget` subclass — `paintEvent` draws a rounded-rect container, teal fill rising from bottom based on `fill_pct` (0–100)
  - Pill dots drawn with `QPainter.drawEllipse` — number of dots = `floor(fill_pct / 12)`, arranged in rows
  - Capacity % text centered in grey
  - Update `fill_pct` from `LOAD_SENSOR` UART messages: `fill_pct = (weight_g / 10.0) / 30.0 * 100`
- **Load sensor progress bar** (`QProgressBar`):
  - Label row: "LOAD SENSOR" micro-label + "Xg / 30g" value
  - Bar color changes via QSS: teal → amber (>80%) → green (100%)
  - Use `setStyleSheet` dynamically based on value
- Status message: "Keep pouring… sensor is reading" or success banner when full (weight ≥ 28g)
- "Close lid & Finish" button: disabled until `fill_pct >= 95`, then enabled

### Step 3 — Done

- Centered layout:
  - 64×64px teal circle with white checkmark icon
  - "Medication Added!" (16px Bold)
  - "{name} {dose}" subtitle (12px muted)
  - "Compartment N · ~X pills loaded" (11px muted)
- Summary card (white, border):
  - 4 rows: Medication / Compartment / Pills loaded / Status
  - Each row: label (11px muted) + value (11px Bold), space-between
- "Back to Schedule" primary button → write new medication to SQLite, navigate to Schedule

---

## Screen 4 — Manual Dispense (`DispenseWidget`)

**TopBar**: "Manual Dispense", back → Home.

**Form card** (white, border-radius 12px):

1. **Medication selector** — `QComboBox` styled to match: `background: #F1F5F9; border: 1px solid #E2E8F0; border-radius: 8px; padding: 6px 12px; font-size: 12px`
   - Populated from SQLite `medications` table

2. **Quantity stepper**:
   - Horizontal layout: `[−]` QPushButton · quantity QLabel (20px Bold, centered) · `[+]` QPushButton
   - Min 1, max 5
   - `[−]` and `[+]` buttons: 36×36px, `background: #E2E8F0; border-radius: 8px`

3. **Confirm override toggle** (bottom of card, top border separator):
   - Left: "Confirm override" (12px Bold) + "Required to enable dispense" (11px muted)
   - Right: `ToggleSwitchWidget`
   - Toggle must be ON to enable Dispense button

**Warning banner** (amber): "Manual dispense bypasses the automated schedule. Use only when necessary."

**"Dispense Now" button**: full-width, 48px height — disabled (grey) until toggle ON. On press → opens confirmation dialog.

**Confirmation dialog** (`QDialog`, 260px wide, border-radius 16px, `background: #FFFFFF`):
- Amber warning icon (40×40px circle)
- "Confirm Dispense" title (14px Bold)
- "Dispense Nx {medication} now?" body (11px muted)
- Two buttons: "Cancel" (secondary) + "Confirm" (primary teal)
- On Confirm: send `DISPENSE_CMD` UART message, show success banner for 3 seconds

**Success banner** (hidden by default): teal-tinted row with checkmark + "Dispensed successfully!" — hide after 3s via `QTimer.singleShot`.

---

## Screen 5 — Activity Log (`LogWidget`)

**TopBar**: "Activity Log", back → Home.

**Scrollable content**:

1. **Bar chart card** (white, border-radius 12px):
   - "LAST 7 DAYS" micro-label
   - `pyqtgraph.PlotWidget` (height 80px): grouped bar chart
     - Teal bars = taken count per day
     - Red bars = missed count per day
     - No axes labels on Y; day abbreviations on X
   - Legend row: teal square "Taken" · red square "Missed"
   - Data: query SQLite `log` table for last 7 days

2. **Log entries list** (read from SQLite `log` table, most recent first):
   - "TODAY" micro-label
   - Each row (white card, border-radius 12px):
     - Left icon (32×32px tinted circle): ✓ teal = taken, ✗ red = missed, wrench amber = manual
     - Center: medication name (12px Bold) + time (11px muted)
     - Right: status badge pill (10px Bold) matching icon color

   Status badge colors:
   - taken: `background: #F0FDFA; color: #0D9488`
   - missed: `background: #FEF2F2; color: #EF4444`
   - manual: `background: #FFFBEB; color: #F59E0B`

---

## Screen 6 — Settings (`SettingsWidget`)

**TopBar**: "Settings", back → Home.

**Scrollable content** — three grouped cards:

### Connectivity group
- **Wi-Fi row**: Wifi icon (teal) + "Wi-Fi" + network name (muted) + ToggleSwitch
  - Toggle → write to SQLite settings, send `SETTINGS_SET` UART message
- **Bluetooth row**: Bluetooth icon (blue `#3B82F6`) + "Bluetooth" + state text + ToggleSwitch

### Notifications group
- **Refill Alert row**: Bell icon (amber) + "Refill Alert" + ToggleSwitch
- **Volume row**:
  - Header: Volume icon (muted) + "Volume" label + "{N}%" value (teal, right-aligned)
  - `QSlider(Qt.Horizontal)`, range 0–100, styled teal
  - On value change → send `SETTINGS_SET` UART message

### System group
- **Timezone row**:
  - Clock icon + "Timezone" label
  - `QComboBox` with options: UTC-8, UTC-5, UTC+0, UTC+1, UTC+2, UTC+5:30, UTC+8
- **Info + reset row**:
  - "Firmware v2.4.1 · Serial #MD-00421" caption (11px muted)
  - "Factory Reset" button: `background: #FEF2F2; color: #EF4444; border: 1px solid rgba(239,68,68,0.2); border-radius: 8px`
  - Opens a `QDialog` (same pattern as Dispense confirmation but red):
    - "Factory Reset?" title
    - Warning body text
    - "Cancel" + "Reset" (red) buttons
    - On Reset: send `FACTORY_RESET` UART message (`confirm_token = 0xDEAD`)

---

## Reusable widgets

### `TopBar` (QWidget, fixed height 48px)

```python
class TopBar(QWidget):
    back_clicked = pyqtSignal()
    def __init__(self, title: str, parent=None): ...
```

- `background: #0F172A`
- Back button (36×36px, border-radius 8px): left arrow icon, white; hover → `background: #1E293B`
- Title QLabel: centered, 14px SemiBold, white

### `ToggleSwitchWidget` (QAbstractButton)

Animated custom toggle. Draw in `paintEvent`:
- Track: 40×20px rounded rect — off: `#CBD5E1`, on: `#0D9488`
- Thumb: 16×16px white circle, shadow
- Animate thumb X position with `QPropertyAnimation` on a custom `thumb_x` property, duration 150ms

### `CardWidget` (QFrame)

```python
# QSS equivalent:
# background: white; border: 1px solid #E2E8F0; border-radius: 12px;
```

### `StatusBadge` (QLabel)

Small pill label. Set text + call `set_status("taken"|"missed"|"manual")` to apply the right colors via `setStyleSheet`.

---

## UART serial worker

```python
# serial_worker.py
from PyQt5.QtCore import QThread, pyqtSignal
import serial
from schema.uart_protocol import decode_frame, MsgType, ...

class SerialWorker(QThread):
    heartbeat_received    = pyqtSignal(object)   # HeartbeatMsg dataclass
    device_status         = pyqtSignal(object)   # DeviceStatusMsg
    dose_event            = pyqtSignal(object)   # DoseEventMsg
    load_sensor_update    = pyqtSignal(object)   # LoadSensorMsg
    lid_status_update     = pyqtSignal(object)   # LidStatusMsg
    dispense_result       = pyqtSignal(object)   # DispenseResultMsg
    error_received        = pyqtSignal(object)   # ErrorMsg

    def __init__(self, port='/dev/ttyAMA0', baud=115200): ...

    def run(self):
        # Read bytes, accumulate until sync bytes found, parse full frame,
        # decode, emit the appropriate signal.
        ...

    def send(self, msg_type: int, payload: bytes):
        # encode_frame + ser.write — call from main thread via QMetaObject.invokeMethod
        # or push to a thread-safe queue
        ...
```

Connect worker signals to page slots in `main.py`:

```python
worker.load_sensor_update.connect(add_med_page.on_load_sensor)
worker.lid_status_update.connect(add_med_page.on_lid_status)
worker.dose_event.connect(log_page.on_dose_event)
worker.device_status.connect(home_page.on_device_status)
worker.dispense_result.connect(dispense_page.on_dispense_result)
```

---

## UART protocol schema

Full binary framing protocol between Pi and MCU. Implemented in `schema/uart_protocol.py` (Pi) and `schema/uart_protocol.h` (MCU).

### Frame format (binary, little-endian)

```
[0xAA][0x55][MSG_TYPE 1B][LENGTH 1B][PAYLOAD 0-251B][CRC8 1B]
```

CRC-8/MAXIM over: `[MSG_TYPE, LENGTH] + PAYLOAD`  
UART: 115200 baud, 8N1

### Message types

| ID | Name | Direction | Payload bytes |
|---|---|---|---|
| 0x01 | HEARTBEAT | MCU→Pi | 4 |
| 0x02 | HEARTBEAT_ACK | Pi→MCU | 4 |
| 0x10 | DISPENSE_CMD | Pi→MCU | 2 |
| 0x11 | DISPENSE_RESULT | MCU→Pi | 3 |
| 0x20 | SCHEDULE_SET | Pi→MCU | 5 |
| 0x21 | SCHEDULE_ACK | MCU→Pi | 2 |
| 0x30 | DOSE_EVENT | MCU→Pi | 6 |
| 0x40 | LOAD_SENSOR | MCU→Pi | 3 |
| 0x41 | LID_STATUS | MCU→Pi | 2 |
| 0x50 | SETTINGS_SET | Pi→MCU | 4 |
| 0x51 | SETTINGS_ACK | MCU→Pi | 1 |
| 0x60 | DEVICE_STATUS | MCU→Pi | 4 |
| 0xF0 | FACTORY_RESET | Pi→MCU | 2 |
| 0xFF | ERROR | Both | 2 |

### Payload struct formats (Python `struct` notation, little-endian `<`)

```
HEARTBEAT       <HBB    battery_mv(u16), status_flags(u8), compartments(u8)
HEARTBEAT_ACK   <I      unix_time(u32)
DISPENSE_CMD    <BB     slot(u8), quantity(u8)
DISPENSE_RESULT <BBB    slot(u8), qty_dispensed(u8), result(u8)
SCHEDULE_SET    <BBBBB  slot(u8), hour(u8), minute(u8), days_mask(u8), active(u8)
SCHEDULE_ACK    <BB     slot(u8), result(u8)
DOSE_EVENT      <BIB    slot(u8), unix_time(u32), status(u8)   [note: 6 bytes]
LOAD_SENSOR     <BH     compartment(u8), weight_g_x10(u16)
LID_STATUS      <BB     compartment(u8), state(u8)
SETTINGS_SET    <BBh    volume(u8), refill_alert(u8), tz_offset_min(i16)
SETTINGS_ACK    <B      result(u8)
DEVICE_STATUS   <BBbB   battery_pct(u8), wifi_rssi(i8), compartments_filled(u8), error_flags(u8)
FACTORY_RESET   <H      confirm_token(u16)  [must be 0xDEAD]
ERROR           <BB     error_code(u8), context_byte(u8)
```

### Status/result enums

```python
# DISPENSE_RESULT.result
DISPENSE_OK       = 0x00
DISPENSE_JAM      = 0x01
DISPENSE_EMPTY    = 0x02
DISPENSE_TIMEOUT  = 0x03

# DOSE_EVENT.status
DOSE_TAKEN  = 0
DOSE_MISSED = 1
DOSE_MANUAL = 2

# LID_STATUS.state
LID_CLOSED = 0
LID_OPEN   = 1

# Error codes (ERROR.error_code)
ERR_UNKNOWN    = 0x00
ERR_BAD_CRC    = 0x01
ERR_BAD_LENGTH = 0x02
ERR_UNKNOWN_MSG= 0x03
ERR_SLOT_BAD   = 0x10
ERR_MOTOR_JAM  = 0x11
ERR_EMPTY      = 0x12
ERR_FLASH      = 0x20
ERR_RTC        = 0x21
```

---

## SQLite schema

```sql
CREATE TABLE medications (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL,
    dose        TEXT NOT NULL,          -- e.g. "500mg"
    slot        INTEGER NOT NULL,       -- compartment 1–8
    hour        INTEGER NOT NULL,       -- 0–23
    minute      INTEGER NOT NULL,       -- 0–59
    days_mask   INTEGER NOT NULL DEFAULT 127,  -- all days
    active      INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE log (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    slot        INTEGER NOT NULL,
    medication  TEXT NOT NULL,          -- denormalized for display
    event_time  INTEGER NOT NULL,       -- unix timestamp
    status      INTEGER NOT NULL        -- 0=taken, 1=missed, 2=manual
);

CREATE TABLE settings (
    key         TEXT PRIMARY KEY,
    value       TEXT NOT NULL
);
-- Seed:
-- INSERT INTO settings VALUES ('volume', '70');
-- INSERT INTO settings VALUES ('refill_alert', '1');
-- INSERT INTO settings VALUES ('wifi', '1');
-- INSERT INTO settings VALUES ('bluetooth', '0');
-- INSERT INTO settings VALUES ('timezone', 'UTC+0');
```

---

## `main.py` entry point

```python
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFontDatabase

from pages.home import HomeWidget
from pages.schedule import ScheduleWidget
from pages.add_medication import AddMedicationWidget
from pages.dispense import DispenseWidget
from pages.log import LogWidget
from pages.settings import SettingsWidget
from serial_worker import SerialWorker

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setFixedSize(320, 480)
        self.setWindowFlags(Qt.FramelessWindowHint)  # fullscreen on Pi

        # Load fonts
        QFontDatabase.addApplicationFont("fonts/Nunito-Regular.ttf")
        QFontDatabase.addApplicationFont("fonts/Nunito-SemiBold.ttf")
        QFontDatabase.addApplicationFont("fonts/Nunito-Bold.ttf")

        # Load stylesheet
        with open("styles.qss") as f:
            self.setStyleSheet(f.read())

        # Pages
        self.stack = QStackedWidget()
        self.home = HomeWidget()
        self.schedule = ScheduleWidget()
        self.add_med = AddMedicationWidget()
        self.dispense = DispenseWidget()
        self.log = LogWidget()
        self.settings_page = SettingsWidget()

        for w in [self.home, self.schedule, self.add_med,
                  self.dispense, self.log, self.settings_page]:
            self.stack.addWidget(w)
        self.setCentralWidget(self.stack)

        # Navigation wiring
        self.home.navigate.connect(self.go_to)
        self.schedule.go_back.connect(lambda: self.go_to(0))
        self.schedule.go_add.connect(lambda: self.go_to(2))
        self.add_med.go_back.connect(lambda: self.go_to(1))
        self.dispense.go_back.connect(lambda: self.go_to(0))
        self.log.go_back.connect(lambda: self.go_to(0))
        self.settings_page.go_back.connect(lambda: self.go_to(0))

        # UART worker
        self.worker = SerialWorker('/dev/ttyAMA0')
        self.worker.load_sensor_update.connect(self.add_med.on_load_sensor)
        self.worker.lid_status_update.connect(self.add_med.on_lid_status)
        self.worker.dose_event.connect(self.log.on_dose_event)
        self.worker.device_status.connect(self.home.on_device_status)
        self.worker.dispense_result.connect(self.dispense.on_dispense_result)
        self.worker.start()

    def go_to(self, index: int):
        self.stack.setCurrentIndex(index)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
```

---

## QSS stylesheet skeleton (`styles.qss`)

```css
/* === Global === */
* { font-family: "Nunito"; font-size: 12px; color: #0F172A; }
QMainWindow, QWidget#root { background: #F8FAFC; }

/* === Cards === */
QFrame.card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
}

/* === TopBar === */
QWidget#topbar { background: #0F172A; }
QLabel#topbar-title { color: #F8FAFC; font-size: 14px; font-weight: 600; }
QPushButton#back-btn {
    background: transparent; border: none; border-radius: 8px;
    color: #F8FAFC;
}
QPushButton#back-btn:pressed { background: #1E293B; }

/* === Home nav cards === */
QPushButton.nav-card { border: none; border-radius: 12px; text-align: left; }
QPushButton.nav-card:pressed { opacity: 0.85; }

/* === Primary button === */
QPushButton.primary {
    background: #0D9488; color: #FFFFFF;
    border: none; border-radius: 12px;
    font-size: 12px; font-weight: 700;
    min-height: 40px;
}
QPushButton.primary:disabled { background: #E2E8F0; color: #64748B; }
QPushButton.primary:pressed { background: #0F766E; }

/* === Secondary button === */
QPushButton.secondary {
    background: #E2E8F0; color: #0F172A;
    border: none; border-radius: 8px;
    font-size: 12px; font-weight: 700;
}

/* === Destructive button === */
QPushButton.destructive {
    background: #FEF2F2; color: #EF4444;
    border: 1px solid rgba(239,68,68,0.2);
    border-radius: 8px; font-weight: 700;
}

/* === Stepper buttons === */
QPushButton.stepper {
    background: #E2E8F0; border: none; border-radius: 8px;
    min-width: 36px; min-height: 36px;
}

/* === QComboBox === */
QComboBox {
    background: #F1F5F9; border: 1px solid #E2E8F0;
    border-radius: 8px; padding: 6px 12px;
}

/* === QSlider (volume) === */
QSlider::groove:horizontal {
    height: 6px; background: #E2E8F0; border-radius: 3px;
}
QSlider::sub-page:horizontal {
    background: #0D9488; border-radius: 3px;
}
QSlider::handle:horizontal {
    background: #0D9488; width: 16px; height: 16px;
    border-radius: 8px; margin: -5px 0;
}

/* === QScrollArea === */
QScrollArea { border: none; background: transparent; }
QScrollBar:vertical { width: 0px; }

/* === Warning banner === */
QFrame.warning {
    background: #FFFBEB; border: 1px solid #FDE68A; border-radius: 12px;
}

/* === Success banner === */
QFrame.success {
    background: #F0FDFA; border: 1px solid rgba(13,148,136,0.3); border-radius: 12px;
}
```

---

## Add Medication — camera integration detail

```python
# In AddMedicationWidget, Step 0
import cv2
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage, QPixmap

class CameraThread(QThread):
    frame_ready = pyqtSignal(QImage)

    def run(self):
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 180)
        while self._running:
            ret, frame = cap.read()
            if ret:
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb.shape
                img = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
                self.frame_ready.emit(img)
        cap.release()

# Connect: cam_thread.frame_ready.connect(lambda img: self.cam_label.setPixmap(QPixmap.fromImage(img)))
# Scan detection (mock): QTimer.singleShot(3000, self.on_scan_detected)
```

---

## Dependencies (`requirements.txt`)

```
PyQt5>=5.15
pyserial>=3.5
pyqtgraph>=0.13
opencv-python>=4.8
pytesseract>=0.3     # optional — real OCR
```

Install on Pi:
```bash
pip install -r requirements.txt
sudo apt install tesseract-ocr   # if using pytesseract
```

---

## Checklist for Claude

When implementing this project, work in this order:

1. `main.py` — QApplication, QMainWindow 320×480 frameless, QStackedWidget, font loading
2. `styles.qss` — full stylesheet from the skeleton above, refine as you go
3. `schema/uart_protocol.py` — frame encode/decode, MsgType enum, all payload dataclasses
4. `db.py` — SQLite open/create, all three tables, CRUD helpers
5. `widgets/toggle_switch.py` — animated ToggleSwitchWidget
6. `widgets/top_bar.py` — TopBar reusable widget
7. `pages/home.py` — HomeWidget with live clock and 4 nav cards
8. `pages/schedule.py` — list from DB, area chart, toggles, Add button
9. `pages/add_medication.py` — 4-step wizard, camera thread, load sensor slots
10. `pages/dispense.py` — form, stepper, modal dialog, UART send
11. `pages/log.py` — bar chart, log list from DB
12. `pages/settings.py` — grouped settings, sliders, factory reset dialog
13. `serial_worker.py` — QThread UART reader, all signals
14. Wire all navigation signals in `main.py`
15. Test without hardware: stub `SerialWorker.run()` to emit mock messages on a timer
