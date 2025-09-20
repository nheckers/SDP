import kwikset
import time

kwikset.setup_serial()
kwikset.setup_arduinobreakout_pins()
kwikset.init_kwikset_lock()

count = 1

while True:
    kwikset.lock()
    kwikset.get_status()
    print(f"Lock Packet Sent [{count}]")
    count += 1
    time.sleep(3)
