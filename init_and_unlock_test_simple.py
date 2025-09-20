import serial
import time

def send_packet(ser, hex_str, label):
    packet = bytes.fromhex(hex_str)
    print(f"[DEBUG] Sending {label} packet: {packet.hex()}")
    ser.write(packet)
    time.sleep(0.3)

def send_init_sequence(ser, phase="INIT"):
    init_packets = [
        "BD0401E7071A", "BD0402E74D53", "BD0403E7021D", "BD0404E70A12",
        "BD0405E71801", "BD0406E70913", "BD0807E7420101010155", "BD0B08E70F1503130147120540"
    ]
    for i, pkt in enumerate(init_packets):
        send_packet(ser, pkt, f"{phase} {i}")

def main():
    print("[INFO] Sending INIT → UNLOCK (0x05) sequence...")

    ser = serial.Serial("COM3", 9600, timeout=1)
    time.sleep(2)

    # Initialization
    send_init_sequence(ser, "INIT")

    # Unlock command using 0x05
    unlock_packet = "BD0409E70510"
    send_packet(ser, unlock_packet, "UNLOCK")

    ser.close()
    print("[INFO] Unlock test complete.")

if __name__ == "__main__":
    main()
