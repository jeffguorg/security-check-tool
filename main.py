from sys import platform as os_name
from sys import argv
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

def get_all_methods():
    # https://stackoverflow.com/questions/34439/finding-what-methods-a-python-object-has/20100900
    instance = NativeOS().instance()
    return  [ method_name for method_name in dir(instance)
                   if callable(getattr(instance, method_name)) and not method_name.startswith('__')]


def run_methods(selected_methods:list):
    obj_methods = get_all_methods()
    if selected_methods is None:
        selected_methods = obj_methods
    total_count = len(selected_methods)
    implement_methods = []
    failed_methods = []
    for method_name in selected_methods:
        assert (method_name in obj_methods)
        func = getattr(NativeOS().instance(), method_name)
        try:
            generator = func()
            for i in generator:
                print(i)
            implement_methods.append(method_name)
        except Exception as ex:
            print(f'failed call {method_name}', ex)
    if len(failed_methods) > 0:
        print("-----------------FAILED----------------")
        for i in failed_methods:
            print(i)
    implement_count = len(implement_methods)
    print("-------------------OK------------------")
    for i in implement_methods:
        print(i)
    print(f"{implement_count} of {total_count} has implemented {implement_count * 100 / total_count}%")


if __name__ == '__main__':
    if len(argv) == 2:
        argument = argv[1]
        if argument == 'all':
            run_methods(None)
        elif argument == 'list':
            for i,n in enumerate(get_all_methods()):
                print(i+1, n)
        elif argument.isdigit():
            start = int(argument) - 1
            print(f'start is {start}')
            assert 0 <= start <= 3
            methods = get_all_methods()[start*4:(start+1)*4]
            run_methods(methods)
    elif len(argv) > 2:
        run_methods(argv[1:])
    else:
        run_methods([
            'get_file_access_records',
            'get_deleted_files_records',
            'get_usb_storage_device_using_records',
            'get_cell_phone_records'
        ])