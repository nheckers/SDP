import time
import serial
import kwikset_protocol
from binascii import hexlify

def read_response(ser):
    print("[DEBUG] Waiting for response from PCB...")
    raw_bytes = b''
    limit = 0
    max_tries = 50

    while limit < max_tries:
        byte = ser.read(1)
        if byte:
            raw_bytes += byte
            if raw_bytes[0] == 0xBD and len(raw_bytes) >= 2:
                expected_len = raw_bytes[1] + 2  # length byte + SOP + checksum
                if len(raw_bytes) >= expected_len:
                    break
        limit += 1

    if raw_bytes:
        packet_str = hexlify(raw_bytes).decode()
        print(f"[RECEIVED] Raw packet from PCB: {packet_str}")
        try:
            parsed = kwikset_protocol.parse_packet(packet_str)
            print(f"[PARSED] {parsed}")
        except Exception as e:
            print(f"[ERROR] Failed to parse packet: {e}")
    else:
        print("[RECEIVED] No valid packet received from PCB.")

def main():
    print("[INFO] Starting Kwikset Lock Test")
    ser = serial.Serial("COM3", 9600, timeout=1)
    time.sleep(2)

    print("[ACTION] Sending LOCK command...")
    ser.write(kwikset_protocol.generate_lock_packet())
    time.sleep(1)
    read_response(ser)

    print("[ACTION] Sending UNLOCK command...")
    ser.write(kwikset_protocol.generate_unlock_packet())
    time.sleep(1)
    read_response(ser)

    ser.close()
    print("[INFO] Test complete.")

if __name__ == "__main__":
    main()
