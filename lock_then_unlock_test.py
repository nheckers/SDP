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
    print("[INFO] Starting lock + unlock (with user code) sequence test...")

    # Connect to serial port
    ser = serial.Serial("COM3", 9600, timeout=1)
    time.sleep(2)

    # Step 1: Initialization
    init_packets = calculate_init_packets()
    for i, pkt in enumerate(init_packets):
        print(f"[DEBUG] Sending INIT packet {i}: {pkt.hex()}")
        ser.write(pkt)
        time.sleep(0.3)

    # Step 2: Lock command
    lock_packet = bytes([0xBD, 0x04, 0x06, 0xE7, 0x03, 0x19])
    print(f"[ACTION] Sending LOCK command: {lock_packet.hex()}")
    ser.write(lock_packet)
    time.sleep(3)

    # Step 3: Unlock with code (e.g., 12 34 56 78 90)
    print("[ACTION] Sending UNLOCK_WITH_CODE command...")
    unlock_code = '1234567890'
    unlock_data = '1234567890'  # Replace this if your lock has a different user code

    # Send unlock_with_code packet using kwikset_protocol logic
    cmd = 'e706'  # UNLOCK_WITH_CODE
    data = '1234567890'
    packet_hex = kwikset_protocol.generate_packet(cmd, data)
    unlock_with_code_packet = bytes.fromhex(packet_hex)
    print(f"[DEBUG] Unlock with code packet: {packet_hex}")
    ser.write(unlock_with_code_packet)

    ser.close()
    print("[INFO] Lock + Unlock with user code test complete.")

if __name__ == "__main__":
    main()
