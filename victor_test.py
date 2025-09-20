import kwikset

kwikset.setup_serial()
kwikset.setup_arduinobreakout_pins()
kwikset.init_kwikset_lock()

while True:

    action = input("What do you want to do? (lock/unlock/exit): ").strip().lower()

    if action == "lock":
        kwikset.lock()
        kwikset.get_status
    elif action == "unlock":
        kwikset.unlock()
        kwikset.get_status
    elif action == "exit":
        print("Exiting...")
        break
    else:
        print("Invalid input. Please type 'lock', 'unlock', or 'exit'.")