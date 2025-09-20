import time
import kwikset
import kwikset_protocol

def send_lock_unlock_with_delay(delay_seconds):
    print(f"[TEST] Trying delay = {delay_seconds:.3f} seconds")
    
    # Lock
    kwikset.ser.write(kwikset_protocol.generate_lock_packet())
    kwikset.ser.flush()
    print("[DEBUG] Sent LOCK packet")
    time.sleep(delay_seconds)

    # Unlock
    kwikset.ser.write(kwikset_protocol.generate_unlock_packet())
    kwikset.ser.flush()
    print("[DEBUG] Sent UNLOCK packet")
    print()

def main():
    kwikset.setup_serial()
    kwikset.setup_arduinobreakout_pins()
    kwikset.init_kwikset_lock()

    print("[INFO] Starting delay test between LOCK and UNLOCK packets...")

    for ms in range(50, 1001, 50):  # Test delays from 50ms to 1000ms in 50ms steps
        delay = ms / 1000.0
        send_lock_unlock_with_delay(delay)
        time.sleep(2)  # Pause between test cycles to let motor settle

    print("[INFO] Test complete. Observe which delays succeeded.")

if __name__ == "__main__":
    main()
