# gripper-universal-control

Universal, modular Python platform for controlling industrial electric grippers.

## Features

- Abstract gripper interface for easy multi-brand expansion.
- Initial DH Robotics Modbus RTU driver implementation.
- RS485 communication helper with reconnect support.
- PyQt5 GUI with command controls and status indicator.
- Extensible architecture for adding SMC / Robotiq / OnRobot drivers.

## Project Structure

```text
gripper_control/
├── main.py
├── core/
│   ├── gripper_base.py
│   └── models.py
├── drivers/
│   └── dh_modbus.py
├── communication/
│   └── serial_rs485.py
├── ui/
│   └── main_window.py
└── utils/
    └── logger.py
```

## Requirements

- Python 3.10+
- Serial/USB RS485 adapter
- DH Robotics gripper configured for Modbus RTU

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

## Run the application

Windows (default COM3):

```bash
python -m gripper_control.main --port COM3 --baudrate 115200 --slave-id 1
```

Linux example:

```bash
python -m gripper_control.main --port /dev/ttyUSB0 --baudrate 115200 --slave-id 1
```

## How to connect to a COM port

1. Plug in the RS485 adapter.
2. Open **Device Manager** in Windows.
3. Expand **Ports (COM & LPT)**.
4. Read the assigned COM port (e.g., `COM5`).
5. Launch the app with the same port:

```bash
python -m gripper_control.main --port COM5
```

## GUI Controls

- **Connect**: Opens Modbus connection to gripper.
- **Initialize**: Sends init command (`0x0100 = 1`).
- **Open**: Sets position to open (`0x0103 = 0`).
- **Close**: Sets position to close (`0x0103 = 1000`).
- **Position slider**: 0–100% (mapped to 0–1000 register).
- **Force slider**: 20–100%.
- **Speed slider**: 0–100% (internally clamped to 1–100 for DH register).

Status indicator colors:
- **Green**: Object detected
- **Blue**: Ready / command successful
- **Red**: Error or command failure

## DH Robotics register map used

- `0x0100`: Initialize
- `0x0101`: Force (20–100)
- `0x0103`: Position (0–1000)
- `0x0104`: Speed (1–100)
- `0x0201`: Status

## Extending with new brands

Create a new driver class implementing `GripperBase` and wire it in `main.py`. No UI redesign is required if the new driver follows the same abstraction API.
