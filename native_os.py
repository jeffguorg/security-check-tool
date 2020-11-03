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


def run_all():
    # https://stackoverflow.com/questions/34439/finding-what-methods-a-python-object-has/20100900
    instance = NativeOS().instance()
    obj_methods = [ method_name for method_name in dir(instance)
                   if callable(getattr(instance, method_name)) and not method_name.startswith('__')]
    total_count = len(obj_methods)
    implement_count = 0
    for name in obj_methods:
        func = getattr(instance, name)
        generator = func()
        if generator is None:
            print(f"not implemented {name}")
        else:
            print(f'CALL {name}')
            implement_count += 1
            for i in generator:
                print(i)
    print(f"{implement_count} of {total_count} has implemented {implement_count*100/total_count}%")

if __name__ == '__main__':
    run_all()
