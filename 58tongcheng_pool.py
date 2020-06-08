import base64
import requests
import re
from urllib.request import urlretrieve
from fontTools.ttLib import TTFont, BytesIO
import time
from xml.dom.minidom import parse
import xml.dom.minidom
from bs4 import BeautifulSoup
import MysqlTool
import warnings

warnings.filterwarnings("ignore")


ini_arr = [
    {'value':'无','key':''},
    {'value':'经','key':''},
    {'value':'验','key':''},
    {'value':'应','key':''},
    {'value':'届','key':''},
    {'value':'生','key':''},
    {'value':'以','key':''},
    {'value':'下','key':''},
    {'value':'高','key':''},
    {'value':'中','key':''},
    {'value':'专','key':''},
    {'value':'技','key':''},
    {'value':'校','key':''},
    {'value':'大','key':''},
    {'value':'本','key':''},
    {'value':'科','key':''},
    {'value':'硕','key':''},
    {'value':'士','key':''},
    {'value':'博','key':''},
    {'value':'E','key':''},
    {'value':'M','key':''},
    {'value':'B','key':''},
    {'value':'A','key':''},
    {'value':'0','key':''},
    {'value':'1','key':''},
    {'value':'2','key':''},
    {'value':'3','key':''},
    {'value':'4','key':''},
    {'value':'5','key':''},
    {'value':'6','key':''},
    {'value':'7','key':''},
    {'value':'8','key':''},
    {'value':'9','key':''},
    {'value':'女','key':''},
    {'value':'士','key':''},
    {'value':'男','key':''},
    {'value':'生','key':''},
]
char_map = {
    '-784,0': '无',
    '0,-144': '经',
    '46,550': '验',
    '-146,-78': '应',
    '-582,0': '届',
    '-928,0': '生',
    '-164,0': '以',
    '-1944,0': '下',
    '-1298,0': '高',
    '-770,0': '中',
    '-265,118': '专',
    '0,-132': '技',
    '-210,-358': '校',
    '-825,-367': '大',
    '52,52': '本',
    '-228,-306': '科',
    '-230,-390': '硕',
    '-746,0': '士',
    '0,-110': '博',
    '833,0': 'E',
    '0,-1026': 'M',
    '0,-1549': 'B',
    '221,0': 'A',
    '0,-410': '0',
    '0,-1325': '1',
    '0,-125': '2',
    '-159,123': '3',
    '0,1023': '4',
    '0,227': '5',
    '121,-62': '6',
    '244,426': '7',
    '0,-134': '8',
    '-128,74': '9',
    '110,150': '女',
    '-746,0': '士',
    '-1588,0': '男',
    '-928,0': '生'
}

# 打开网页
def open_page(page_url):
    headers = {
        'accept-language':'zh-CN,zh;q=0.9',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
    }
    response = requests.get(page_url, headers=headers)
    return response


# 获得base64字符串并生成xml
def creat_xml(base64_string):
    bin_data = base64.decodebytes(base64_string.encode())
    with open('./58tongcheng_pool.woff','wb') as f:
        f.write(bin_data)
    font = TTFont(BytesIO(bin_data))
    font.saveXML("./58tongcheng_pool.xml")

# 解析xml,获得所有前端编码和坐标映射
def read_xml(ini_arr,char_map):
    DOMTree = xml.dom.minidom.parse("./58tongcheng_pool.xml")
    collection = DOMTree.documentElement
    fonts = collection.getElementsByTagName("TTGlyph")
    key_pos = {}
    for font in fonts:
        if font.getElementsByTagName('pt').length < 1:
            continue;
        x_arr = []
        y_arr = []
        for s in font.getElementsByTagName('pt'):
            x_arr.append(int(s.getAttribute('x')))
            y_arr.append(int(s.getAttribute('y')))
        key = "x"+font.getAttribute("name").replace('uni','').lower()
        key_pos[key] = str(x_arr[0]-x_arr[1])+","+str(y_arr[0]-y_arr[1]);
    return key_pos

# 获得坐标和字符映射，用于生成字典
def read_char(key_pos,char_map):
    for commom_char in ini_arr:
        if commom_char['key'] == '':
            continue
        pos = key_pos[commom_char['key']]
        char_map[pos] = commom_char['value']
    print("-----------坐标偏移->字符")
    print(char_map)

# 根据字库，解析页面,返用户信息数组
def read_html_text(html_text):
    soup = BeautifulSoup(html_text, "html.parser")
    city = soup.find('a',class_='tabA').find('span').text.strip().replace("全职招聘","")
    infolist = soup.find(id='infolist').find_all("dl")
    # sql = "insert ignore into s_resume_tongcheng(city,only,user_details_page,hope_job,name,sex,age,work_experiance,education,now_job,job_experiance) values"

    if len(infolist) < 1:
        return
    for info in infolist:
        job = " "
        sql = "insert ignore into s_resume_tongcheng(city,only,user_details_page,hope_job,name,sex,age,work_experiance,education,now_job,job_experience) values"

        a = info.find("a")
        dd =  info.find_all("dd")
        if a is None or len(dd) < 6:
            continue
        user_details_page = a.attrs['href'].split("?")[0]
        job_url = 'https://passport.58.com/login/?path=https:' + str(user_details_page)
        headers = {
            'cookie': 'Hm_lvt_a3013634de7e7a5d307653e15a0584cf=1587975452,1588228313,1588230548; Hm_lpvt_a3013634de7e7a5d307653e15a0584cf=1588990658; wmda_uuid=86e1eb2a6a94a258afda71d186cc23ed; wmda_visited_projects=%3B10104579731767%3B1731916484865%3B11187958619315%3B3381039819650%3B1409632296065%3B1731918550401%3B7790950805815%3B2286118353409%3B4200524323842; xxzl_deviceid=%2BAz2l1kUT0TH0PxuPCoMX7sPiYc7TrSxZJGwJum%2BwOhZN7Xy75Ldqsnn%2BUyQVsiI; 58tj_uuid=33d8bb90-f93e-41da-93d5-1209b5bb675b; als=0; id58=e87rZF62IncCTzbfFZqaAg==; www58com="UserID=27243117285895&UserName=ewaahh_e"; 58cooper="userid=27243117285895&username=ewaahh_e"; 58uname=ewaahh_e; sessionid=c5a822ed-a4bd-4693-9923-65586ed5a624; param8616=1; param8716kop=1; isSmartSortTipShowed=true; wmda_session_id_10104579731767=1589157993676-b11c5e9d-3aea-c067; xxzl_smartid=61e3c06eb87c9b56d9915151ab18c290; wmda_session_id_1731916484865=1589160937957-95e88c27-4e00-85ce; new_uv=6; utm_source=; spm=; init_refer=https%253A%252F%252Fha.58.com%252Fsearchjob%252Fpn3%252F%253Fparam8616%253D1%2526PGTID%253D0d302409-003c-8e57-a655-90c655f0c4b7%2526ClickID%253D5; jl_list_left_banner=1; PPU="UID=27243117285895&UN=ewaahh_e&TT=ca7d009e205e9c7952d7fdd851f410e1&PBODY=dmpe9AGUYIc8PwzZTxqGBYh91U2w0XyRbVxCJ3sFWwDkEnQAVgUy8xhH-RFN3yh6CRla0VvrywphK9ZzzhqVdaM-8T_lTrtd-mBoe6CPhKTHMnDD8fweJ2pu6A4dT3bPqXAB44QVwIzXwStnJvuy9GQF3xwCK0NY25IdcyqMCug&VER=1"; new_session=0; ljrzfc=1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.18363'}
        r2 = requests.get(job_url, headers=headers)
        html_text2 = r2.text
        soupl = BeautifulSoup(html_text2, "html.parser")
        infolist1 = soupl.find_all(class_="experience-detail")
        # sql1 = "insert ignore into s_job_experiance(itemname) values"
        # sql2 = ""
        for info in infolist1:
            if infolist1 is None:
                continue
            span = info.find_all("span")
            div = info.find_all("div")
            content = info.find(class_="item-content")
            if div[0].text is  None:
                itemName = ""
            else:
                itemName = div[0].text
            job_time = span[0].text
            Pay_level = span[1].text
            job_post = span[2].text
            job_content = ""
            if content is not None:
                job_content = content.text
            # job += "itemName:"+itemName+"','""job_time:"+job_time+"','""Pay_level:"+Pay_level+"','""job_post:"+job_post+','"job_content:" + job_content + "&"
            job +=  "\"itemName\":"+"\""+itemName+"\",""\"job_time\":\""+job_time+"\",""\"Pay_level\":\""+Pay_level+"\",""\"job_post\":\""+job_post+'\",'"\"job_content\":\"" + job_content + "\"&"
            # print(job_time)
            # print(job)
        #dpid = re.search(r'dpid=\w+', user_details_page).group(0).replace("dpid=","")
        sortid = a.attrs['sortid']
        hope_job = a.text
        name = dd[1].text
        sex = "1" if dd[2].text == "男" else "0"
        age = dd[3].text.replace("岁","")
        work_experiance = dd[4].text
        education = dd[5].text
        now_job = dd[6].text
        # sql += '("'+city+'","'+('sex='+sex+'&'+'age='+age+'&'+'education='+education+'&'+'now_job='+now_job+'&'+'hope_job='+hope_job)+'","'+user_details_page+'","'+hope_job+'","'+name+'","'+sex+'","'+age+'","'+work_experiance+'","'+education+'","'+now_job+'","'+job+'")'
        sql += '("'+city+'","'+('sex='+sex+'&'+'age='+age+'&'+'education='+education+'&'+'now_job='+now_job+'&'+'hope_job='+hope_job)+'","'+user_details_page+'","'+hope_job+'","'+name+'","'+sex+'","'+age+'","'+work_experiance+'","'+education+'","'+now_job+'",\''+job+'\')'
        sql = sql.replace(')(','),(')
        print(sql)
        db = MysqlTool.get_db('jdbc:mysql://','username','password','database')
        MysqlTool.insert(db,sql)
        time.sleep(30)


# 一个页面信息存库
def read_page(web_url,ini_arr,char_map):
    response = open_page(web_url)
    html_text = response.text
    base64_str = re.search(r'base64,(.*?)\)', html_text, re.S).group(1)
    creat_xml(base64_str)
    print('-----------页面：开始解析xml')
    print("-----------页面：转化前端编码--->坐标偏移")
    key_pos = read_xml(ini_arr,char_map)
    print("-----------页面：转换前端编码--->明文")
    for key in key_pos.keys():
        pos = key_pos[key]
        if pos in char_map:
            char_value = char_map[pos]
            html_text = html_text.replace('&#'+key+';',char_value)
    print("-----------页面：读取简历列表")
    read_html_text(html_text)
    time.sleep(5)



print("-----------字库-----------")
print(char_map)
page = 1
while page < 70:
    try:
        print("【"+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+"】第"+str(page)+"页")
        url = "https://ha.58.com/searchjob/pn"+str(page)+"/?param8616=1"
        try:
            next = read_page(url,ini_arr,char_map)
        except Exception as e:
            print("【异常】程序暂停60秒",e)
            time.sleep(60)
        page = page + 1
        if page == 70:
            page = 1
    except Exception as e:
        print("【异常】程序暂停60秒")
        time.sleep(60)
