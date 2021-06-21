import re
import requests
import time
import execjs
from bs4 import BeautifulSoup
from requests.api import post

url = 'http://www.qiman6.com/'
target_url = 'http://www.qiman6.com/12845/'#奇漫屋漫画页面地址(可修改)
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0'
headers = {'User-Agent':user_agent}
posts = '{"Filename":"/bookchapter/"}'#需要post的值

requests.adapters.DEFAULT_RETRIES = 5 #增加重连次数
r = requests.session()
r.keep_alive = False #关闭多余连接
r = r.get(target_url,headers=headers)
r.encoding = 'utf-8'
#需要加一段请求列表

soup = BeautifulSoup(r.text,features='lxml')
chapter_list = soup.find('div',id="chapter-list1",class_="list").find_all('a')
data = " ".join(map(str,chapter_list))#将chapter_list列表转化为字符串
target_urls = re.findall(r'href="/(.+?)"',data)
url_list = []
for i in target_urls:
    chapter_url = url + i
    url_list.append(chapter_url)

req = requests.session()#请求漫画页面
req.keep_alive = False
req = req.get(url_list[0])#需要多次请求页面
req.encoding = 'utf-8'

c_soup = BeautifulSoup(req.text,features='lxml')#获取漫画地址
c_chapter = c_soup.find_all('script',type='text/javascript')
data = " ".join(map(str,c_chapter))
target = re.findall(r'eval(.+?)\}\)\)',data)
target = "eval" + target[0] + "}))"

def decode_packed_codes(code):#解密js
    def encode_base_n(num, n, table=None):
        FULL_TABLE = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
        if not table:
            table = FULL_TABLE[:n]

        if n > len(table):
            raise ValueError('base %d exceeds table length %d' % (n, len(table)))

        if num == 0:
            return table[0]

        ret = ''
        while num:
            ret = table[num % n] + ret
            num = num // n
        return ret

    pattern = r"}\('(.+)',(\d+),(\d+),'([^']+)'\.split\('\|'\)"
    mobj = re.search(pattern, code)
    obfucasted_code, base, count, symbols = mobj.groups()
    base = int(base)
    count = int(count)
    symbols = symbols.split('|')
    symbol_table = {}

    while count:
        count -= 1
        base_n_count = encode_base_n(count, base)
        symbol_table[base_n_count] = symbols[count] or base_n_count

    return re.sub(
        r'\b(\w+)\b', lambda mobj: symbol_table[mobj.group(0)],
        obfucasted_code)

result = decode_packed_codes(target)
print(result)
