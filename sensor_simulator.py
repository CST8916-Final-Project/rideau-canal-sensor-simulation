import json
import os
import random
import signal
import sys
import time
from datetime import datetime, timezone
from typing import Dict, List

from azure.iot.device import IoTHubDeviceClient, Message
from dotenv import load_dotenv


load_dotenv()

SEND_INTERVAL_SECONDS = 10


def utc_now_iso() -> str:
    """Return current UTC time in ISO 8601 format."""
    return datetime.now(timezone.utc).isoformat()


def clamp(value: float, minimum: float, maximum: float) -> float:
    """Keep a float value inside a min/max range."""
    return max(minimum, min(value, maximum))


def jitter(value: float, min_delta: float, max_delta: float) -> float:
    """Add a small random change to a value."""
    return value + random.uniform(min_delta, max_delta)


class VirtualSensor:
    def __init__(
        self,
        device_id: str,
        location: str,
        connection_string: str,
        ice_thickness_cm: float,
        surface_temp_c: float,
        snow_accumulation_cm: float,
        external_temp_c: float,
    ) -> None:
        self.device_id = device_id
        self.location = location
        self.connection_string = connection_string
        self.client = IoTHubDeviceClient.create_from_connection_string(connection_string)

        # Starting values
        self.ice_thickness_cm = ice_thickness_cm
        self.surface_temp_c = surface_temp_c
        self.snow_accumulation_cm = snow_accumulation_cm
        self.external_temp_c = external_temp_c

    def connect(self) -> None:
        self.client.connect()
        print(f"[CONNECTED] {self.device_id} ({self.location})")

    def disconnect(self) -> None:
        try:
            self.client.disconnect()
            print(f"[DISCONNECTED] {self.device_id}")
        except Exception as exc:
            print(f"[WARN] Could not disconnect {self.device_id}: {exc}")

    def generate_reading(self) -> Dict:
        """
        Generate one telemetry reading with slow realistic drift.
        This keeps values changing gradually instead of jumping too much.
        """
        self.external_temp_c = clamp(jitter(self.external_temp_c, -0.6, 0.6), -20.0, 5.0)
        self.surface_temp_c = clamp(
            jitter(self.surface_temp_c, -0.5, 0.5) + (self.external_temp_c - self.surface_temp_c) * 0.08,
            -15.0,
            3.0,
        )
        self.ice_thickness_cm = clamp(
            jitter(self.ice_thickness_cm, -0.3, 0.2),
            20.0,
            40.0,
        )
        self.snow_accumulation_cm = clamp(
            jitter(self.snow_accumulation_cm, -0.2, 0.4),
            0.0,
            12.0,
        )

        reading = {
            "deviceId": self.device_id,
            "location": self.location,
            "timestamp": utc_now_iso(),
            "iceThicknessCm": round(self.ice_thickness_cm, 2),
            "surfaceTempC": round(self.surface_temp_c, 2),
            "snowAccumulationCm": round(self.snow_accumulation_cm, 2),
            "externalTempC": round(self.external_temp_c, 2),
        }
        return reading

    def send_reading(self) -> None:
        reading = self.generate_reading()
        payload = json.dumps(reading)

        message = Message(payload)
        message.content_encoding = "utf-8"
        message.content_type = "application/json"

        # Optional application properties for easier debugging/routing
        message.custom_properties["deviceId"] = self.device_id
        message.custom_properties["location"] = self.location

        self.client.send_message(message)
        print(f"[SENT] {self.device_id}: {payload}")


def get_required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ValueError(f"Missing required environment variable: {name}")
    return value


def build_sensors() -> List[VirtualSensor]:
    """
    Build the 3 required location sensors:
    Dow's Lake, Fifth Avenue, and NAC.
    """
    dows_lake = VirtualSensor(
        device_id="dows-lake",
        location="Dow's Lake",
        connection_string=get_required_env("IOTHUB_DEVICE_CONNECTION_STRING_DOWS_LAKE"),
        ice_thickness_cm=31.5,
        surface_temp_c=-3.5,
        snow_accumulation_cm=1.2,
        external_temp_c=-6.0,
    )

    fifth_avenue = VirtualSensor(
        device_id="fifth-avenue",
        location="Fifth Avenue",
        connection_string=get_required_env("IOTHUB_DEVICE_CONNECTION_STRING_FIFTH_AVE"),
        ice_thickness_cm=28.0,
        surface_temp_c=-1.2,
        snow_accumulation_cm=2.4,
        external_temp_c=-4.8,
    )

    nac = VirtualSensor(
        device_id="nac",
        location="NAC",
        connection_string=get_required_env("IOTHUB_DEVICE_CONNECTION_STRING_NAC"),
        ice_thickness_cm=24.5,
        surface_temp_c=0.2,
        snow_accumulation_cm=3.0,
        external_temp_c=-2.5,
    )

    return [dows_lake, fifth_avenue, nac]


running = True


def stop_handler(signum, frame) -> None:
    global running
    running = False
    print("\n[INFO] Stop signal received. Shutting down...")


def main() -> None:
    global running

    sensors = build_sensors()

    for sensor in sensors:
        sensor.connect()

    signal.signal(signal.SIGINT, stop_handler)
    signal.signal(signal.SIGTERM, stop_handler)

    print(f"[INFO] Sending telemetry every {SEND_INTERVAL_SECONDS} seconds...")
    print("[INFO] Press Ctrl+C to stop.")

    try:
        while running:
            for sensor in sensors:
                try:
                    sensor.send_reading()
                except Exception as exc:
                    print(f"[ERROR] Failed to send reading for {sensor.device_id}: {exc}")

            time.sleep(SEND_INTERVAL_SECONDS)

    finally:
        for sensor in sensors:
            sensor.disconnect()


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"[FATAL] {exc}")
        sys.exit(1)