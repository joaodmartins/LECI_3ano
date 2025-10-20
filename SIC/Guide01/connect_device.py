#!/usr/bin/env python3
import sys
import time
from pydbus import SystemBus

def connect_device(mac_address):
    bus = SystemBus()
    device_path = "/org/bluez/hci0/dev_" + mac_address.replace(":", "_")

    print(f"🔍 Device path: {device_path}")
    try:
        device = bus.get("org.bluez", device_path)
    except Exception as e:
        print(f"❌ Device not found on BlueZ: {e}")
        print("💡 Tip: run 'bluetoothctl scan on' first so BlueZ registers the device.")
        return False

    try:
        print("🔗 Connecting to device...")
        device.Connect()
        time.sleep(2)  # give it a moment
        props = device.GetAll("org.bluez.Device1")
        if props.get("Connected", False):
            print("✅ Successfully connected!")
            return True
        else:
            print("⚠️ Connection attempt made, but device not marked as connected.")
            return False
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 connect_device.py <MAC_ADDRESS>")
        sys.exit(1)
    connect_device(sys.argv[1])
