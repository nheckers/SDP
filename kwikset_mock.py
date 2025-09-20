def setup_serial():
    print("[MOCK] setup_serial() called")

def setup_arduinobreakout_pins():
    print("[MOCK] setup_arduinobreakout_pins() called")

def lock():
    print("[MOCK] lock() called — Door would be locked")

def unlock():
    print("[MOCK] unlock() called — Door would be unlocked")

def get_status():
    print("[MOCK] get_status() called")
    return "MOCKED_STATUS"