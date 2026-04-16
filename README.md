# Rideau Canal Sensor Simulation

## Overview
This repository contains the Python sensor simulator for the Rideau Canal Skateway Monitoring System. It simulates telemetry data from three locations:
- Dow’s Lake
- Fifth Avenue
- NAC

The simulator sends sensor readings to Azure IoT Hub every 10 seconds.

## Features
- simulates 3 devices
- sends JSON telemetry to Azure IoT Hub
- generates realistic changing values

## Telemetry Fields
Each message contains:
- deviceId
- location
- timestamp
- iceThicknessCm
- surfaceTempC
- snowAccumulationCm
- externalTempC

## Files
- `sensor_simulator.py`
- `requirements.txt`
- `.env`

## Requirements
- Python 3.x
- Azure IoT Hub device connection strings
- Required Python packages from `requirements.txt`

## Installation

```bash
pip install -r requirements.txt
```
## Run
```bash
python sensor_simulator.py
```

## AI Usage Disclosure
AI tools were used for assistance with debugging, code structure, and documentation.
