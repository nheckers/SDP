#!/usr/bin/python3

# This is a library for providing access to Kwikset Smartcode Locks via UART
# The h/w interface is 3.3V 9600 baud 8N1 standard UART
# This is more of a protocol encoder/decoder though

import kwikset_protocol
import serial
import time
import os
import threading
from binascii import hexlify, unhexlify
import platform

ser = None

def setup_arduinobreakout_pins():
    if platform.system() != "Linux":
        print("[INFO] Skipping GPIO setup — not on a Linux system.")
        return

    # First let's make sure all the pins are exported for config
    os.system("echo 214 > /sys/class/gpio/export")
    os.system("echo 248 > /sys/class/gpio/export")
    os.system("echo 249 > /sys/class/gpio/export")
    os.system("echo 216 > /sys/class/gpio/export")
    os.system("echo 217 > /sys/class/gpio/export")
    # Next lets Tristate all the outputs
    os.system("echo low > /sys/class/gpio/gpio214/direction")
    # Setup the buffer/level shifter I/O directions
    os.system("echo low > /sys/class/gpio/gpio248/direction")
    os.system("echo high > /sys/class/gpio/gpio249/direction")
    # Disable the external pull ups
    os.system("echo low > /sys/class/gpio/gpio216/direction")
    os.system("echo low > /sys/class/gpio/gpio217/direction")
    # Remove tristate 
    os.system("echo high > /sys/class/gpio/gpio214/direction")

def setup_serial(port="COM3"):
    global ser
    try:
        ser = serial.Serial(port, 9600, timeout=0)
        print(f"[INFO] Serial port {port} opened.")
    except serial.SerialException as e:
        print(f"[ERROR] Could not open port {port}: {e}")
    print(f"[DEBUG] ser is: {ser}")  # Add this

def init_kwikset_lock():
    global ser
    if ser is None:
        print("Serial Port not setup")
        return False
    for num in range(8):
        ser.write(kwikset_protocol.generate_init_packet(num))
        # time.sleep(10)

def unlock():
    global ser
    if ser is None:
        print("Serial Port not setup")
        return False

    packet = kwikset_protocol.generate_unlock_packet()

    # Add debug info for analysis
    print("[DEBUG] Unlock packet (raw bytes):", packet)
    print("[DEBUG] Unlock packet (hex):", kwikset_protocol.hexlify(packet))
    print("[DEBUG] Unlock packet (list of hex values):", [hex(b) for b in packet])

    ser.reset_input_buffer()
    ser.reset_output_buffer()
    time.sleep(10)  # Give the lock a moment to prepare
    ser.write(packet)
    print("Unlock Packet Sent")


def lock():
    global ser
    if ser is None:
        print("Serial Port not setup")
        return False
    ser.write(kwikset_protocol.generate_lock_packet())
    packet = kwikset_protocol.generate_lock_packet()
    print("[DEBUG] Lock packet being sent:", packet)
    ser.write(packet)
    print("Lock Packet Sent")
    time.sleep(10)  # Give the lock a moment to prepare


def get_status():
    global ser
    if ser is None:
        print("Serial Port not setup")
        return False
    limit = 0
    MAX_TRIES = 20
    header = None
    while (limit < MAX_TRIES) and (header != '\xbd'):
        header = ser.read().decode(errors='ignore')  # decode byte to string
        limit += 1
    if limit == MAX_TRIES:
        print(f"No start byte found in {MAX_TRIES} characters")
        return False
    hex_length = hexlify(ser.read()).decode()
    length = int(hex_length, 16)
    pkt = "bd%s%s" % (hex_length, hexlify(ser.read(length)).decode())
    return kwikset_protocol.parse_packet(pkt)