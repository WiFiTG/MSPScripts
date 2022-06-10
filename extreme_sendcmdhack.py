#!usr/bin/env python
# this is a hacked together script to bust through some spreadsheets real quick,
# it reads from a text file and connects to the IPs
# it can find if the credentials match, then it will input commands
# on the devices that you choose with send_command()
# it gracefully disconnects each time a switch is configured
# and at the end of the session as well.

from netmiko import ConnectHandler

# create a text file that you can paste IP addresses line by line as this script reads directly from it
with open('devices.txt') as devices:
    for IP in devices:
        Device = {
            # eventually I'll move these to their own functions? that way we can reuse them
            # and just call "boss_dnscheck(ip, ip_list) or something like that
            # 'device_type': 'extreme_ers',
            # 'device_type': 'extreme_vsp',
            'device_type': 'extreme_exos',
            # 'device_type': 'extreme',
            'ip': IP,
            'username': '',   # CHANGE THIS AS PER SCHOOL
            'password': '',    # CHANGE THIS AS PER SCHOOL
            'conn_timeout': 10  # this is required for doing larger lists of IP's, increase as needed
        }

        net_connect = ConnectHandler(**Device)
        net_connect.enable()
        print('Connecting to ' + IP)
        print('-' * 79)
        output = net_connect.send_command('show version')   # change this to what you need

        print(output)
        # delay so you don't trip over yourself
        net_connect.select_delay_factor(10)


        print()
        print('-' * 79)
        net_connect.disconnect()


# df.close()
print('Finished diagnostic check.')
# print('Finished Writing')
net_connect.disconnect()

