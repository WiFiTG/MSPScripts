# !usr/bin/python
# hacking my way through serial connections


import serial
import time


# make serial object
ser = serial.Serial(
    port = 'COM1', #COM is on windows, linux is different
    baudrate=9600, #many different baudrates are available
    parity='N',    #no idea
    stopbits=1,
    bytesize=8,
    timeout=8      #8 seconds seems to be a good timeout, may need to be increased
    )

def send_to_console(ser: serial.Serial, command: str, wait_time: float = 0.5):
    from time import sleep
    command_to_send = command + "\r"
    ser.write(command_to_send.encode('utf-8'))
    sleep(wait_time)
    print(ser.read(ser.inWaiting()).decode('utf-8'), end="")

time.sleep(1)
write2 = send_to_console()
# write3 = send_to_console(ser, ser.write("show vlan basic"))
time.sleep(1)
time.sleep(1)
settings = ser.get_settings()
name = ser.name

print(ser.isOpen())
#print(write2)
#print(write3)
print(name)