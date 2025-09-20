import time
import serial
import kwikset_protocol

def calculate_init_packets():
    INIT_CMDS = ['e707','e74d','e702','e70a','e718','e709','e742','e70f']
    INIT_DATAS = ['','','','','','','01010101','15031301471205']
    packets = []

    for i in range(len(INIT_CMDS)):
        cmd = INIT_CMDS[i]
        data = INIT_DATAS[i]
        pkt = kwikset_protocol.generate_packet(cmd, data)
        packets.append(bytes.fromhex(pkt))
    return packets

def main():
    print("[INFO] Starting buzzer test...")

    # Connect to serial port
    ser = serial.Serial("COM3", 9600, timeout=1)
    time.sleep(2)

    # Step 1: Send initialization packets
    init_packets = calculate_init_packets()
    for i, pkt in enumerate(init_packets):
        print(f"[DEBUG] Sending INIT packet {i}: {pkt.hex()}")
        ser.write(pkt)
        time.sleep(0.3)

    # Step 2: Send buzzer command (0x1E = 3 seconds)
    buzzer_cmd = 'e74c'  # 0xE7 = Command Type, 0x4C = SET_BUZZER_ON
    duration = '1e'      # 0x1E = 30 × 100ms = 3 seconds
    packet_hex = kwikset_protocol.generate_packet(buzzer_cmd, duration)
    buzzer_packet = bytes.fromhex(packet_hex)
    print(f"[ACTION] Sending BUZZER command: {packet_hex}")
    ser.write(buzzer_packet)

    ser.close()
    print("[INFO] Buzzer command sent. Test complete.")

if __name__ == "__main__":
    main()
