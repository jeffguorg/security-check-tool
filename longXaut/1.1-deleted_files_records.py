import winshell as ws

def get_deleted_files_records():

    allRecords=[]
    records=list(ws.recycle_bin())

    if len(records)==0:
        return "Empty Recycle Bin"
    for i in range(len(records)):
        record={}
        # print(dir(records[i]))
        record["filepath"]=str(records[i].original_filename())
        try:
            record["create_time"]=str(records[i].getctime())[:-13]
            record["modify_time"]=str(records[i].getmtime())[:-13]
        except Exception:
            record["modify_time"]=str(records[i].recycle_date())[:-6]
        allRecords.append(record)
        yield allRecords

    # return allRecords

if __name__ == '__main__':

    result=get_deleted_files_records()
    print(result.__next__())
    print(result.__next__())