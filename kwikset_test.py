import time
import kwikset
import serial

def main():
    print("[INFO] Starting Kwikset Lock Test")
    kwikset.setup_serial()
    kwikset.init_kwikset_lock()

    print("[ACTION] Sending LOCK command...")
    kwikset.lock()
    time.sleep(3)

    print("[DEBUG] Querying lock status before unlock...")

    # Clear buffer before receiving
    kwikset.ser.reset_input_buffer()

    # Read raw response manually for insight
    raw_bytes = b''
    limit = 0
    max_tries = 20
    while limit < max_tries:
        byte = kwikset.ser.read(1)
        if byte:
            raw_bytes += byte
            if raw_bytes[0] == 0xBD and len(raw_bytes) >= 2:
                expected_len = raw_bytes[1] + 2  # length byte + SOP + checksum
                if len(raw_bytes) >= expected_len:
                    break
        limit += 1

    if raw_bytes:
        print(f"[RECEIVED] Raw packet from PCB: {raw_bytes.hex()}")
    else:
        print("[RECEIVED] No valid packet received from PCB.")

    # Call standard get_status for parsed result
    status = kwikset.get_status()
    print(f"[DEBUG] Lock status: {status}")

    time.sleep(5)

    print("[ACTION] Sending UNLOCK command...")
    kwikset.unlock()

if __name__ == "__main__":
    main()
