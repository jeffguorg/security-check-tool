from typing import Iterable

from abstract_os import AbstractOS


class WindowsNative(AbstractOS):
    def get_file_access_records(self) -> Iterable[dict]:
        pass

    def get_deleted_files_records(self) -> Iterable[dict]:
        pass

    def get_cell_phone_records(self) -> Iterable[dict]:
        pass

    def get_all_usb_device_records(self) -> Iterable[dict]:
        pass

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

    def get_usb_storage_device_using_records(self):
        yield {
            "device_name": "KingSoft USB 2.0",
            "serilas": "241300000293",
            "manufacture": "Samsung",
            "description": "USB 2.0 Flash Driveß",
            "last_plugin_time": "2020-10-22 08:10"
        }

        yield {
            "device_name": "Toshiba USB 3.0",
            "serilas": "241300001293",
            "manufacture": "japen toshiba",
            "description": "USB 3.0 Flash",
            "last_plugin_time": "2020-10-29 19:56"
        }