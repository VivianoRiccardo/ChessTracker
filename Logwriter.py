import os
import datetime

def delete_file_if_exists(file_path):
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except:
            return

def save_log(filename, message):
    try:
        date = datetime.datetime.now()
        d = datetime.timedelta(days = 10)
        past_date = date - d
        str_date = str(date)
        str_date = str_date[:str_date.find(' ')]
        str_past_date = str(past_date)
        str_past_date = str_past_date[:str_past_date.find(' ')]
        past_file = filename.format(str_past_date)
        delete_file_if_exists(past_file)
        filename = filename.format(str_date)
        f = open(filename,'a+')
        f.write('['+str(date)+'] MESSAGE: '+str(message))
        f.close()
    except:
        return
