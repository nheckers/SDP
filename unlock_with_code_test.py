import serial
import time
import kwikset_protocol

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

def unlock_with_code(ser, user_code_hex):
    print(f"[ACTION] Attempting to unlock with code: {user_code_hex}")
    cmd = "e706"  # Command type: unlock with code
    data = user_code_hex
    packet = kwikset_protocol.generate_packet(cmd, data)
    send_packet(ser, packet, "UNLOCK_WITH_CODE")

def main():
    print("[INFO] Starting unlock-with-code test...")

    # Connect to serial port
    ser = serial.Serial("COM3", 9600, timeout=1)
    time.sleep(2)

    # Step 1: Init
    send_init_sequence(ser, "INIT")

    # Step 2: Try unlocking with a known user code (example: 123456)
    user_code = "313233343536"  # hex representation of ASCII "123456"
    unlock_with_code(ser, user_code)

    ser.close()
    print("[INFO] Unlock-with-code test complete.")

if __name__ == "__main__":
    main()
