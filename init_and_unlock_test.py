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
    print("[INFO] Starting full init + unlock test...")

    # Connect to serial port
    ser = serial.Serial("COM3", 9600, timeout=1)  # Change COM port if needed
    time.sleep(2)

    # Step 1: Send initialization packets and print each
    init_packets = calculate_init_packets()
    for i, pkt in enumerate(init_packets):
        print(f"[DEBUG] Sending INIT packet {i}: {pkt.hex()}")
        ser.write(pkt)
        time.sleep(0.3)

    # Step 2: Wait and then send correct unlock packet from datasheet
    print("[INFO] Sending correct manual unlock packet...")
    unlock_packet = bytes([0xBD, 0x04, 0x09, 0xE7, 0x05, 0x10])
    print(f"[DEBUG] Unlock packet: {unlock_packet.hex()}")
    time.sleep(1)
    ser.write(unlock_packet)

    ser.close()
    print("[INFO] Unlock command sent. Test complete.")

if __name__ == "__main__":
    main()
