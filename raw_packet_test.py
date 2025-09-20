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

def generate_unlock_packet(packet_id_hex):
    sop = "BD"
    length = "04"
    cmd_type = "E7"
    unlock_cmd = "05"
    payload = length + packet_id_hex + cmd_type + unlock_cmd
    crc = calculate_crc(payload)
    return sop + payload + crc

def calculate_crc(hex_payload):
    crc = 0xFF
    for i in range(0, len(hex_payload), 2):
        crc ^= int(hex_payload[i:i+2], 16)
    return f"{crc:02X}"

def main():
    print("[INFO] Starting unlock (0x05) variant test...")

    ser = serial.Serial("COM3", 9600, timeout=1)
    time.sleep(2)

    # Step 1: Initialization and Lock
    send_init_sequence(ser, "INIT")
    send_packet(ser, "BD0406E70319", "LOCK")

    time.sleep(3)

    # Step 2: Re-initialize
    send_init_sequence(ser, "RE-INIT")

    # Step 3: Try sending multiple unlock packets with different packet IDs
    print("[INFO] Testing multiple unlock packets with varying packet IDs...")
    for pkt_id in range(9, 16):  # try packet IDs 0x09 to 0x0F
        pkt_id_hex = f"{pkt_id:02X}"
        unlock_pkt = generate_unlock_packet(pkt_id_hex)
        send_packet(ser, unlock_pkt, f"UNLOCK packet_id=0x{pkt_id_hex}")
        time.sleep(1.5)

    ser.close()
    print("[INFO] Unlock variant test complete.")

if __name__ == "__main__":
    main()
