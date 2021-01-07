from requests import post, get
import re
import base64
import json
import time
import sqlite3
from bs4 import BeautifulSoup
SCKEY = ''
sc_push = ''


def get_sckey():
    global SCKEY
    with open('SCKEY', 'r') as f:
        SCKEY = f.read()


def db_opt(company, notice_time, title):
    conn = sqlite3.connect('src.db')
    c = conn.cursor()
    flag = False
    bytes_title = title.encode("utf-8")
    title = base64.b64encode(bytes_title)
    title=str(title,encoding = "utf8")
    try:
        c.execute('''CREATE TABLE SRC_NOTE
            (company       TEXT      NOT NULL,
            time           TEXT    NOT NULL,
            title          TEXT     NOT NULL
            );''')
        c.execute("INSERT INTO SRC_NOTE (company,time,title) \
                VALUES ('"+company+"', '"+notice_time+"', '"+title+"')")
        flag = True
    except sqlite3.OperationalError:
        # print(e)
        res = c.execute(
            'select time,title from SRC_NOTE where company ="'+company+'"')
        res = res.fetchall()
        for r in res:
            if notice_time in r and title in r:
                flag = False
                break
            else:
                flag = True
        if flag == True:
            c.execute("DELETE FROM SRC_NOTE WHERE company ='" + company \
                + "' and title ='"+title+"'")
            c.execute("INSERT INTO SRC_NOTE (company,time,title) \
                VALUES ('"+company+"', '"+notice_time+"', '"+title+"')")
        if len(res) == 0:
            c.execute("INSERT INTO SRC_NOTE (company,time,title) \
                VALUES ('"+company+"', '"+notice_time+"', '"+title+"')")
            flag = True
    conn.commit()
    conn.close()
    return flag


def sc_send(title, desp=''):
    """
    向server酱推送消息
    """
    global SCKEY
    api = "https://sc.ftqq.com/"+SCKEY+'.send'
    data = {
        "text": title,
        "desp": desp
    }
    req = post(api, data=data)
    req = json.loads(req.text)
    if req['errmsg'] == "success":
        print(title)
    return req


def get_src(url):
    r = get(url)
    res = BeautifulSoup(r.text, 'html.parser')
    return res


def spider_BT():
    """
    爬取补天的专属src
    """
    # post_data = {"s": "", "p": 1, "sort": 1, "token": ''}
    post_data = post('https://www.butian.net/Reward/corps')
    data = json.loads(post_data.text)
    data = data['data']['list']
    new = []
    with open('res', 'r') as f:
        old_res = f.read()
        if old_res != '':
            old_res = json.loads(old_res)
        else:
            old_res = []
    for x in data:
        if x not in old_res:
            # print('\033[0;33m[new]\033[0m '+x['company_name'])
            new.append(x['company_name'])
    if len(new) != 0:
        title = "补天有"+str(len(new))+"个新资产上线了"
        sc_send(title=title, desp=str(new))
        with open('res', 'w') as w:
            w.write(json.dumps(data))


def print_color(company, notice_time, title):
    global sc_push
    grep_list = ['活动', '周岁', '周年', '双倍', '三倍', '端午', '七夕', '双11安全保卫战']
    num = 1
    # flag = True
    flag = db_opt(company, notice_time, title)
    if flag == True:
        sc_push = sc_push+'- '+notice_time+'\t'+title+'\n'
        for i in grep_list:
            if (i in title) and (num == 1) and ('2021' in notice_time or notice_time == '' or '21-' in notice_time or '20-' in notice_time) and (
                    '公示' not in title and '公告' not in title):
                print('\033[0;33m| \033[0m\033[0;31m%s\t%s\033[0m' %
                      (notice_time, title))
                num = num + 1
        if num == 1:
            print('\033[0;33m| \033[0m' + notice_time + '\t' + title)
    return flag


def src_360(number):
    global sc_push
    company = '360'
    num=0
    print(
        '\n\033[0;33m-----------------------360 SRC------------------------\033[0m')
    url = 'https://security.360.cn/News/news?type=-1'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'}
    r = get(url, headers=headers)
    bs = BeautifulSoup(r.text, 'html.parser')
    notice_list = bs.select('.news-content')[0].select('li')
    if number > len(notice_list):
        number = len(notice_list)
    for i in range(0, number):
        time = notice_list[i + 4].select('.new-list-time')[0].text.strip()
        title = notice_list[i + 4].select('a')[0].text
        flag = print_color(company, time, title)
        if flag == True:
            num = num + 1
    if num > 0:
        sc_push = sc_push+'# 360 SRC\n\n'


def src_58(number):
    global sc_push
    company = '58'
    num=0
    print(
        '\n\033[0;33m-----------------------58 SRC------------------------\033[0m')
    url = 'https://security.58.com/notice/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'}
    r = get(url, headers=headers)
    bs = BeautifulSoup(r.text, 'html.parser')
    notice_list = bs.select('.time')
    if number > len(notice_list):
        number = len(notice_list)
    for i in range(0, number):
        time = notice_list[i].text
        title = bs.select('.box')[0].select('a')[i].text
        flag = print_color(company, time, title)
        if flag == True:
            num = num + 1
    if num > 0:
        sc_push = sc_push+'# 58 SRC\n\n'


def alibaba(number):
    global sc_push
    company = 'alibaba'
    num=0
    print(
        '\n\033[0;33m-----------------------阿里SRC------------------------\033[0m')
    url = 'https://security.alibaba.com/api/asrc/pub/announcements/list.json?&page=1'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'}
    r = get(url, headers=headers)
    r_json = json.loads(r.text)
    notice_list = r_json['data']['rows']
    if number > len(notice_list):
        number = len(notice_list)
    for i in range(0, number):
        time = notice_list[i]['lastModify']
        title = notice_list[i]['title']
        # print_color(company, time, title)
        flag = print_color(company, time, title)
        if flag == True:
            num = num + 1
    if num > 0:
        sc_push = sc_push+'# 阿里SRC\n\n'


def ele(number):
    global sc_push
    company = 'ele'
    num=0
    print('\n\033[0;33m-----------------------阿里本地生活SRC----------------\033[0m')
    url = 'https://security.ele.me/api/bulletin/listBulletins?offset=0&limit=5'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'}
    r = get(url, headers=headers)
    r_json = json.loads(r.text)
    notice_list = r_json['modelList']
    if number > len(notice_list):
        number = len(notice_list)
    for i in range(0, number):
        timeStamp = notice_list[i]['createdAt']
        time_format = time.strftime(
            "%Y-%m-%d %H:%M:%S", time.localtime(float(timeStamp / 1000)))
        title = notice_list[i]['title']
        # print_color(company, time_format, title)
        flag = print_color(company, time_format, title)
        if flag == True:
            num = num + 1
    if num > 0:
        sc_push = sc_push+'# 阿里本地生活SRC\n\n'


def iqiyi(number):
    global sc_push
    company = 'iqiyi'
    num=0
    print(
        '\n\033[0;33m-----------------------爱奇艺SRC----------------------\033[0m')
    url = 'https://security.iqiyi.com/api/publish/notice/list?sign=6ce5b4f7ad460b2ae3046422f61f905e4e3ecd03'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'}
    r = get(url, headers=headers)
    r_json = json.loads(r.text)
    notice_list = r_json['data']
    if number > len(notice_list):
        number = len(notice_list)
    for i in range(0, number):
        time = notice_list[i]['create_time_str']
        title = notice_list[i]['title']
        # print_color(company, time, title)
        flag = print_color(company, time, title)
        if flag == True:
            num = num + 1
    if num > 0:
        sc_push = sc_push+'# 爱奇艺SRC\n\n'


def baidu(number):
    global sc_push
    company = 'baidu'
    num=0
    print(
        '\n\033[0;33m-----------------------百度SRC------------------------\033[0m')
    url = 'https://bsrc.baidu.com/v2/api/announcement?type=&page=1&pageSize=10'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'}
    r = get(url, headers=headers)
    r_json = json.loads(r.text)
    notice_list = r_json['retdata']['announcements']
    if number > len(notice_list):
        number = len(notice_list)
    for i in range(0, number):
        time = notice_list[i]['createTime']
        title = notice_list[i]['title']
        # print_color(company, time, title)
        flag = print_color(company, time, title)
        if flag == True:
            num = num + 1
    if num > 0:
        sc_push = sc_push+'# 百度SRC\n\n'


def ke(number):
    global sc_push
    company = 'beike'
    num=0
    print(
        '\n\033[0;33m-----------------------贝壳SRC------------------------\033[0m')
    url = 'https://security.ke.com/api/notices/list'
    headers = {
        'Referer': 'https://security.ke.com/notices',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'
    }
    r = post(url, headers=headers, data={"page": 1})
    r_json = json.loads(r.text)
    notice_list = r_json['data']['list']
    if number > len(notice_list):
        number = len(notice_list)
    for i in range(0, number):
        time = notice_list[i]['createTime']
        title = notice_list[i]['title']
        # print_color(company, time, title)
        flag = print_color(company, time, title)
        if flag == True:
            num = num + 1
    if num > 0:
        sc_push = sc_push+'# 贝壳SRC\n\n'


def bilibili(number):
    global sc_push
    company = 'bilibili'
    num=0
    print(
        '\n\033[0;33m-----------------------哔哩哔哩SRC---------------------\033[0m')
    url = 'https://security.bilibili.com/announcement/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'}
    r = get(url, headers=headers)
    bs = BeautifulSoup(r.text, 'html.parser')
    number = number * 2 + 1
    notice_list = bs.select('td')
    if number > len(notice_list):
        number = len(notice_list)
    for i in range(2, number, 2):
        time = notice_list[i].text.replace('\n', '')
        title = notice_list[i + 1].text.replace('\n', '')
        # print_color(company, time, title)
        flag = print_color(company, time, title)
        if flag == True:
            num = num + 1
    if num > 0:
        sc_push = sc_push+'# 哔哩哔哩SRC\n\n'


def cainiao(number):
    global sc_push
    company = 'cainiao'
    num=0
    print(
        '\n\033[0;33m-----------------------菜鸟SRC------------------------\033[0m')
    url = 'https://sec.cainiao.com/announcement.htm'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'}
    r = get(url, headers=headers)
    bs = BeautifulSoup(r.text, 'html.parser')
    notice_list = bs.select('td')
    if number > len(notice_list):
        number = len(notice_list)
    for i in range(0, number):
        time = notice_list[i].text.split('\n')[0].strip().split('][')[
            0].replace('[', '')
        title = notice_list[i].text.split('\n')[1].strip()
        # print_color(company, time, title)
        flag = print_color(company, time, title)
        if flag == True:
            num = num + 1
    if num > 0:
        sc_push = sc_push+'# 菜鸟SRC\n\n'


def didichuxing(number):
    global sc_push
    company = 'didiCX'
    num=0
    print(
        '\n\033[0;33m-----------------------滴滴出行SRC---------------------\033[0m')
    url = 'http://sec.didichuxing.com/rest/article/list?page=1&size=5&option=0'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'}
    r = get(url, headers=headers)
    r_json = json.loads(r.text)
    notice_list = r_json['data']
    if number > len(notice_list):
        number = len(notice_list)
    for i in range(0, number):
        timeStamp = notice_list[i]['time']
        time_format = time.strftime(
            "%Y-%m-%d %H:%M:%S", time.localtime(float(timeStamp / 1000)))
        title = notice_list[i]['title']
        # print_color(company, time_format, title)
        flag = print_color(company, time_format, title)
        if flag == True:
            num = num + 1
    if num > 0:
        sc_push = sc_push+'# 滴滴出行SRC\n\n'


def duxiaoman(number):
    global sc_push
    company = 'duxiaoman'
    num=0
    print(
        '\n\033[0;33m-----------------------度小满SRC----------------------\033[0m')
    url = 'https://security.duxiaoman.com/index.php?v2api/announcelist'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'}
    r = post(url, headers=headers, data='page=1&type=0&token=null')
    r_json = json.loads(r.text)
    notice_list = r_json['data']['rows']
    if number > len(notice_list):
        number = len(notice_list)
    for i in range(0, number):
        time = notice_list[i]['time']
        title = notice_list[i]['title']
        # print_color(company, time, title)
        flag = print_color(company, time, title)
        if flag == True:
            num = num + 1
    if num > 0:
        sc_push = sc_push+'# 度小满SRC\n\n'


def guazi(number):
    global sc_push
    company = 'guazi'
    num=0
    print(
        '\n\033[0;33m-----------------------瓜子SRC------------------------\033[0m')
    url = 'https://security.guazi.com/gzsrc/notice/queryNoticesList'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'}
    r = post(url, headers=headers, data="pageNo=1")
    r_json = json.loads(r.text)
    notice_list = r_json['data']['list']
    if number > len(notice_list):
        number = len(notice_list)
    for i in range(0, number):
        time = notice_list[i]['publishDate']
        title = notice_list[i]['title']
        # print_color(company, time, title)
        flag = print_color(company, time, title)
        if flag == True:
            num = num + 1
    if num > 0:
        sc_push = sc_push+'# 瓜子SRC\n\n'


def jd(number):
    global sc_push
    company = 'jd'
    num=0
    print(
        '\n\033[0;33m-----------------------京东SRC------------------------\033[0m')
    url = 'https://security.jd.com/notice/list?parent_type=2&child_type=0&offset=0&limit=12'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'}
    r = get(url, headers=headers)
    r_json = json.loads(r.text)
    notice_list = r_json['data']['notices']
    if number > len(notice_list):
        number = len(notice_list)
    for i in range(0, number):
        time = notice_list[i]['CreateTime']
        title = notice_list[i]['Title']
        # print_color(company, time, title)
        flag = print_color(company, time, title)
        if flag == True:
            num = num + 1
    if num > 0:
        sc_push = sc_push+'# 京东SRC\n\n'


def alipay(number):
    global sc_push
    company = 'alipay'
    num=0
    print(
        '\n\033[0;33m-----------------------蚂蚁金服SRC---------------------\033[0m')
    url = 'https://security.alipay.com/sc/afsrc/notice/noticeList.json?_input_charset=utf-8&_output_charset=utf-8'
    headers = {
        'Referer': 'https://security.alipay.com/home.htm',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'
    }
    r = get(url, headers=headers)
    r_json = json.loads(r.text)
    notice_list = r_json['resultAfsrc']['data']
    if number > len(notice_list):
        number = len(notice_list)
    for i in range(0, number):
        time = notice_list[i]['noticeTime']
        title = notice_list[i]['title']
        # print_color(company, time, title)
        flag = print_color(company, time, title)
        if flag == True:
            num = num + 1
    if num > 0:
        sc_push = sc_push+'# 蚂蚁金服SRC\n\n'


def meituan(number):
    global sc_push
    company = 'meituan'
    num=0
    print(
        '\n\033[0;33m-----------------------美团SRC------------------------\033[0m')
    url = 'https://security.meituan.com/api/announce/list?typeId=0&curPage=1&perPage=5'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'}
    r = get(url, headers=headers)
    r_json = json.loads(r.text)
    notice_list = r_json['data']['items']
    if number > len(notice_list):
        number = len(notice_list)
    for i in range(0, number):
        timeStamp = notice_list[i]['createTime']
        time_format = time.strftime(
            "%Y-%m-%d %H:%M:%S", time.localtime(float(timeStamp / 1000)))
        title = notice_list[i]['name']
        # print_color(company, time_format, title)
        flag = print_color(company, time_format, title)
        if flag == True:
            num = num + 1
    if num > 0:
        sc_push = sc_push+'# 美团SRC\n\n'


def immomo(number):
    global sc_push
    company = 'immomo'
    num=0
    print(
        '\n\033[0;33m-----------------------陌陌SRC------------------------\033[0m')
    url = 'https://security.immomo.com/blog'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'}
    r = get(url, headers=headers)
    bs = BeautifulSoup(r.text, 'html.parser')
    notice_list = bs.select('.blog-list')[0].select('span')
    if number > len(notice_list):
        number = len(notice_list)
    for i in range(0, number):
        time = notice_list[i].text
        title = bs.select(
            '.blog-list')[0].select('h2')[i].text.strip().split('\n')[-2].strip()
        # print_color(company, time, title)
        flag = print_color(company, time, title)
        if flag == True:
            num = num + 1
    if num > 0:
        sc_push = sc_push+'# 陌陌SRC\n\n'
        


def oppo(number):
    global sc_push
    company = 'oppo'
    num=0
    print(
        '\n\033[0;33m-----------------------OPPO SRC-----------------------\033[0m')
    url = 'https://security.oppo.com/cn/be/cn/FEnotice/findAllNotice'
    headers = {
        'Host': 'security.oppo.com',
        'Content-Type': 'application/json;charset=UTF-8',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'}
    r = post(url, headers=headers, data='{"pageNum":1,"pageSize":10}')
    r_json = json.loads(r.text)
    notice_list = r_json['AllNotice']['list']
    if number > len(notice_list):
        number = len(notice_list)
    for i in range(0, number):
        time = notice_list[i]['notice_online_time']
        title = notice_list[i]['notice_name']
        # print_color(company, time, title)
        flag = print_color(company, time, title)
        if flag == True:
            num = num + 1
    if num > 0:
        sc_push = sc_push+'# OPPO SRC\n\n'


def pingan(number):
    global sc_push
    company = 'pingan'
    num=0
    print(
        '\n\033[0;33m-----------------------平安SRC------------------------\033[0m')
    url = 'https://security.pingan.com/announcement/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'}
    r = get(url, headers=headers)
    bs = BeautifulSoup(r.text, 'html.parser')
    notice_list = bs.select('#News_List')[0].select('li')
    if number > len(notice_list):
        number = len(notice_list)
    for i in range(0, number):
        time = notice_list[i + 1].select('span')[0].text.strip()
        title = notice_list[i + 1].select('a')[0].text.strip()
        # print_color(company, time, title)
        flag = print_color(company, time, title)
        if flag == True:
            num = num + 1
    if num > 0:
        sc_push = sc_push+'# 平安SRC\n\n'


def shuidihuzhu(number):
    global sc_push
    company = 'shuidihuzhu'
    num=0
    print(
        '\n\033[0;33m-----------------------水滴SRC------------------------\033[0m')
    url = 'https://api.shuidihuzhu.com/api/wide/announce/getAnnouncePageList'
    headers = {
        'Content-Type': 'application/json; charset=UTF-8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'
    }
    r = post(url, headers=headers, data='{"pageNum":1,"pageSize":10}')
    r_json = json.loads(r.text)
    notice_list = r_json['data']['list']
    if number > len(notice_list):
        number = len(notice_list)
    for i in range(0, number):
        timeStamp = notice_list[i]['updateTime']
        time_format = time.strftime(
            "%Y-%m-%d %H:%M:%S", time.localtime(float(timeStamp / 1000)))
        title = notice_list[i]['title']
        # print_color(company, time_format, title)
        flag = print_color(company, time_format, title)
        if flag == True:
            num = num + 1
    if num > 0:
        sc_push = sc_push+'# 水滴SRC\n\n'


def sf_express(number):
    global sc_push
    company = 'sf_express'
    num=0
    print(
        '\n\033[0;33m-----------------------顺丰SRC------------------------\033[0m')
    url = 'http://sfsrc.sf-express.com/notice/getLatestNotices'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'}
    r = post(url, headers=headers, data="limit=10&offset=0")
    r_json = json.loads(r.text)
    notice_list = r_json['rows']
    if number > len(notice_list):
        number = len(notice_list)
    for i in range(0, number):
        timeStamp = notice_list[i]['modifyTime']
        time_format = time.strftime(
            "%Y-%m-%d %H:%M:%S", time.localtime(float(timeStamp / 1000)))
        title = notice_list[i]['noticeTitle']
        # print_color(company, time_format, title)
        flag = print_color(company, time_format, title)
        if flag == True:
            num = num + 1
    if num > 0:
        sc_push = sc_push+'# 顺丰SRC\n\n'


def tencent(number):
    global sc_push
    company = 'tencent'
    num=0
    print(
        '\n\033[0;33m-----------------------腾讯SRC------------------------\033[0m')
    url = 'https://security.tencent.com/index.php/announcement'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'}
    r = get(url, headers=headers)
    bs = BeautifulSoup(r.text, 'html.parser')
    notice_list = bs.select('.section-announcement')[0].select('li')
    if number > len(notice_list):
        number = len(notice_list)
    for i in range(0, number):
        time = notice_list[i].select('span')[0].text
        title = notice_list[i].select('a')[0].text
        # print_color(company, time, title)
        flag = print_color(company, time, title)
        if flag == True:
            num = num + 1
    if num > 0:
        sc_push = sc_push+'# 腾讯SRC\n\n'


def vivo(number):
    global sc_push
    company = 'vivo'
    num=0
    print(
        '\n\033[0;33m-----------------------vivo SRC-----------------------\033[0m')
    url = 'https://security.vivo.com.cn/api/front/notice/noticeListByPage.do'
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'}
    r = post(url, headers=headers,
             data='{"pageNo":1,"pageSize":10,"pageOrder":"","pageSort":""}')
    r_json = json.loads(r.text)
    notice_list = r_json['data']['list']
    if number > len(notice_list):
        number = len(notice_list)
    for i in range(0, number):
        time = notice_list[i]['updateTime']
        title = notice_list[i]['noticeTitle']
        # print_color(company, time, title)
        flag = print_color(company, time, title)
        if flag == True:
            num = num + 1
    if num > 0:
        sc_push = sc_push+'# vivo SRC\n\n'


def src_163(number):
    global sc_push
    company = 'src_163'
    num=0
    print(
        '\n\033[0;33m-----------------------网易SRC------------------------\033[0m')
    url = 'https://aq.163.com/api/p/article/getNoticeList.json'
    headers = {
        'Content-Type': 'application/json;charset=UTF-8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'}
    r = post(url, headers=headers,
             data='{"offset":0,"limit":20,"childCategory":1}')
    r_json = json.loads(r.text)
    notice_list = r_json['data']
    if number > len(notice_list):
        number = len(notice_list)
    for i in range(0, number):
        timeStamp = notice_list[i]['createTime']
        time_format = time.strftime(
            "%Y-%m-%d %H:%M:%S", time.localtime(float(timeStamp / 1000)))
        title = notice_list[i]['title']
        # print_color(company, time_format, title)
        flag = print_color(company, time_format, title)
        if flag == True:
            num = num + 1
    if num > 0:
        sc_push = sc_push+'# 网易SRC\n\n'


def vip(number):
    global sc_push
    company = 'vip'
    num=0
    print(
        '\n\033[0;33m-----------------------唯品会SRC----------------------\033[0m')
    url = 'https://sec.vip.com/notice'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'}
    r = get(url, headers=headers)
    bs = BeautifulSoup(r.text, 'html.parser')
    notice_list = bs.select('.vsrc-news-nameLink')
    if number > len(notice_list):
        number = len(notice_list)
    for i in range(0, number):
        time = bs.select('.news-date')[0].text
        title = notice_list[i].text
        # print_color(company, time, title)
        flag = print_color(company, time, title)
        if flag == True:
            num = num + 1
    if num > 0:
        sc_push = sc_push+'# 唯品会SRC\n\n'


def wifi(number):
    global sc_push
    company = 'wifi'
    num=0
    print(
        '\n\033[0;33m-----------------------WiFi万能钥匙SRC-----------------\033[0m')
    url = 'https://sec.wifi.com/api/announce'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'}
    r = post(url, headers=headers, data='pageNo=0&limit=10')
    r_json = json.loads(r.text)
    notice_list = r_json['data']['result']
    if number > len(notice_list):
        number = len(notice_list)
    for i in range(0, number):
        time = notice_list[i]['publish_time']
        title = notice_list[i]['title']
        # print_color(company, time, title)
        flag = print_color(company, time, title)
        if flag == True:
            num = num + 1
    if num > 0:
        sc_push = sc_push+'# WiFi万能钥匙SRC\n\n'


def zto(number):
    global sc_push
    company = 'zto'
    num=0
    print(
        '\n\033[0;33m-----------------------中通SRC------------------------\033[0m')
    url = 'https://sec.zto.com/api/notice/list'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'}
    r = get(url, headers=headers)
    r_json = json.loads(r.text)
    notice_list = r_json
    if number > len(notice_list):
        number = len(notice_list)
    for i in range(0, number):
        time = notice_list[i]['updated_at'].split('.')[0].replace('T', ' ')
        title = notice_list[i]['title']
        # print_color(company, time, title)
        flag = print_color(company, time, title)
        if flag == True:
            num = num + 1
    if num > 0:
        sc_push = sc_push+'# 中通SRC\n\n'


def bytedance(number):
    global sc_push
    company = 'bytedance'
    num=0
    print(
        '\n\033[0;33m-----------------------字节跳动SRC---------------------\033[0m')
    url = 'https://security.bytedance.com/notice/getNotices/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'}
    r = get(url, headers=headers)
    bs = BeautifulSoup(r.text, 'html.parser')
    notice_list = bs.select('.container')[0].select('li')
    if number > len(notice_list):
        number = len(notice_list)
    for i in range(0, number):
        time = notice_list[i].select('span')[0].text
        title = notice_list[i].select('a')[0].text
        # print_color(company, time, title)
        flag = print_color(company, time, title)
        if flag == True:
            num = num + 1
    if num > 0:
        sc_push = sc_push+'# 字节跳动SRC\n\n'


# def defaute_test(number):
#     company = 'defaute_test'
#     num=0
#     print(
#         '\n\033[0;33m-----------------------defaute_test---------------------\033[0m')
#     url = 'https://defaute_test.com/notice/getNotices/'
#     headers = {
#         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'}
#     r = get(url, headers=headers)
#     bs = BeautifulSoup(r.text, 'html.parser')
#     print_color(company, '', '')
#     # todo


if __name__ == "__main__":
    get_sckey()
    spider_BT()
    number = 3
    src_360(number)  # 360
    src_58(number)  # 58
    alibaba(number)  # 阿里
    ele(number)  # 阿里本地生活
    iqiyi(number)  # 爱奇艺
    baidu(number)  # 百度
    ke(number)  # 贝壳
    bilibili(number)  # 哔哩哔哩
    cainiao(number)  # 菜鸟裹裹
    didichuxing(number)  # 滴滴出行
    duxiaoman(number)  # 度小满
    guazi(number)  # 瓜子
    jd(number)  # 京东
    alipay(number)  # 蚂蚁金服
    meituan(number)  # 美团
    immomo(number)  # 陌陌
    # oppo(number)  # OPPO
    pingan(number)  # 平安
    shuidihuzhu(number)  # 水滴互助
    sf_express(number)  # 顺丰
    tencent(number)  # 腾讯
    vivo(number)  # vivo
    src_163(number)  # 网易
    vip(number)  # 唯品会
    wifi(number)  # WIFI万能钥匙
    zto(number)  # 中通
    bytedance(number)  # 字节跳动
    if sc_push != '':
        sc_send('SRC平台公告更新了！', sc_push)
