from sys import argv

from runner import get_all_methods
from runner import run_methods


def main():
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
    elif len(argv) > 2 and argv[1] == 'call':
        methods = argv[2:]
        if not isinstance(methods, list):
            methods = [methods]
        run_methods(methods)
    else:
        run_methods([
            'get_file_access_records',
            'get_deleted_files_records',
            'get_usb_storage_device_using_records',
            'get_cell_phone_records',

            'get_all_usb_device_records',
            'get_installed_anti_virus_software_records',
            'get_installed_software_records',
            'get_services_records'
        ])


if __name__ == '__main__':
    main()
