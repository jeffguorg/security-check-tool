
from winreg import *
import sys

def get_all_usb_device_records():

    regRoot = ConnectRegistry(None, HKEY_LOCAL_MACHINE)
    subDir = r"SYSTEM\CurrentControlSet\Enum\USBSTOR"
    keyHandle = OpenKey(regRoot, subDir)
    count = QueryInfoKey(keyHandle)[0]
    allRecords=[]

    for i in range(count):
        subKeyName = EnumKey(keyHandle, i)
        subDir_2 = r'%s\%s' % (subDir, subKeyName)
        keyHandle_2 = OpenKey(regRoot, subDir_2)
        num = QueryInfoKey(keyHandle_2)[0]
        for j in range(num):

            subKeyName_2 = EnumKey(keyHandle_2, j)
            result_path = r'%s\%s' % (subDir_2, subKeyName_2)
            keyHandle_3 = OpenKey(regRoot, result_path)
            numKey = QueryInfoKey(keyHandle_3)[1]
            for k in range(numKey):
                record={}
                name, value, type_ = EnumValue(keyHandle_3, k)
                if(('Service' in name) and ('disk'in value)):
                    device_name,type_ = QueryValueEx(keyHandle_3,'FriendlyName')
                    serilas= subKeyName_2
                    manufacture=device_name.split(" ")[0]
                    description,type_ = QueryValueEx(keyHandle_3,'DeviceDesc')

                    with open('C:\\Windows\\inf\\setupapi.dev.log', 'r') as f1:
                        list1 = f1.readlines()
                    le=len(list1)
                    for i in range(0, len(list1)):
                        if serilas[:-2] in list1[i-le] :
                            last_plugin_time=list1[i-le+1][19:-8]
                            break

                    record["device_name"]=device_name
                    record["serilas"]=serilas[:-2]
                    record["manufacture"]=manufacture
                    record["description"]=str(description.split(";")[1:])[1:-1]
                    record["last_plugin_time"]=last_plugin_time
                    allRecords.append(record)
                    yield allRecords
    CloseKey(keyHandle)
    CloseKey(regRoot)

    # return allRecords


if __name__ == '__main__':

    result=get_all_usb_device_records()

    print(result.__next__())
