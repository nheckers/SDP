import kwikset
import kwikset_protocol
import time
import os

kwikset.setup_serial()
kwikset.setup_arduinobreakout_pins()
kwikset.init_kwikset_lock()

def send_packet_bytewise(packet, label):
    print(f"[ACTION] Sending {label} (byte-by-byte pulse)...")
    os.system("echo high > /sys/class/gpio/gpio214/direction")
    for b in packet:
        kwikset.ser.write(bytes([b]))
        time.sleep(0.005)  # short delay between bytes
    os.system("echo low > /sys/class/gpio/gpio214/direction")

def pulse_lock():
    lock_packet = kwikset_protocol.generate_lock_packet()
    send_packet_bytewise(lock_packet, "LOCK")

def pulse_unlock():
    unlock_packet = kwikset_protocol.generate_unlock_packet()
    send_packet_bytewise(unlock_packet, "UNLOCK")

while True:
    action = input("What do you want to do? (lock/unlock/exit): ").strip().lower()

    if action == "lock":
        pulse_lock()
    elif action == "unlock":
        pulse_unlock()
    elif action == "exit":
        print("Exiting...")
        break
    else:
        print("Invalid input. Please type 'lock', 'unlock', or 'exit'.")
