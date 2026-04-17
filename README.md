# Rideau Canal Sensor Simulation

## Overview

This repository contains the Python-based sensor simulator for the Rideau Canal Skateway Monitoring System.

The simulator creates three virtual sensors for:
- **Dow's Lake**
- **Fifth Avenue**
- **NAC**

It generates environmental telemetry data every 10 seconds and sends the messages to **Azure IoT Hub** using the **Azure IoT Device SDK for Python**.

The simulator is used to test the real-time data pipeline for ingestion, processing, storage, and dashboard visualization.

### Technologies Used
- Python 3
- Azure IoT Device SDK for Python
- python-dotenv

---

## Prerequisites

Before running the simulator, make sure you have:

- Python 3 installed
- `pip` installed
- An Azure subscription
- An Azure IoT Hub already created
- Three registered IoT Hub devices:
  - `dows-lake`
  - `fifth-avenue`
  - `nac`
- Valid device connection strings for the three devices

---

## Installation

Clone the repository and install the required packages:

```bash
pip install -r requirements.txt
```

The required dependencies are listed in `requirements.txt`.

---

## Configuration

Create a `.env` file in the project root.

Add the device connection strings for the three virtual sensors:

```env
IOTHUB_DEVICE_CONNECTION_STRING_DOWS_LAKE
IOTHUB_DEVICE_CONNECTION_STRING_FIFTH_AVE
IOTHUB_DEVICE_CONNECTION_STRING_NAC
```
---

## Usage

Run the simulator with:

```bash
python sensor_simulator.py
```

When it starts successfully, it will:
1. connect the three virtual sensors to Azure IoT Hub
2. generate simulated readings every 10 seconds
3. send telemetry messages in JSON format
4. print the outgoing messages in the terminal

To stop the simulator, press:

```text
Ctrl + C
```
---

## Code Structure

### Main Files
- `sensor_simulator.py` - main simulator logic
- `requirements.txt` - Python dependencies
- `.env` - sample environment variables

### Main Components

#### `VirtualSensor` class
This class represents one simulated sensor device.

It is responsible for:
- storing the sensor state
- connecting to Azure IoT Hub
- generating readings
- sending telemetry messages

Each location is represented by one `VirtualSensor` object.

#### `build_sensors()`
This function creates the three virtual sensors:
- Dow's Lake
- Fifth Avenue
- NAC

It also assigns each sensor its device ID, location name, connection string, and starting values.

#### `generate_reading()`
This function generates one telemetry reading.

It updates the values for:
- ice thickness
- surface temperature
- snow accumulation
- external temperature

Then it returns a Python dictionary that is later converted to JSON.

#### `send_reading()`
This function:
- calls `generate_reading()`
- converts the reading to JSON
- creates an Azure IoT message
- sends the message to IoT Hub

#### `main()`
This is the main program entry point.

It:
- builds the virtual sensors
- connects them to IoT Hub
- sends messages every 10 seconds
- handles graceful shutdown when the user stops the program

---

## Key Functions

### `utc_now_iso()`
Returns the current UTC timestamp in ISO 8601 format.

### `clamp(value, minimum, maximum)`
Keeps a generated value inside a defined range.

### `jitter(value, min_delta, max_delta)`
Adds a small random variation to a value to simulate sensor changes.

### `generate_reading()`
Creates the telemetry data for one sensor reading.

### `send_reading()`
Sends the generated telemetry to Azure IoT Hub.

---

## Sensor Data Format

Each telemetry message is sent in JSON format.

### JSON Schema
```json
{
  "deviceId": "string",
  "location": "string",
  "timestamp": "string",
  "iceThicknessCm": "number",
  "surfaceTempC": "number",
  "snowAccumulationCm": "number",
  "externalTempC": "number"
}
```

### Example Output
```json
{
  "deviceId": "dows-lake",
  "location": "Dow's Lake",
  "timestamp": "2026-04-16T02:40:00.000000+00:00",
  "iceThicknessCm": 31.84,
  "surfaceTempC": -3.62,
  "snowAccumulationCm": 1.43,
  "externalTempC": -5.27
}
```

---

## Troubleshooting

### 1. Connection string error
**Problem:** The simulator fails to connect to IoT Hub.

**Possible cause:** One or more device connection strings are missing or incorrect.

**Fix:**  
Check the `.env` file and verify that the three environment variables are present and correct.

---

### 2. IoT Hub not receiving messages
**Problem:** The simulator appears to run, but Azure IoT Hub does not show incoming telemetry.

**Possible cause:** Wrong connection strings, wrong device IDs, or simulator not sending successfully.

**Fix:**  
- verify the device IDs in IoT Hub
- verify the connection strings
- check the terminal output for sent messages
- check the **Telemetry messages sent** metric in Azure IoT Hub
