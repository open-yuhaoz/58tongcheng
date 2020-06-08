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
import os
warnings.filterwarnings("ignore")


# 搜索保存企业信息
def search_save_enterprise(enterprise_name):
    url = "https://www.qichacha.com/search?key="+enterprise_name
    headers = {
        'cookie':'zg_did=%7B%22did%22%3A%20%2216f01e6fc9a287-09f78c7fd358d2-3c604504-1fa400-16f01e6fc9b399%22%7D; UM_distinctid=16f01e6fcc60-0c9a7ff58694dd-3c604504-1fa400-16f01e6fcc77a6; _uab_collina=157628491298421272054837; acw_tc=77a7bc2115762849094503571ed864bace39d5c1dd1373e2f18b0910d6; QCCSESSID=9ucjno7p2upkmj8s82dkft6ve1; CNZZDATA1254842228=1316452498-1576284793-https%253A%252F%252Fwww.so.com%252F%7C1577078021; hasShow=1; acw_sc__v3=5e00582d268df765dbfdcaf8047d44499dc164fd; Hm_lvt_3456bee468c83cc63fb5147f119f1075=1576457084,1577080878,1577080909,1577080951; acw_sc__v2=5e0058c97c7c0644dd979cc2b1278ca5b7e3d4b1; zg_de1d1a35bfa24ce29bbf2c7eb17e6c4f=%7B%22sid%22%3A%201577080877332%2C%22updated%22%3A%201577081094169%2C%22info%22%3A%201577080877334%2C%22superProperty%22%3A%20%22%7B%7D%22%2C%22platform%22%3A%20%22%7B%7D%22%2C%22utm%22%3A%20%22%7B%7D%22%2C%22referrerDomain%22%3A%20%22www.so.com%22%2C%22cuid%22%3A%20%22b5127ab2c1fa07af7386b121206db537%22%2C%22zs%22%3A%200%2C%22sc%22%3A%200%7D; Hm_lpvt_3456bee468c83cc63fb5147f119f1075=1577081094',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
    }
    html_text = ""
    try:
        html_text = requests.get(url,headers=headers, timeout=5).text
    except requests.exceptions.RequestException:
        print("请求超时，程序暂停60秒")
        time.sleep(60)
        return
    soup = BeautifulSoup(html_text, "html.parser")
    if re.search(r'小查没有找到相关数据', html_text) is not None:
        db = MysqlTool.get_db('jdbc:mysql://','username','password','database')
        MysqlTool.update(db,"update s_job_tongcheng set has_qichacha = 2 where comp_name = '"+enterprise_name+"'")
        print("企查查未搜索到【"+enterprise_name+"】")
        return
    if soup.find(id='search-result') is None or soup.find(id='search-result').find("tr") is None:
        print("访问过于频繁，需要重新验证。等待60秒")
        time.sleep(60)
        return
    enterprise = soup.find(id='search-result').find("tr")
    res = {}
    url = "https://www.qichacha.com/" + enterprise.find("a").attrs['href']
    res_text = enterprise.text.replace(" ","").replace("\n","").replace("更多号码","").replace("更多邮箱","")
    print("搜索结果："+res_text)
    res['enterprise_name'] = enterprise_name
    res['boss_name'] = re.search(r'：.+注册资本：', res_text).group(0).replace("注册资本","").replace("：","")
    res['start_date'] = re.search(r'成立日期：.+邮箱：', res_text).group(0).replace("成立日期：","").replace("邮箱：","")
    res['email'] = re.search(r'邮箱：.+电话：', res_text).group(0).replace("邮箱：","").replace("电话：","")
    res['tel'] = re.search(r'电话：.+地址：', res_text).group(0).replace("电话：","").replace("地址：","")
    res['address'] = re.search(r'地址：.+', res_text).group(0).replace("地址：","")
    res['url'] = url
    sql = "insert ignore into s_enterprise_qichacha(enterprise_name,boss_name,start_date,email,tel,address,url) values"
    sql += "('"+res['enterprise_name']+"','"+res['boss_name']+"','"+res['start_date']+"','"+res['email']+"','"+res['tel']+"','"+res['address']+"','"+res['url']+"')"
    db = MysqlTool.get_db('jdbc:mysql://','username','password','database')
    MysqlTool.insert(db,sql)
    db = MysqlTool.get_db('jdbc:mysql://','username','password','database')
    MysqlTool.update(db,"update s_job_tongcheng set has_qichacha = 1 where comp_name = '"+res['enterprise_name']+"'")
    time.sleep(7)

while 1:
    try:
        db = MysqlTool.get_db('jdbc:mysql://','username','password','database')
        rows = MysqlTool.select(db,"select comp_name from s_job_tongcheng where has_qichacha = 0 GROUP BY comp_name order by create_time desc limit 0,10")
        if len(rows) < 1:
            print("*******************暂无需要查询的企业，等待30秒*********************")
            time.sleep(30)
        else:
            print("企业列表："+str(rows))
        for row in rows:
            print("【"+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+"】搜索："+row[0])
            search_save_enterprise(row[0])
    except Exception as e:
        print("【异常】程序暂停60秒")
        time.sleep(60)
