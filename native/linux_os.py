from typing import Iterable
from abstract_os import AbstractOS


class LinuxNative(AbstractOS):
    def get_file_access_records(self) -> Iterable[dict]:
        pass

    def get_deleted_files_records(self) -> Iterable[dict]:
        pass

    def get_usb_storage_device_using_records(self) -> Iterable[dict]:
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
        res = os.popen(
            "cat /etc/lightdm/lightdm.conf | grep ^autologin").readlines()
        res1 = "".join(res).split("=")

        item = {"user" : "" , "is_auto_login" : False }

        if len(res) == 0 :
            yield item
        elif res1[-1] == "\n":
            yield item
        else:
            yield {
                "user": res1[-1][:-1],
                "is_auto_login": True,
            }


    def get_users_groups_records(self) -> Iterable[dict]:
        res = os.popen("cat /etc/group").readlines()

        for i in range(len(res)):
            group = res[i].split(":")
            yield{
                "group_name": group[0],
                "members": group[-1][:-1].split(",")
            }


    def get_hardware_records(self) -> Iterable[dict]:
        pass

    def get_system_drives_records(self) -> Iterable[dict]:
        path_list = []
        def get_all(path):
            paths = os.listdir(path)  # 列出指定路径下的所有目录和文件
            for i in paths:
                com_path = os.path.join(path, i)
                if os.path.isdir(com_path):
                    get_all(com_path)  # 如果该路径是目录，则调用自身方法
                elif os.path.isfile(com_path):
                    path_list.append(com_path)  # 如果该路径是文件，则追加到path_list中
            return path_list

        path_list = get_all(path=r'/lib/modules/4.19.0-6-amd64/kernel/drivers')

        for i in range(len(path_list)):

            yield {
                "name": path_list[i].split("/")[-1][:-3],
                "install_time": str(datetime.datetime.fromtimestamp(os.stat(path_list[i]).st_ctime))[0:19]
            }