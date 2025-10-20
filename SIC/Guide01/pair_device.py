#!/usr/bin/env python3
import sys, time
from pydbus import SystemBus

def pair_device(mac_address):
    bus = SystemBus()
    adapter_path = "/org/bluez/hci0"
    device_path = adapter_path + "/dev_" + mac_address.replace(":", "_")

    print(f"🔍 Looking for device at {device_path}")
    try:
        device = bus.get("org.bluez", device_path)
    except Exception as e:
        print(f"❌ Device not found in BlueZ: {e}")
        print("💡 Tip: run 'bluetoothctl scan on' first so BlueZ registers the device.")
        return False

    try:
        print("🔗 Starting pairing...")
        device.Pair()  # Initiate pairing

        for i in range(10):
            props = device.GetAll("org.bluez.Device1")
            if props.get("Paired", False):
                print("✅ Successfully paired!")
                return True
            print(f"⏳ Waiting... ({i+1}/10)")
            time.sleep(1)

        print("⚠️ Pairing timed out or failed.")
        return False

    except Exception as e:
        print(f"❌ Error during pairing: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 pair_device.py <MAC_ADDRESS>")
        sys.exit(1)

    mac = sys.argv[1]
    success = pair_device(mac)
    if success:
        print("🎉 Device paired.")
    else:
        print("❌ Failed to pair device.")
