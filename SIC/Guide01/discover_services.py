import bluetooth

KNOWN_SERVICES = {
    "00001101-0000-1000-8000-00805f9b34fb": "Serial Port",
    "0000110a-0000-1000-8000-00805f9b34fb": "Audio Source",
    "0000110b-0000-1000-8000-00805f9b34fb": "Audio Sink",
    "0000110c-0000-1000-8000-00805f9b34fb": "A/V Remote Control Target",
    "0000110e-0000-1000-8000-00805f9b34fb": "Handsfree",
    "00001112-0000-1000-8000-00805f9b34fb": "Headset",
    "0000112f-0000-1000-8000-00805f9b34fb": "Phonebook Access - PCE",
}

def discover_services(device_addr):
	services = bluetooth.find_service(address=device_addr)
	if services:
		print(f"Services and UUIDs for device {device_addr}:")
		for service in services:
			service_classes = service.get('service-classes', []) 
			service_id = service.get('service-id', '')

			friendly_name = KNOWN_SERVICES.get(service_id.lower(), "Unknown Service")
			print(f"|--| Service Classes: {service['service-classes']}")
			print(f"| | Service UUID: {service['service-id']}")
			print(f"|")
	else:
		print(f"No services found for {device_addr}.")

def discover_devices_and_services():
    print("Discovering nearby Bluetooth devices...")
    devices = bluetooth.discover_devices(duration=8, lookup_names=True)
    if not devices:
        print("No devices found.")
        return

    print(f"Found {len(devices)} device(s):")
    for addr, name in devices:
        print(f"  Device: {name} [{addr}]")
        discover_services(addr)
        print("-" * 40)


if __name__ == "__main__":
	discover_devices_and_services()
