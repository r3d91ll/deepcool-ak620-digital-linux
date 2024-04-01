import time
import hid
import psutil

VENDOR_ID = 0x3633  # DeepCool's Vendor ID
PRODUCT_ID = 0x0002  # AK620's Product ID
INTERVAL = 2

def get_bar_value(input_value):
    return (input_value - 1) // 10 + 1

def get_data(value=0, mode='util'):
    value = int(value)
    base_data = [16, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    numbers = [int(char) for char in str(value)]
    base_data[4] = get_bar_value(value)
    if mode == 'util':
        base_data[1] = 76
    elif mode == 'start':
        base_data[1] = 170
    elif mode == 'temp':
        base_data[1] = 19

    # Place the numbers into the base data array starting at position 5, moving backwards
    for i, num in enumerate(reversed(numbers), start=5):
        base_data[i] = num

    # Convert the list of integers to bytes
    return bytes(base_data)

def get_temperature():
    # Subtract 10 to compensate for the observed offset in the HID device's display
    temp = round(psutil.sensors_temperatures()['k10temp'][0].current) - 10
    #print(f"Adjusted Temperature to send: {temp}")  # Debug output
    return get_data(value=temp, mode='temp')

def get_utils():
    utils = psutil.cpu_percent(interval=1)
    # If the issue was related to scaling, this adjustment would be for testing:
    # However, this is conceptually incorrect for percentage scaling; it's for illustration.
    #scaled_utils = utils * 10  # Incorrect for percentage scaling; see above explanation.
    print(f"CPU Usage: {utils}")
    return get_data(value=int(utils), mode='util')

try:
    h = hid.Device(vid=VENDOR_ID, pid=PRODUCT_ID)
    h.nonblocking = 1  # Set nonblocking to 1 (integer)
    h.write(get_data(mode="start"))
    while True:
        temp = get_temperature()
        h.write(temp)
        time.sleep(INTERVAL)
        utils = get_utils()
        h.write(utils)
        time.sleep(INTERVAL)
except IOError as ex:
    print(ex)
    print("Ensure that the AK620 is connected and the script has the correct Vendor ID and Product ID.")
except KeyboardInterrupt:
    print("Script terminated by user.")
except Exception as ex:
    print(f"An unexpected error occurred: {ex}")
finally:
    if 'h' in locals() or 'h' in globals():
        h.close()

