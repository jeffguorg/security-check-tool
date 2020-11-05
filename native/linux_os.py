from typing import Iterable
from abstract_os import AbstractOS


from xml.etree import ElementTree
from urllib.parse import unquote

import getpass
import os
from datetime import datetime, timedelta

import configparser
import re
import json

import subprocess
import shlex

import pydbus
from gi.repository import GLib
import multiprocessing
        


class LinuxNative(AbstractOS):
    def get_file_access_records(self) -> Iterable[dict]:
        etree = ElementTree.parse(os.path.expanduser("~/.local/share/recently-used.xbel"))
        for bookmark in etree.findall("bookmark"):
            if 'href' in bookmark.attrib:
                href = bookmark.attrib['href']
                if href.startswith("file://"):
                    href = href[7:]
                href = unquote(href)
                yield {
                    "username": getpass.getuser(),
                    "access_time": bookmark.attrib['visited'],
                    "file_path": href,
                    "is_exists": os.path.exists(href)
                }

        for desktop_file in os.listdir(os.path.expanduser("~/.local/share/RecentDocuments")):
            desktop_filepath = os.path.join(os.path.expanduser("~/.local/share/RecentDocuments"), desktop_file)
            config = configparser.ConfigParser()
            config.read(desktop_filepath)

            stat = os.stat(desktop_filepath)
            filepath = None
            for k, v in config["Desktop Entry"].items():
                if k.lower().startswith("url") and v.startswith("file:"):
                    filepath = v.lstrip("file:")

            if filepath is None:
                continue

            filepath = os.path.expanduser(filepath)
            filepath = os.path.expandvars(filepath)

            yield {
                    "username": getpass.getuser(),
                    "access_time": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    "file_path": filepath,
                    "is_exists": os.path.exists(filepath)
            }


    def get_deleted_files_records(self) -> Iterable[dict]:
        for filename in os.listdir(os.path.expanduser("~/.local/share/Trash/files")):
            info_filename = os.path.join(os.path.expanduser("~/.local/share/Trash/info"), filename + ".trashinfo")
            config = configparser.RawConfigParser()
            config.read(info_filename)

            filepath = unquote(config['Trash Info']['Path'])

            yield {
                "filepath": filepath,
                "delete_time": datetime.fromisoformat(config['Trash Info']['DeletionDate']),
            }

    def _read_udev_log(self, filename, value_maps):
        try:
            with open(filename) as fp:
                for line in fp.readlines():
                    record = json.loads(line)

                    result = dict()
                    for k, v in value_maps.items():
                        result.update({
                            k: v(record)
                        })
                    yield result
        except FileNotFoundError:
            pass


    def get_usb_storage_device_using_records(self) -> Iterable[dict]:
        """
        read udev log from /var/log/udev-disks.log
        """
        return self._read_udev_log("/var/log/udev-disks.log", {
            "serial": lambda x: x.get("ID_SERIAL_SHORT"),
            "device_name": lambda x: x.get("ID_MODEL"),
            "last_plugin_time": lambda x: x["time"],
        })

    def get_cell_phone_records(self) -> Iterable[dict]:
        """
        read udev log from /var/log/udev-android.log
        """
        return self._read_udev_log("/var/log/udev-android.log", {
            "serial": lambda x: x.get("ID_SERIAL_SHORT"),
            "manufacture": lambda x: x.get("ID_VENDOR_FROM_DATABASE"),
            "device_name": lambda x: x.get("ID_MODEL"),
            "last_plugin_time": lambda x: datetime.fromisoformat(x["time"]),
        })

    def get_all_usb_device_records(self) -> Iterable[dict]:
        """
        read udev log from /var/log/udev-all.log
        """
        return self._read_udev_log("/var/log/udev-all.log", {
            "serial": lambda x: x.get("ID_SERIAL_SHORT"),
            "manufacture": lambda x: x.get("ID_VENDOR_FROM_DATABASE"),
            "device_name": lambda x: x.get("ID_MODEL"),
            "last_plugin_time": lambda x: datetime.fromisoformat(x["time"]),
        })

    def get_installed_anti_virus_software_records(self) -> Iterable[dict]:
        return filter(lambda record: 'com.qihoo.360safe' == record.get("name"), self.get_installed_anti_virus_software_records())

    def get_installed_software_records(self) -> Iterable[dict]:
        packages = []
        loop = GLib.MainLoop()

        bus = pydbus.SystemBus()
        packagekit = bus.get(".PackageKit")
        transactionPath = packagekit.CreateTransaction()
        transaction = bus.get(".PackageKit", transactionPath)

        def onPackage(info, package, summary):
            package_name, version, _, flags = package.split(";")
            if 'installed' in flags.split(":"):
                packages.append({
                    "name": package_name,
                    "version": version,
                    "description": summary
                })

        def onFinished(*args, **kwargs):
            loop.quit()

        transaction.Package.connect(onPackage)
        transaction.Finished.connect(onFinished)

        transaction.GetPackages(3)


        loop.run()
        
        return packages


    def get_services_records(self) -> Iterable[dict]:
        bus = pydbus.SystemBus()
        systemd = bus.get(".systemd1")
        units = systemd.ListUnits()
        for name, description, load_state, active_state, sub_state, _, object_path, _, _, _ in units:
            if name.endswith(".service"):
                service = bus.get(".systemd1", object_path)
                yield {
                    "name": name,
                    "display_name": description,
                    "status": active_state,
                }

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


