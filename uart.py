#!/usr/bin/env python
import mraa
import sys
from datetime import datetime



def string_to_float(data_string):
    try:
        data_as_float = eval(str(data_string))
        return round( data_as_float, 2)
    except:
        return 0.00

def serial_number():
    serial_number = None
    with open('device.txt', 'r') as f:
        name = f.readline()
        serial_number = f.readline().strip()

    return serial_number

############################################################
# Initialize UART
sys.stdout.write("Initializing UART...")
u=mraa.Uart(0)
print("...done")

# Set UART parameters
print("Setting UART parameters: baudrate 9600, 8N1, no flow control")
u.setBaudRate(9600)
u.setMode(8, mraa.UART_PARITY_NONE, 1)
u.setFlowcontrol(False, False)

# Flush!
u.flush()

# Data buffer
data_buffer = []
incoming_data_string = ""


# Start a neverending loop waiting for data to arrive.
# Press Ctrl+C to get out of it.

print("Sending control signal to MSP")
# Control => #
# Expected first byte returned => *
u.write(bytearray('#'))

print("Waiting for data...\n\n")
while True:
    if u.dataAvailable():
        # Read a single byte over uart
        data_byte = u.readStr(1)

        if(data_byte=='*'):
            print "FUCK YEA"
            if (incoming_data_string != ""):
                data_buffer.append( format(string_to_float(incoming_data_string), '0.3f') )
                print data_buffer
            # Reset data string
            incoming_data_string = ""
        elif(data_byte == '#'):
            # Get serial
            sn = serial_number()
            time_stamp = datetime.now().strftime("%Y-%m-%dT%H:%M:00")
            # Prepend time stamp and serial number
            data_buffer.insert(0, time_stamp)
            data_buffer.insert(0, sn) 

            print "Writing buffer to file."

            file_path = "data/sensor_data_latest.txt"
            with open(file_path, 'a') as f:
                string = ', '.join(data_buffer)
                f.write(string + '\n')

            u.flush()
        else:
            # Otherwise, build out next value
            incoming_data_string += data_byte




###########################################
