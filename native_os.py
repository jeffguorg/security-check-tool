from sys import platform as os_name

from abstract_os import AbstractOS


class NativeOS(AbstractOS):
    def __init__(self):
        self._instance = None

    def instance(self) -> AbstractOS:
        if self._instance is not None:
            return self._instance
        if os_name == 'win32':
            from native.windows_os import WindowsNative
            self._instance = WindowsNative()
        elif os_name == 'linux':
            from native.linux_os import LinuxNative
            self._instance = LinuxNative()
        elif os_name == 'darwin':
            from native.mac_os import MacNative
            self._instance = MacNative()
        else:
            raise NotImplementedError(os_name)
        return self._instance


if __name__ == '__main__':
    # s = NativeOS.instance().list_removable_drives()
    for i in NativeOS().instance().get_usb_plugin_records():
        print(i)
