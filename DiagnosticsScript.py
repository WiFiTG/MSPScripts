# Lane, Tim, and Raf.
# This is NOT an automation or error checking tool, it may be later on, but not yet.

# importing modules and defining variables
from netmiko import SSHDetect, ConnectHandler
# Setting variables
switch_ip = input("What is the IP address of the switch: ")
switch_username = input("what is the username: ")
switch_password = input("What is the password: ")
p = switch_password

# setting user input as variable and initiating autodetect
device = {
    "device_type": "autodetect",
    "host": switch_ip,
    "username": switch_username,
    "password": p,
    "session_log": "log.txt"
}

# Trying SSHDetect
net_connect = ConnectHandler(**device)
OSGuesser = SSHDetect(**device)
best_match = OSGuesser.autodetect()
# Update the 'device' dictionary with the device_type
device["device_type"] = best_match

# Not sure what connect handler does here, other than query the device from kwargs?
with ConnectHandler(**device) as connection:
    print(connection.find_prompt())

# Disconnecting the first session, duh.
net_connect.disconnect()

# defining the OS/platform as the best_match by SSH Detect
os_type = best_match

# defining a secondary device because I was unsure what to put here. I am not a developer, but I try my best
device2 = {
    "device_type": best_match,
    "host": switch_ip,
    "username": switch_username,
    "password": p,
    "session_log": "log.txt"

}
# connecting to device
net_connect = ConnectHandler(**device2)
print('Attempting to connect to ' + switch_ip)

# at this point connection should be established, no?


print('-' * 79)
print("1 Find MAC Address")
print('2 Show routes')
print('3 Find loop SLPP, ELRP, STP')
print('4 Test Cable termination')
print('5 Show interfaces verbose')
print('6 Show access profiles')
print('7 Show snmp configuration')
print('8 Show lldp neighbors')
command_list = input('What would you like to do? Please enter a number from the list above: \n')

# Simple if then statement to detect OS. This should probably be broken into separate imports.
if command_list == "1":
    os_type = best_match
    net_connect = ConnectHandler(**device2)
    macaddress = input('what is the mac address(xx.xx.xx.xx): \n')
    if OSGuesser.autodetect() == "extreme_exos":
        output = net_connect.send_command("show fdb")
        print(output)
    elif OSGuesser.autodetect() == "extreme_vsp":
        output = net_connect.send_command("show vlan mac-address-entry mac {}".format(macaddress))
        print(output)
    else:
        print("Device type not supported")
else:
    print("please select something else, danke")


net_connect.disconnect()
