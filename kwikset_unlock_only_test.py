import time
import kwikset

def main():
    print("[INFO] Starting Kwikset Unlock Test")

    # Step 1: Setup serial connection
    print("[INFO] Setting up serial connection...")
    kwikset.setup_serial()

    # Step 2: Initialize the Kwikset lock
    print("[INFO] Initializing Kwikset lock...")
    kwikset.init_kwikset_lock()

    # Step 3: Delay for stability
    time.sleep(3)

    # Step 4: Attempt to unlock
    print("[ACTION] Sending UNLOCK command...")
    kwikset.unlock()

    print("[INFO] Unlock attempt complete.")

if __name__ == "__main__":
    main()
