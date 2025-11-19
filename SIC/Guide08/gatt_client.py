#!/usr/bin/env python3
from pydbus import SystemBus
from gi.repository import GLib
import dbus
import time
import sys

BLUEZ_SERVICE = "org.bluez"
ADAPTER_IFACE = "org.bluez.Adapter1"
DEVICE_IFACE = "org.bluez.Device1"
GATT_CHRC_IFACE = "org.bluez.GattCharacteristic1"
DBUS_PROP_IFACE = "org.freedesktop.DBus.Properties"

CHAT_SERVICE_UUID = "12345678-1234-5678-1234-56789abcdef0"
CHAT_MSG_UUID = "12345678-1234-5678-1234-56789abcdef1"

bus = SystemBus()
mainloop = None

def find_adapter():
    """Procura adaptador bluetooth (ex: hci0)."""
    mngr = bus.get("org.bluez", "/")
    objs = mngr.GetManagedObjects()
    for path, ifaces in objs.items():
        if ADAPTER_IFACE in ifaces:
            return path
    raise RuntimeError("Nenhum adaptador encontrado.")

def find_device(target_uuid):
    """Procura dispositivo que anuncie o serviço alvo."""
    mngr = bus.get("org.bluez", "/")
    objs = mngr.GetManagedObjects()
    for path, ifaces in objs.items():
        if DEVICE_IFACE in ifaces:
            dev_props = ifaces[DEVICE_IFACE]
            uuids = dev_props.get("UUIDs", [])
            if target_uuid.lower() in [u.lower() for u in uuids]:
                return path
    return None

def notification_handler(interface, changed, invalidated, path):
    """Recebe notificações do servidor."""
    if interface != GATT_CHRC_IFACE:
        return
    if "Value" in changed:
        try:
            data = bytes(changed["Value"]).decode("utf-8")
        except Exception:
            data = str(changed["Value"])
        print(f"\nMensagem recebida: {data}\n> ", end="", flush=True)

def connect_device(dev_path):
    dev_obj = bus.get(BLUEZ_SERVICE, dev_path)
    if not dev_obj.Connected:
        print("🔗 A ligar ao dispositivo ...")
        dev_obj.Connect()
        while not dev_obj.Connected:
            time.sleep(0.5)
    print("Conectado!")
    return dev_obj

def get_characteristic_path(target_uuid):
    mngr = bus.get("org.bluez", "/")
    objs = mngr.GetManagedObjects()
    for path, ifaces in objs.items():
        if GATT_CHRC_IFACE in ifaces:
            chrc = ifaces[GATT_CHRC_IFACE]
            if chrc["UUID"].lower() == target_uuid.lower():
                return path
    return None

def main():
    global mainloop
    print("Cliente BLE Chat (usando BlueZ diretamente)")

    adapter_path = find_adapter()
    adapter = bus.get(BLUEZ_SERVICE, adapter_path)
    print(f"Adaptador encontrado: {adapter_path}")

    print("A procurar dispositivos (5s)...")
    adapter.StartDiscovery()
    time.sleep(5)
    adapter.StopDiscovery()

    dev_path = find_device(CHAT_SERVICE_UUID)
    if not dev_path:
        print("Nenhum dispositivo com o serviço de chat encontrado.")
        return

    print(f"Dispositivo com ChatService encontrado: {dev_path}")
    dev = connect_device(dev_path)

    chrc_path = get_characteristic_path(CHAT_MSG_UUID)
    if not chrc_path:
        print("Characteristic do chat não encontrada.")
        return

    print(f"Característica encontrada: {chrc_path}")

    chrc_obj = bus.get(BLUEZ_SERVICE, chrc_path)
    props_iface = dbus.Interface(bus.get_object(BLUEZ_SERVICE, chrc_path), DBUS_PROP_IFACE)

    # Subscrever a notificações
    props_iface.connect_to_signal("PropertiesChanged", notification_handler, path=chrc_path)
    chrc_iface = dbus.Interface(bus.get_object(BLUEZ_SERVICE, chrc_path), GATT_CHRC_IFACE)
    chrc_iface.StartNotify()

    print("Subscrito! Escreve mensagens e carrega ENTER (ou /quit para sair)\n")

    mainloop = GLib.MainLoop()
    import threading
    def input_loop():
        while True:
            msg = input("> ").strip()
            if msg in ("/quit", "exit", "q"):
                chrc_iface.StopNotify()
                dev.Disconnect()
                mainloop.quit()
                break
            if msg:
                try:
                    chrc_iface.WriteValue(dbus.ByteArray(msg.encode("utf-8")), {})
                except Exception as e:
                    print(f"Erro ao enviar: {e}")

    threading.Thread(target=input_loop, daemon=True).start()
    mainloop.run()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nEncerrado pelo utilizador.")
