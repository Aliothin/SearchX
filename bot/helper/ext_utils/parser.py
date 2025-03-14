import base64
import re
import requests

from lxml import etree
from urllib.parse import urlparse, parse_qs

from bot import UNIFIED_EMAIL, UNIFIED_PASS, GDTOT_CRYPT, HUBDRIVE_CRYPT, KATDRIVE_CRYPT, DRIVEFIRE_CRYPT, SHAREDRIVE_PHPCKS
from bot.helper.ext_utils.exceptions import DDLException

account = {
    'email': UNIFIED_EMAIL, 
    'passwd': UNIFIED_PASS
}

def account_login(client, url, email, password):
    data = {
        'email': email,
        'password': password
    }
    client.post(f'https://{urlparse(url).netloc}/login', data=data)

def gen_payload(data, boundary=f'{"-"*6}_'):
    data_string = ''
    for item in data:
        data_string += f'{boundary}\r\n'
        data_string += f'Content-Disposition: form-data; name="{item}"\r\n\r\n{data[item]}\r\n'
    data_string += f'{boundary}--\r\n'
    return data_string

def parse_infou(data):
    info = re.findall('>(.*?)<\/li>', data)
    info_parsed = {}
    for item in info:
        kv = [s.strip() for s in item.split(':', maxsplit = 1)]
        info_parsed[kv[0].lower()] = kv[1]
    return info_parsed

def unified(url: str) -> str:
    if (UNIFIED_EMAIL or UNIFIED_PASS) is None:
        raise DDLException("UNIFIED_EMAIL and UNIFIED_PASS env vars not provided")
    client = requests.Session()
    client.headers.update({
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36"
    })

    account_login(client, url, account['email'], account['passwd'])

    res = client.get(url)
    key = re.findall('"key",\s+"(.*?)"', res.text)[0]

    ddl_btn = etree.HTML(res.content).xpath("//button[@id='drc']")

    info_parsed = parse_infou(res.text)
    info_parsed['error'] = False
    info_parsed['link_type'] = 'login' # direct/login
    
    headers = {
        "Content-Type": f"multipart/form-data; boundary={'-'*4}_",
    }
    
    data = {
        'type': 1,
        'key': key,
        'action': 'original'
    }
    
    if len(ddl_btn):
        info_parsed['link_type'] = 'direct'
        data['action'] = 'direct'
    
    while data['type'] <= 3:
        try:
            response = client.post(url, data=gen_payload(data), headers=headers).json()
            break
        except: data['type'] += 1
        
    if 'url' in response:
        info_parsed['gdrive_link'] = response['url']
    elif 'error' in response and response['error']:
        info_parsed['error'] = True
        info_parsed['error_message'] = response['message']
    else:
        info_parsed['error'] = True
        info_parsed['error_message'] = 'Something went wrong :('
    
    if urlparse(url).netloc == 'appdrive.in' and not info_parsed['error']:
        flink = info_parsed['gdrive_link']
        return flink
    
    if urlparse(url).netloc == 'driveapp.in' and not info_parsed['error']:
        res = client.get(info_parsed['gdrive_link'])
        drive_link = etree.HTML(res.content).xpath("//a[contains(@class,'btn')]/@href")[0]
        flink = drive_link

    if urlparse(url).netloc == 'drivesharer.in' and not info_parsed['error']:
        res = client.get(info_parsed['gdrive_link'])
        drive_link = etree.HTML(res.content).xpath("//a[contains(@class,'btn btn-primary')]/@href")[0]
        flink = drive_link

    if urlparse(url).netloc == 'drivebit.in' and not info_parsed['error']:
        res = client.get(info_parsed['gdrive_link'])
        drive_link = etree.HTML(res.content).xpath("//a[contains(@class,'btn btn-primary')]/@href")[0]
        flink = drive_link
        
    if urlparse(url).netloc == 'drivelinks.in' and not info_parsed['error']:
        res = client.get(info_parsed['gdrive_link'])
        drive_link = etree.HTML(res.content).xpath("//a[contains(@class,'btn btn-primary')]/@href")[0]
        flink = drive_link


    info_parsed['src_url'] = url
    
    return flink

                           
def parse_info(res):
    info_parsed = {}
    title = re.findall('>(.*?)<\/h4>', res.text)[0]
    info_chunks = re.findall('>(.*?)<\/td>', res.text)
    info_parsed['title'] = title
    for i in range(0, len(info_chunks), 2):
        info_parsed[info_chunks[i]] = info_chunks[i+1]
    return info_parsed

def udrive(url: str) -> str:
    client = requests.Session()
    if 'hubdrive' in url:
        client.cookies.update({'crypt': HUBDRIVE_CRYPT})
    if 'drivehub' in url:
        client.cookies.update({'crypt': HUBDRIVE_CRYPT})
    if 'katdrive' in url:
        client.cookies.update({'crypt': KATDRIVE_CRYPT})
    if 'kolop' in url:
        client.cookies.update({'crypt': KATDRIVE_CRYPT})
    if 'drivefire' in url:
        client.cookies.update({'crypt': DRIVEFIRE_CRYPT})
    res = client.get(url)
    info_parsed = parse_info(res)
    info_parsed['error'] = False
    
    up = urlparse(url)
    req_url = f"{up.scheme}://{up.netloc}/ajax.php?ajax=download"
    
    file_id = url.split('/')[-1]
    
    data = { 'id': file_id }
    
    headers = {
        'x-requested-with': 'XMLHttpRequest'
    }
    
    try:
        res = client.post(req_url, headers=headers, data=data).json()['file']
    except: return {'error': True, 'src_url': url}
    
    if 'drivefire.co' in url:
      return res
    else:
      gd_id = re.findall('gd=(.*)', res, re.DOTALL)[0]
    
    info_parsed['gdrive_url'] = f"https://drive.google.com/open?id={gd_id}"
    info_parsed['src_url'] = url

    return info_parsed['gdrive_url']        
        
def gdtot(url: str) -> str:
    if GDTOT_CRYPT is None:
        raise DDLException("GDTOT_CRYPT env var not provided")
    client = requests.Session()
    client.cookies.update({'crypt': GDTOT_CRYPT})
    res = client.get(url)
    res = client.get(f"https://new.gdtot.nl/dld?id={url.split('/')[-1]}")
    url = re.findall(r'URL=(.*?)"', res.text)[0]
    info = {}
    info['error'] = False
    params = parse_qs(urlparse(url).query)
    if 'gd' not in params or not params['gd'] or params['gd'][0] == 'false':
        info['error'] = True
        if 'msgx' in params:
            info['message'] = params['msgx'][0]
        else:
            info['message'] = 'Invalid link'
    else:
        decoded_id = base64.b64decode(str(params['gd'][0])).decode('utf-8')
        drive_link = f'https://drive.google.com/open?id={decoded_id}'
        info['gdrive_link'] = drive_link
    if not info['error']:
        return info['gdrive_link']
    else:
        raise DDLException(f"{info['message']}")

        
def shareDrive(url,directLogin=True):

    scrapper = requests.Session()

    #retrieving session PHPSESSID
    cook = scrapper.get(url)
    cookies = cook.cookies.get_dict()
    PHPSESSID = cookies['PHPSESSID']

    headers = {
        'authority' : urlparse(url).netloc,
        'Content-Type' : 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin' : f'https://{urlparse(url).netloc}/',
        'referer' : url,
        'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.35',
        'X-Requested-With	' : 'XMLHttpRequest'
    }

    if directLogin==False:
        cookies = {
            'PHPSESSID' : PHPSESSID,
            'PHPCKS' : SHAREDRIVE_PHPCKS
        }

        data = {
            'id' : url.rsplit('/',1)[1],
            'key' : 'original'
        }
    else:
        cookies = {
            'PHPSESSID' : PHPSESSID
        }

        data = {
            'id' : url.rsplit('/',1)[1],
            'key' : 'direct'
        }

    
    resp = scrapper.post(f'https://{urlparse(url).netloc}/post', headers=headers, data=data, cookies=cookies)

    if directLogin==False:
        driveUrl = resp['redirect']
        return driveUrl
    else:
        try:
            toJson = resp.json()
            driveUrl = toJson['redirect']
            return driveUrl
        except:
            if len(SHAREDRIVE_PHPCKS)>0:
                shareDrive(url,directLogin=False)
            else:
                raise DDLException('Direct Login is not there and you have not provided SHAREDRIVE_PHPCKS cookie value!!')        
