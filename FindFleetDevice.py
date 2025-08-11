"""
Find Fleet Device tool
- a quick tool to allow the admin to put in a MAC address of a device into it without needing for themselves to connect to the VPN (the connection and disconnection of the VPN should be handled by the script)
- It would be nice for the tool to be able to tell what port it is on, and what VLANs are on that port.
- It will use netmiko python package
- The devices that it will use are a mix of Extreme VSP and Extreme EXOS

Workflow:

User will open executable:

Program will ask user to join VPN or program will start VPN to execute
Program will ask for MAC address
Program will use MAC address as variable to search via the mac address table on the core
Program will identify the second hop to the device, log IP and sysname, and proceed with logging into second hop.
Program will identify port the MAC is learned from on the second hop
Program will then identify what VLAN is untagged and tagged on that port
Program will repeat above until we reach the exact port of the MAC address we are looking for.
Program will log the port, IP, sysname, VLAN, and anything else.
Program will report back findings to programmer

"""



import re
import subprocess
import pyautogui
import subprocess
import time
import getpass
import sys
from netmiko import ConnectHandler

# Creds/Core/VPN
CREDENTIALS = {
    "username": "admin",
    "password": "password",
}

CORE_SWITCH = {
    "device_type": "extreme_exos",
    "host": "10.0.0.1",
    **CREDENTIALS,
}

VPN_COMMAND_CONNECT = "path/to/connect_vpn.sh"
VPN_COMMAND_DISCONNECT = "path/to/disconnect_vpn.sh"

# ============================

def connect_vpn():
    print("[*] Connecting to VPN...")
    cmd = r'"C:\Program Files\Fortinet\FortiClient\FortiClient.exe" connect -s -m vpn -n "MyVPNProfile" -u "vpnuser" -p "vpnpassword"'
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        raise Exception("VPN connection failed")
    print("[+] VPN connected.")

def disconnect_vpn():
    print("[*] Disconnecting VPN...")
    # Some versions of FortiClient close VPN on app exit
    subprocess.run('taskkill /IM FortiClient.exe /F', shell=True)
    print("[-] VPN disconnected.")



def find_mac_on_device(device, mac):
    print(f"[*] Connecting to {device['host']} ({device['device_type']})...")
    conn = ConnectHandler(**device)

    output = conn.send_command(f"show mac-address-table | include {mac}")
    print(f"[>] Output from {device['host']}:\n{output}")

    # Parse port, VLAN, next device. THIS SHIT DOESN'T WORK YET
    match = re.search(r"(?P<vlan>\d+)\s+(?P<mac>[0-9a-f.]+)\s+\S+\s+(?P<port>\S+)", output, re.IGNORECASE)
    if not match:
        print("[!] MAC not found on this device.")
        return None

    port = match.group("port")
    vlan = match.group("vlan")

    # Use LLDP to find next hop if available
    lldp = conn.send_command(f"show lldp neighbors port {port}")
    next_hop_match = re.search(r"(?P<hostname>\S+)\s+(?P<ip>\d+\.\d+\.\d+\.\d+)", lldp)
    next_hop_ip = next_hop_match.group("ip") if next_hop_match else None
    next_hop_sysname = next_hop_match.group("hostname") if next_hop_match else None

    conn.disconnect()

    return {
        "ip": device["host"],
        "sysname": next_hop_sysname or "unknown",
        "port": port,
        "vlan": vlan,
        "next_ip": next_hop_ip,
    }

def recursive_mac_trace(device, mac, visited=None):
    if visited is None:
        visited = []

    result = find_mac_on_device(device, mac)
    if not result or not result["next_ip"] or result["next_ip"] in [v["ip"] for v in visited]:
        visited.append(result)
        return visited

    # Decide next device type dynamically or use known mapping
    next_device = {
        "device_type": "extreme_exos",  # or "extreme_vsp" dynamically
        "host": result["next_ip"],
        **CREDENTIALS
    }

    visited.append(result)
    return recursive_mac_trace(next_device, mac, visited)

def main():
    mac = input("Enter MAC address (e.g., aa:bb:cc:dd:ee:ff): ").strip().lower()

    connect_vpn()

    try:
        results = recursive_mac_trace(CORE_SWITCH, mac)
    finally:
        disconnect_vpn()

    print("\n=== Trace Complete ===")
    for hop in results:
        if hop:
            print(f"{hop['ip']} | {hop['sysname']} | Port: {hop['port']} | VLAN: {hop['vlan']}")
        else:
            print("[!] No further hops found.")

if __name__ == "__main__":
    main()
