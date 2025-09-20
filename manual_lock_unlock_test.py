import time
import kwikset
import kwikset_protocol

# SET YOUR TEST DELAY HERE (in seconds)
DELAY_SECONDS = 0.5  # You can manually change this value before each run

def main():
    kwikset.setup_serial()
    kwikset.setup_arduinobreakout_pins()
    kwikset.init_kwikset_lock()

    print(f"[INFO] Sending LOCK packet...")
    kwikset.ser.write(kwikset_protocol.generate_lock_packet())
    kwikset.ser.flush()

    print(f"[WAIT] Sleeping for {DELAY_SECONDS} seconds...")
    time.sleep(DELAY_SECONDS)

    print("[INFO] Sending UNLOCK packet...")
    kwikset.ser.write(kwikset_protocol.generate_unlock_packet())
    kwikset.ser.flush()

    print("[INFO] Test complete.")

if __name__ == "__main__":
    main()
