#!/usr/bin/env python3
"""
scan_and_services.py
- Scan devices with PyBluez
- Try to list services via PyBluez.find_service()
- Fallback: query BlueZ via D-Bus (pydbus) to get UUIDs
- Map common UUIDs to friendly names
"""

import bluetooth
import sys
import time

# Optional: pydbus fallback
try:
    from pydbus import SystemBus
    HAVE_PYDBUS = True
except Exception:
    HAVE_PYDBUS = False

# Mapping common Bluetooth service UUIDs (16-bit / 32-bit or canonical 128-bit)
UUID_FRIENDLY = {
    # Common 16-bit assigned numbers in 128-bit form
    "00001101-0000-1000-8000-00805f9b34fb": "Serial Port (SPP)",
    "00001108-0000-1000-8000-00805f9b34fb": "Headset",
    "00001112-0000-1000-8000-00805f9b34fb": "Human Interface Device (HID)",
    "0000110b-0000-1000-8000-00805f9b34fb": "Audio Source (A2DP)",
    "0000110e-0000-1000-8000-00805f9b34fb": "AV Remote Control (AVRCP)",
    "0000111e-0000-1000-8000-00805f9b34fb": "Handsfree",
    "00001105-0000-1000-8000-00805f9b34fb": "OBEX Object Push",
    "00001106-0000-1000-8000-00805f9b34fb": "OBEX File Transfer",
    # Add more as needed...
}

def friendly_name_for_uuid(uuid):
    if not uuid:
        return None
    u = uuid.lower()
    # If small 16-bit uuid like '1101' convert to base form
    if len(u) <= 4:
        u = f"0000{u}-0000-1000-8000-00805f9b34fb"
    # normalize common forms
    if u in UUID_FRIENDLY:
        return UUID_FRIENDLY[u]
    # try strip brackets / uppercase variations
    u = u.replace("{", "").replace("}", "")
    return UUID_FRIENDLY.get(u, None)

def scan_and_list_services(scan_duration=8):
    print(f"[*] Scanning for Bluetooth devices for {scan_duration}s...")
    try:
        nearby = bluetooth.discover_devices(duration=scan_duration, lookup_names=True)
    except Exception as e:
        print("Error running discover_devices():", e)
        nearby = []

    if not nearby:
        print("[!] No devices found by PyBluez scan.")
    else:
        print(f"[+] Found {len(nearby)} device(s).")

    results = []
    for addr, name in nearby:
        print("\n---")
        print(f"Device: {name} [{addr}]")
        entry = {"addr": addr, "name": name, "pybluez_services": [], "dbus_uuids": []}

        # 1) Try PyBluez find_service()
        try:
            services = bluetooth.find_service(address=addr)
            if services:
                print(f" PyBluez: found {len(services)} service entries:")
                for s in services:
                    sname = s.get("name") or "<no-name>"
                    suuid = s.get("service-id") or s.get("service-classes") or ""
                    port = s.get("port")
                    print(f"   - {sname} | UUID: {suuid} | port: {port}")
                    entry["pybluez_services"].append({"name": sname, "uuid": suuid, "port": port})
            else:
                print(" PyBluez: no services returned by find_service()")
        except Exception as e:
            print(" PyBluez find_service() error:", e)

        # 2) Fallback: use D-Bus to get UUIDs (if pydbus available)
        if HAVE_PYDBUS:
            try:
                bus = SystemBus()
                mng = bus.get("org.bluez", "/").GetManagedObjects()
                # scan managed objects for Device1 with matching Address
                found = False
                for path, interfaces in mng.items():
                    devinfo = interfaces.get("org.bluez.Device1")
                    if devinfo and devinfo.get("Address", "").upper() == addr.upper():
                        found = True
                        uuids = devinfo.get("UUIDs") or []
                        if uuids:
                            print(f" D-Bus: BlueZ knows {len(uuids)} UUID(s):")
                            for u in uuids:
                                fname = friendly_name_for_uuid(u) or "<unknown>"
                                print(f"   - {u} -> {fname}")
                                entry["dbus_uuids"].append({"uuid": u, "friendly": fname})
                        else:
                            print(" D-Bus: BlueZ device object has no UUIDs listed.")
                        break
                if not found:
                    print(" D-Bus: device object not present in BlueZ managed objects (try scanning with bluetoothctl first).")
            except Exception as e:
                print(" D-Bus error (pydbus):", e)
                if not HAVE_PYDBUS:
                    print(" pydbus not installed; install with: pip install pydbus")
        else:
            print(" D-Bus fallback not available (pydbus not installed). Consider installing pydbus.")

        results.append(entry)

    return results

if __name__ == "__main__":
    r = scan_and_list_services(scan_duration=8)
    # Summary:
    print("\n\nSummary:")
    for e in r:
        ns = len(e["pybluez_services"]) + len(e["dbus_uuids"])
        print(f" - {e['name']} [{e['addr']}] -> total profiles/UUIDs found: {ns}")
