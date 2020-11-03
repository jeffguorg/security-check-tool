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
        pass

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
                    devices[k.strip()] = v.strip()
                    

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
