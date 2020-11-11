from sys import argv

from runner import get_all_methods
from runner import run_methods

def run_four_methods(start:int):
    print(f'start is {start}')
    assert 1 <= start <= 4
    all_methods = [
        'get_file_access_records',
        'get_deleted_files_records',
        'get_usb_storage_device_using_records',
        'get_cell_phone_records',

        'get_all_usb_device_records',
        'get_installed_anti_virus_software_records',
        'get_installed_software_records',
        'get_services_records',

        'get_current_network_records',
        'get_system_logs_records',
        'get_power_of_records',
        'get_sharing_settings_records',

        'get_strategy_records',
        'get_users_groups_records',
        'get_hardware_records',
        'get_system_drives_records'
    ]
    start -= 1
    stage_methods = all_methods[start * 4:(start + 1) * 4]
    run_methods(stage_methods)


def main():
    if len(argv) == 2:
        argument = argv[1]
        if argument == 'all':
            run_methods(None)
        elif argument == 'list':
            for i,n in enumerate(get_all_methods()):
                print(i+1, n)
    elif len(argv) > 2:
        if argv[1] == 'call':
            methods = argv[2:]
            if not isinstance(methods, list):
                methods = [methods]
            run_methods(methods)
        elif argv[1] == 'stage':
            start = int(argv[2])
            run_four_methods(start)
    else:
        run_methods(None)


if __name__ == '__main__':
    main()
