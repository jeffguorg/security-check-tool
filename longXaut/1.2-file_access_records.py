import os
import sys
import win32com.client 
import datetime

def get_file_access_records():

    direction = 'C:\\Users\\Administrator\\AppData\\Roaming\\Microsoft\\Windows\\Recent\\'
    file_lists = os.listdir(direction)
    
    allRecords=[]
    

    for i in range(len(file_lists)):
        record={}
        try:
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(direction+file_lists[i])
            record["username"]=direction.split("\\")[2]
            record["access_time"]=str(datetime.datetime.utcfromtimestamp(int(os.path.getatime(direction+file_lists[i]))))
            record["file_path"]=shortcut.Targetpath
            if os.path.exists(shortcut.Targetpath):
                record["is_exists"]=True  
            else:
                record["is_exists"]=False
            allRecords.append(record)
            yield allRecords
        except:
            # AutomaticDestinations
            pass
        
    # return allRecords

if __name__ == '__main__':

    result=get_file_access_records()
    print(result.__next__())

# os.path.getatime(file) 输出文件访问时间
# os.path.getctime(file) 输出文件的创建时间
# os.path.getmtime(file) 输出文件最近修改时间