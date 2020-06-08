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




# 搜索保存一页的职位信息
def search_save_job(page_num):
    page_url ="https://ha.58.com/job/pn"+str(page_num)
    headers = {
        'accept-language':'zh-CN,zh;q=0.9',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
    }
    response = requests.get(page_url, headers=headers)
    html_text = response.text
    soup = BeautifulSoup(html_text, "html.parser")
    if soup.find(id = "list_con") is None or soup.find(id = "list_con").find_all("li",class_="job_item") is None:
        time.sleep(5)
        return
    job_info_list = soup.find(id = "list_con").find_all("li",class_="job_item")
    sql = "insert ignore into s_job_tongcheng(job_name,job_salary,job_wel,comp_name,cate,xueli,jingyan,only) values"
    for job_info in job_info_list:
        job_name = "" if job_info.find(class_="job_name") is None else job_info.find(class_="job_name").text.replace(" ","").replace("\n","")
        job_salary = "" if job_info.find(class_="job_salary") is None else job_info.find(class_="job_salary").text.replace(" ","").replace("\n","")
        job_wel = "" if job_info.find(class_="job_wel") is None else job_info.find(class_="job_wel").text.replace(" ","").replace("\n",",").strip(",")
        comp_name = "" if job_info.find(class_="comp_name").find("a") is None else job_info.find(class_="comp_name").find("a").attrs['title'].replace(" ","").replace("\n","")
        cate = "" if job_info.find(class_="cate") is None else job_info.find(class_="cate").text.replace(" ","").replace("\n","")
        xueli = "" if job_info.find(class_="xueli") is None else job_info.find(class_="xueli").text.replace(" ","").replace("\n","")
        jingyan = "" if job_info.find(class_="jingyan") is None else job_info.find(class_="jingyan").text.replace(" ","").replace("\n","")
        sql += "('"+job_name+"','"+job_salary+"','"+job_wel+"','"+comp_name+"','"+cate+"','"+xueli+"','"+jingyan+"','"+("comp_name="+comp_name+"&cate="+cate+"&job_name="+job_name)+"')"
    sql = sql.replace(")(","),(")
    print(sql)
    db = MysqlTool.get_db('jdbc:mysql://','username','password','database')
    MysqlTool.insert(db,sql)
    time.sleep(5)

#  delete from s_58_pool where LEFT(create_time,10) <= DATE_SUB(CURDATE(),INTERVAL 3 day) and tel is null

page = 1
while page < 70:
    try:
        print("【"+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+"】第"+str(page)+"页")
        search_save_job(page)
        page = page + 1
        if page == 70:
            page =1
    except Exception as e:
        print("【异常】程序暂停60秒")
        time.sleep(60)
