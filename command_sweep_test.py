import serial
import time

def send_packet(ser, hex_str, label):
    packet = bytes.fromhex(hex_str)
    print(f"[DEBUG] Sending {label} packet: {packet.hex()}")
    ser.write(packet)
    time.sleep(0.5)

def send_init_sequence(ser, phase="INIT"):
    init_packets = [
        "BD0401E7071A", "BD0402E74D53", "BD0403E7021D", "BD0404E70A12",
        "BD0405E71801", "BD0406E70913", "BD0807E7420101010155", "BD0B08E70F1503130147120540"
    ]
    for i, pkt in enumerate(init_packets):
        send_packet(ser, pkt, f"{phase} {i}")

def generate_packet(packet_id_hex, command_id_hex):
    sop = "BD"
    length = "04"
    cmd_type = "E7"
    payload = length + packet_id_hex + cmd_type + command_id_hex
    crc = calculate_crc(payload)
    return sop + payload + crc

def calculate_crc(hex_payload):
    crc = 0xFF
    for i in range(0, len(hex_payload), 2):
        crc ^= int(hex_payload[i:i+2], 16)
    return f"{crc:02X}"

def main():
    print("[INFO] Starting command sweep test (0x01 to 0x0F)...")

    ser = serial.Serial("COM3", 9600, timeout=1)
    time.sleep(2)

    # Full initialization before sending commands
    send_init_sequence(ser, "INIT")

    # Use packet ID 0x09 for all commands
    packet_id = "09"

    # Try command IDs from 0x01 to 0x0F
    for cmd_id in range(1, 16):
        cmd_hex = f"{cmd_id:02X}"
        full_packet = generate_packet(packet_id, cmd_hex)
        send_packet(ser, full_packet, f"COMMAND 0x{cmd_hex}")
        time.sleep(1.5)

    ser.close()
    print("[INFO] Command sweep complete.")

if __name__ == "__main__":
    main()
