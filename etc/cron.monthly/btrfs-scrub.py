#!/bin/python3

import json
import subprocess

# Get a list of disks and their filetype
devices = json.loads(subprocess.check_output(["lsblk", "-n", "-i", "--json",
                                                           "-o", "NAME,FSTYPE,MOUNTPOINT"]).decode())

devices = devices["blockdevices"] # select the json area "blockdevices"

dev_list = tuple(devices) # change the devices list into a tuple
scrub_list = [] # this is the list of devices we want to run btrfs_scrub on

for device in dev_list:  # we will iterate through the dev list and add devices to the scrub_list
    if device['mountpoint'] == '/mnt' or device['mountpoint'] == '/media': 
        # if the device is in these locations, it is probably removable and we don't want to include it
        continue
    elif device == []:  # if the device is empty, we skip
        continue
    elif 'children' in device:
        for child in device['children']:
            if "fstype" not in child.keys():  # if it doesn't have a label, skip
                continue
            elif not child['fstype'] == 'btrfs':  # if it is a btrfs partition, add it
                scrub_list.append("/dev" + child['name'])
    else: # this is the case wher the device does not have children
        if device['fstype'] == 'btrfs':
            scrub_list.append("/dev" + child['name'])

final_command = ""

for device_name in scrub_list:
    final_command += device_name

subprocess.check_output("btrfs scrub start " + final_command)