import re
import threading

SIZE_UNITS = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']

def get_readable_file_size(size_in_bytes) -> str:
    if size_in_bytes is None:
        return '0B'
    index = 0
    while size_in_bytes >= 1024:
        size_in_bytes /= 1024
        index += 1
    try:
        return f'{round(size_in_bytes, 2)}{SIZE_UNITS[index]}'
    except IndexError:
        return 'File too large'

def is_gdrive_link(url: str):
    return "drive.google.com" in url

def is_appdrive_link(url: str):
    url = re.match(r'https?://(appdrive)\.\S+', url)
    return bool(url)

def is_driveapp_link(url: str):
    url = re.match(r'https?://(driveapp)\.\S+', url)
    return bool(url)

def is_gdflix_link(url: str):
    url = re.match(r'https?://(gdflix)\.\S+', url)
    return bool(url)

def is_drivelinks_link(url: str):
    url = re.match(r'https?://(drivelinks)\.\S+', url)
    return bool(url)

def is_drivebit_link(url: str):
    url = re.match(r'https?://(drivebit)\.\S+', url)
    return bool(url)

def is_drivesharer_link(url: str):
    url = re.match(r'https?://(drivesharer)\.\S+', url)
    return bool(url)

def is_gdtot_link(url: str):
    url = re.match(r'https?://.+\.gdtot\.\S+', url)
    return bool(url)

def is_hubdrive_link(url: str):
    url = re.match(r'https?://(hubdrive)\.\S+', url)
    return bool(url)

def is_drivehub_link(url: str):
    url = re.match(r'https?://(drivehub)\.\S+', url)
    return bool(url)

def is_katdrive_link(url: str):
    url = re.match(r'https?://(katdrive)\.\S+', url)
    return bool(url)

def is_kolop_link(url: str):
    url = re.match(r'https?://(kolop)\.\S+', url)
    return bool(url)

def is_drivefire_link(url: str):
    url = re.match(r'https?://(drivefire)\.\S+', url)
    return bool(url)

def is_sharedrive_link(url: str):
    url = re.match(r'https?://(sharedrive)\.\S+', url)
    return bool(url)

def is_adfly_link(url: str):
    url = re.match(r'https?://(adf)\.ly/\S+', url)
    return bool(url)

def is_gplinks_link(url: str):
    url = re.match(r'https?://(gplinks)\.\S+', url)
    return bool(url)

def is_rocklinks_link(url: str):
    if 'spidermods.in' in url:
        return bool(url)
    if 'rocklink.in' in url:
        return bool(url)
    if 'rocklinks.net' in url:
        return bool(url)
    
def is_droplink_link(url: str):
    url = re.match(r'https?://(droplink)\.\S+', url)
    return bool(url)
    
def new_thread(fn):
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=fn, args=args, kwargs=kwargs)
        thread.start()
        return thread
    return wrapper
