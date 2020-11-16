from typing import Iterable
from abstract_os import AbstractOS
import os
import datetime


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
import shutil

import multiprocessing
import subprocess as sp        
        
import psutil

RECENTUSED_XML_PATH=os.path.expanduser("~/.local/share/recently-used.xbel")
RECENTDOC_DIR_PATH=os.path.expanduser("~/.local/share/RecentDocuments")

TRASH_DIR_PATH=os.path.expanduser("~/.local/share/Trash")
TRASHFILE_DIR_PATH=os.path.join(TRASH_DIR_PATH, "file")
TRASHINFO_DIR_PATH=os.path.join(TRASH_DIR_PATH, "info")

class LinuxNative(AbstractOS):
    def get_file_access_records(self) -> Iterable[dict]:
        if os.path.isfile(RECENTUSED_XML_PATH):
            etree = ElementTree.parse(RECENTUSED_XML_PATH)
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
        elif os.path.isdir(RECENTDOC_DIR_PATH):
            for desktop_file in os.listdir(RECENTDOC_DIR_PATH):
                desktop_filepath = os.path.join(RECENTDOC_DIR_PATH, desktop_file)
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
        if os.path.isdir(TRASHFILE_DIR_PATH) and os.path.isdir(TRASHINFO_DIR_PATH):
            for filename in os.listdir(TRASHFILE_DIR_PATH):
                info_filename = os.path.join(TRASHINFO_DIR_PATH, filename + ".trashinfo")
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

    def get_installed_software_records(self, sep="####SEP####") -> Iterable[dict]:
        import shutil
        dpkg = shutil.which("dpkg")
        rpm = shutil.which("rpm")

        proc = None
        if dpkg is not None:
            proc = sp.run(shlex.split("dpkg-query -W -f '" + sep + "\\n${Package}|${Version}\\n${Description}\\n'"), stdout=sp.PIPE, stderr=sp.PIPE)
        if rpm is not None:
            proc = sp.run(shlex.split("rpm -qa --queryformat '" + sep + "\\n%{name}|%{version}-%{release}\\n%{description}\\n'"), stdout=sp.PIPE, stderr=sp.PIPE)
        
        if proc is not None:
            stdout = proc.stdout.decode()
            packages = filter(lambda x: x.strip(), stdout.split(sep))
            for package in packages:
                lines = list(filter(None, (package.strip() for package in package.splitlines())))
                name, version = lines[0].strip().split("|")
                description = "\n".join(lines[1:])

                yield {
                    "name": name,
                    "version": version,
                    "description": description,
                }

    def get_services_records(self) -> Iterable[dict]:
        for service_type in ("system", "user"):
            proc = sp.run(shlex.split("systemctl list-unit-files --type service --no-legend --no-pager --" + service_type), stdout=sp.PIPE)
            service_units = dict(line.strip().split() for line in proc.stdout.decode().splitlines())

            proc = sp.run(shlex.split("systemctl list-units --type service --no-legend --no-pager --all"), stdout=sp.PIPE, stderr=sp.PIPE)
            stdout = proc.stdout.decode()
            services = stdout.splitlines(False)
            for service in map(lambda s: s.strip(), services):
                name, loaded, active, running, description = service.split(maxsplit=4)
                if name not in service_units:
                    continue

                proc = sp.run(["systemctl", "show", "--property", "MainPID", "--value", name], stdout=sp.PIPE, stderr=sp.PIPE)
                pid = int(proc.stdout)
            
                yield {
                    "name": name,
                    "display_name": description,
                    "start_type": "auto" if service_units[name] == "enabled" else "disabled" if service_units[name] == "masked" else "manual",
                    "process_id": pid,
                    "is_system_service": service_type == "system",
                    "status": running,
                }

    def get_current_network_records(self) -> Iterable[dict]:
        import socket
        return map(lambda conn: dict(
            protocol = "tcp" if conn.type == socket.SOCK_STREAM else "udp" if conn.type == socket.SOCK_DGRAM else "raw",
            local_ip=conn.laddr.ip,
            local_port=conn.laddr.port,
            remote_ip=conn.raddr.ip if conn.raddr else '',
            remote_port=conn.raddr.port if conn.raddr else 0,
            status = conn.status.lower(),
        ), filter(lambda conn: conn.family in (socket.AddressFamily.AF_INET, socket.AddressFamily.AF_INET6), psutil.net_connections()))

    def get_system_logs_records(self) -> Iterable[dict]:
        pass

    def get_power_off_records(self, wtmp_path="/var/log/wtmp") -> Iterable[dict]:
        import utmp
        with open(wtmp_path, "rb") as fp:
            for record in utmp.read(fp.read()):
                if record.user == 'reboot':
                    yield dict(
                        time=record.time.strftime("%Y-%m-%d %H:%M:%S"),
                        event="power on",
                    )
                elif record.user == 'shutdown':
                    yield dict(
                        time=record.time.strftime("%Y-%m-%d %H:%M:%S"),
                        event="power off",
                    )

    def get_sharing_settings_records(self) -> Iterable[dict]:
        pass

    def get_strategy_records(self) -> Iterable[dict]:
        res = os.popen(
            "cat /etc/lightdm/lightdm.conf | grep ^autologin").readlines()
        res1 = "".join(res).split("=")
        item = {
            "user": "",
            "is_auto_login": False,
        }
        if len(res) == 0 or res1[-1] == "\n":
            yield item
        elif res1[-1] == "\n":
            yield item
        else:
            yield {
                "user": res1[-1][:-1],
                "is_auto_login": True,
            }

    def get_users_groups_records(self) -> Iterable[dict]:
        import grp
        return map(lambda g: dict(
            group_id= g.gr_gid,
            group_name= g.gr_name,
            members= g.gr_mem,
        ), grp.getgrall())


    def get_hardware_records(self) -> Iterable[dict]:
        with open('/proc/cpuinfo') as fd:
            for line in fd:
                if line.startswith('model name'):
                    cpu_model = line.split(':')[1].strip().split()
                    cpu_model = cpu_model[0] + ' ' + \
                        cpu_model[2] + ' ' + cpu_model[-1]
                    yield {'kind': 'CPU 处理器', 'info': cpu_model.strip()}

        with os.popen('sudo  fdisk -l') as fd:
            for line in fd:
                if line.startswith('Disk /dev'):
                    cpu_model1 = line.split(':')[-1][:-1]
                elif line.startswith('Disk model: '):
                    cpu_model = line.split(':')[-1][:-1]+cpu_model1
                    yield {'kind': "硬盘", 'info': cpu_model.strip()}

        with os.popen('sudo dmidecode -t 2') as fd:
            for line in fd:
                line = line.strip()
                if line.startswith('Manufacturer'):
                    cpu_model1 = line.split(':')[-1][:-1]
                elif line.startswith('Product Name'):
                    cpu_model = line.split(':')[-1][:-1]+cpu_model1
                    yield {'kind': "主板", 'info': cpu_model.strip()}

        with os.popen('/sbin/ifconfig') as fd:
            for line in fd:

                if line.split(" ")[0]!="":
                    name=line.split(":")[0]
                if 'ether' in line:
                    yield{
                        "name":name,
                        "address":line.split()[1]
                    }

    def get_system_drivers_records(self, active_only=True) -> Iterable[dict]:
        import kmodpy

        kmod = kmodpy.Kmod()
        for modname, _ in (kmod.loaded() if active_only else kmod.list()):
            modinfo = dict((k.decode(), v.decode())for k, v in kmod.modinfo(modname))
            yield dict(
                name=modname,
                description=modinfo.get("description", "")
            )

