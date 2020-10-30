from abstract_os import AbstractOS


class WindowsNative(AbstractOS):
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