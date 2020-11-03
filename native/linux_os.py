from typing import Iterable
from abstract_os import AbstractOS

from xml.etree import ElementTree
import os
from datetime import datetime, timedelta
import getpass
import configparser
import re

import subprocess
import shlex


class LinuxNative(AbstractOS):
    def get_file_access_records(self) -> Iterable[dict]:
        etree = ElementTree.parse(os.path.expanduser("~/.local/share/recently-used.xbel"))
        for bookmark in etree.findall("bookmark"):
            if 'href' in bookmark.attrib:
                href = bookmark.attrib['href']
                yield {
                    "username": getpass.getuser(),
                    "access_time": bookmark.attrib['visited'],
                    "file_path": href,
                    "is_exists": os.path.exists(href)
                }

    def get_deleted_files_records(self) -> Iterable[dict]:
        for filename in os.listdir(os.path.expanduser("~/.local/share/Trash/files")):
            info_filename = os.path.join(os.path.expanduser("~/.local/share/Trash/files"), filename + ".trashinfo")
            config = configparser.ConfigParser()
            config.read(info_filename)

            stat = os.stat(filename)

            yield {
                "filepath": config['Trash Info']['Path'],
                "delete_time": datetime.fromisoformat(config['Trash Info']['DeletionDate']),
                "create_time": datetime.fromtimestamp(stat.st_ctime),
                "modify_time": datetime.fromtimestamp(stat.st_mtime)
            }

    def get_usb_storage_device_using_records(self) -> Iterable[dict]:
        """
        it is tricky to get storage devices log. a common pattern for usb storage device is:
            [  966.555258] usb 1-4: USB disconnect, device number 7
            [  971.323076] usb 1-4: new high-speed USB device number 8 using xhci_hcd
            [  971.478838] usb 1-4: New USB device found, idVendor=04e8, idProduct=61f5, bcdDevice= 1.00
            [  971.478845] usb 1-4: New USB device strings: Mfr=2, Product=3, SerialNumber=1
            [  971.478849] usb 1-4: Product: Portable SSD T5
            [  971.478852] usb 1-4: Manufacturer: Samsung
            [  971.478854] usb 1-4: SerialNumber: 1234567DC8C1
            [  971.483839] scsi host2: uas
            [  971.485029] scsi 2:0:0:0: Direct-Access     Samsung  Portable SSD T5  0    PQ: 0 ANSI: 6
            [  971.486953] sd 2:0:0:0: Attached scsi generic sg1 type 0

        WARN: kernel buffer can be cleared so messages can be lost


        a more proper way to do this, is to configure udev to log usb storage device
        """
        # get uptime
        with open("/proc/uptime") as fp:
            uptime_content = fp.read()
        uptime = float(uptime_content.split()[0])


        dmesg = subprocess.run(shlex.split("dmesg"), stdout=subprocess.PIPE)
        devices = dict()
        last_occurances = dict()

        for line in dmesg.stdout.decode().splitlines():
            match = re.match("\\[ *(?P<time>[0-9.]+)\\].*", line)
            if not match:
                continue
            msg_time,  = match.groups()
            current_time = datetime.now() - timedelta(seconds=uptime - float(msg_time))

            match_usb = re.match("\\[ *(?P<time>[0-9.]+)\\] usb *(?P<device>[^:]*): *(?P<message>.*)", line)
            match_scsi = re.match("\\[ *(?P<time>[0-9.]+)\\] scsi.*", line)
            match_sd = re.match("\\[ *(?P<time>[0-9.]+)\\] sd .*", line)

            if match_usb:
                (msg_time, msg_device, msg_content) = match_usb.groups()
                last_occurances[msg_device] = datetime.now() - timedelta(seconds=uptime - float(msg_time))
                if re.match("[nN]ew.*", msg_content):
                    devices[msg_device] = dict(Time=current_time)
                if msg_device in devices:
                    if '=' not in msg_content and ':' in msg_content:
                        k, v = msg_content.split(":")
                        devices[msg_device][k.strip()] = v.strip()
            else:
                devices_to_remove_from_occurance = set()
                for device, last_occurance in last_occurances.items():
                    if device not in devices:
                        continue
                    if (current_time - last_occurance).seconds > 3 and device in devices:
                        devices_to_remove_from_occurance.add(device)
                        continue
                    else:
                        if match_scsi:
                            devices[device]["Possibility"] = devices[device].get("Possibility", 0) + 0.4
                        elif match_sd:
                            devices[device]["Possibility"] = devices[device].get("Possibility", 0) + 0.4
    
    
                for device_id in devices_to_remove_from_occurance:
                    device = devices[device_id]
                    yield {
                        "serial": device["SerialNumber"],
                        "manufacture": device['Manufacturer'],
                        "device_name": device['Product'],
                        "last_plugin_time": device['Time'],
                    }
                    devices.pop(device_id)
                    last_occurances.pop(device_id)


    def get_cell_phone_records(self) -> Iterable[dict]:
        pass

    def get_all_usb_device_records(self) -> Iterable[dict]:
        # get uptime
        with open("/proc/uptime") as fp:
            uptime_content = fp.read()
        uptime = float(uptime_content.split()[0])


        dmesg = subprocess.run(shlex.split("bash -c \"dmesg | grep 'usb [[:digit:]]-[[:digit:]]'\""), stdout=subprocess.PIPE)
        devices = dict()
        for line in dmesg.stdout.decode().splitlines():
            match = re.match("\\[ *(?P<time>[0-9.]+)\\] *(?P<device>[^:]*): *(?P<message>.*)", line)
            if match:
                (msg_time, msg_device, msg_content) = match.groups()
                if msg_device not in devices:
                    devices[msg_device] = dict(
                        Time = msg_time
                    )
                if ':' not in msg_content and '=' in msg_content:
                    k, v = msg_content.split("=")
                    devices[msg_device][k.strip()] = v.strip()
                    

        for device in devices.values():
            yield {
                "serial": device["SerialNumber"],
                "manufacture": device['Manufacturer'],
                "device_name": device['Product'],
                "last_plugin_time": datetime.now() - timedelta(seconds=uptime - device['Time'])
            }

    def get_installed_anti_virus_software_records(self) -> Iterable[dict]:
        pass

    def get_installed_software_records(self) -> Iterable[dict]:
        pass

    def get_services_records(self) -> Iterable[dict]:
        pass

    def get_current_network_records(self) -> Iterable[dict]:
        pass

    def get_system_logs_records(self) -> Iterable[dict]:
        pass

    def get_power_of_records(self) -> Iterable[dict]:
        pass

    def get_sharing_settings_records(self) -> Iterable[dict]:
        pass

    def get_strategy_records(self) -> Iterable[dict]:
        pass

    def get_users_groups_records(self) -> Iterable[dict]:
        pass

    def get_hardware_records(self) -> Iterable[dict]:
        pass

    def get_system_drives_records(self) -> Iterable[dict]:
        pass
