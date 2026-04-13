# Universal Gripper Control (PyQt5)

Desktop application for controlling a Modbus-based electric gripper with a clean modular architecture.

## Project structure

```text
gripper_control/
├── core/
│   ├── controller.py
│   ├── gripper_base.py
│   └── models.py
├── drivers/
│   ├── dh_modbus.py
│   └── py_modbus_gripper.py
├── ui/
│   └── main_window.py
├── utils/
│   └── logger.py
└── main.py
```

## Install

```bash
python -m pip install -r requirements.txt
```

## Run

```bash
python -m gripper_control.main
```

## Implemented UI features

- COM port dropdown (`COM1` to `COM10`)
- Baudrate dropdown (`9600`, `19200`, `38400`, `57600`, `115200`)
- Slave ID (`1..247`)
- Position/Force/Speed sliders (`0..100%`)
- Connect / Initialize / Open / Close buttons
- Color status indicator (Green/Red/Gray)
- Read-only log panel

## Driver note

The Modbus client uses the current pymodbus import:

```python
from pymodbus.client import ModbusSerialClient
```

and initializes without the removed `method` parameter.
