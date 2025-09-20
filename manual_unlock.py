import serial
import time

def main():
    print("[INFO] Starting manual unlock test...")

    # Adjust COM port if needed
    ser = serial.Serial("COM3", 9600, timeout=1)
    time.sleep(2)  # Allow port to stabilize

    # Manually crafted unlock packet as per documentation
    unlock_packet = bytes([0xBD, 0x04, 0x09, 0xE7, 0x05, 0x10])
    print(f"[DEBUG] Sending manual unlock packet: {unlock_packet.hex()}")

    ser.write(unlock_packet)
    ser.close()

    print("[INFO] Manual unlock command sent.")

if __name__ == "__main__":
    main()
