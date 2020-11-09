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
import subprocess as sp        
        
import psutil


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
                    "access_time": datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d %H:%M:%S"),
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
                "delete_time": datetime.fromisoformat(config['Trash Info']['DeletionDate']).strftime("%Y-%m-%d %H:%M:%S"),
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
            "last_plugin_time": lambda x: datetime.fromisoformat(x["time"]).strftime("%Y-%m-%d %H:%M:%S"),
        })

    def get_all_usb_device_records(self) -> Iterable[dict]:
        """
        read udev log from /var/log/udev-all.log
        """
        return self._read_udev_log("/var/log/udev-all.log", {
            "serial": lambda x: x.get("ID_SERIAL_SHORT"),
            "manufacture": lambda x: x.get("ID_VENDOR_FROM_DATABASE"),
            "device_name": lambda x: x.get("ID_MODEL"),
            "last_plugin_time": lambda x: datetime.fromisoformat(x["time"]).strftime("%Y-%m-%d %H:%M:%S"),
        })

    def get_installed_anti_virus_software_records(self) -> Iterable[dict]:
        return filter(lambda record: 'com.qihoo.360safe' == record.get("name"), self.get_installed_software_records())

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
        import socket
        return map(lambda conn: filter(lambda conn: conn.family in (socket.AddressFamily.AF_INET, socket.AddressFamily.AF_INET6), dict(
            protocol = "tcp" if conn.type == socket.SOCK_STREAM else "udp" if conn.type == socket.SOCK_DGRAM else "raw",
            local_ip=conn.laddr.ip,
            local_port=conn.laddr.port,
            remote_ip=conn.raddr.ip if conn.raddr else '',
            remote_port=conn.raddr.port if conn.raddr else 0,
            status = conn.status.lower(),
        ), psutil.net_connections()))

    def get_system_logs_records(self) -> Iterable[dict]:
        pass

    def get_power_off_records(self, wtmp_path="/var/log/wtmp") -> Iterable[dict]:
        import utmp
        with open(wtmp_path, "rb") as fp:
            for record in utmp.read(fp.read()):
                if record.user == 'reboot':
                    yield dict(
                        time=datetime.fromtimestamp(record.time).strftime("%Y-%m-%d %H:%M:%S"),
                        event= "power on",
                    )
                elif record.user == 'shutdown':
                    yield dict(
                        time=datetime.fromtimestamp(record.time).strftime("%Y-%m-%d %H:%M:%S"),
                        event= "power off",
                    )

    def get_sharing_settings_records(self) -> Iterable[dict]:
        pass

    def get_strategy_records(self) -> Iterable[dict]:
        pass

    def get_users_groups_records(self) -> Iterable[dict]:
        import grp
        return map(lambda g: dict(
            group_id: g.gr_gid,
            group_name: g.gr_name,
            members: g.gr_mem,
        ), grp.getgrall())


    def get_hardware_records(self) -> Iterable[dict]:
        pass

    def get_system_drivers_records(self, active_only=True) -> Iterable[dict]:
        import kmodpy

        kmod = kmodpy.Kmod()
        for modname, _ in (kmod.loaded() if active_only else kmod.list()):
            modinfo = dict((k.decode(), v.decode())for k, v in kmod.modinfo(modname))
            yield dict(
                name=modname,
                description=modinfo.get("description", "")
            )


