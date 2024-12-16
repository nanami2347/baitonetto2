import sqlite3
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from selenium import webdriver
from selenium.webdriver.common.by import By
import re
#import sql_baitonetto
import sql_update

def pagecount(html):
      kensu_list = re.findall('検索結果<span class="mainFontColor">(.*)</span>件',html)
      if kensu_list == []:
        return(1)
      else:
        kensu_all = kensu_list[0]
        kensu_all_string = kensu_all.replace(',', '')
        kensu_all_int = int(kensu_all_string)
        page = kensu_all_int // 20 + 2
        return(page)

def sagasu(page,name,url):
      job_url_all = []

      for i in range(1, page):
        j = str(i)
        #URL_job = "https://baitonet.jp/search/?page=" + j
        URL_job = url + j
        driver.get(URL_job)
        job_html = driver.page_source
        job_123 = re.findall(name, job_html)
        job_url = list(set(job_123))
        job_url_all = job_url_all + job_url
      return(job_url_all)

def sigotonaiyoucount(job_url_all):
  joblist = []
  for job in job_url_all:
        search_url = 'https://baitonet.jp/' + job
        driver.get(search_url)
        element = driver.find_element(By.CLASS_NAME, "jobContentsTxt")
        element = element.text
        elementcount = len(element)
        job_only_url = 'https://baitonet.jp/' + job
        jobname = (job.replace('job_', '').replace('/', ''))
        joblist.append([jobname,elementcount,element,job_only_url])
  return(joblist)

def search(number):
    #p = [1,"北海道", "青森県","岩手県","宮城県","秋田県","山形県","福島県","茨城県","栃木県","群馬県","埼玉","千葉県","東京都","神奈川県","新潟県","富山県","石川県","福井県","山梨県","長野県","岐阜県","静岡県","愛知県","三重県","滋賀県","京都府","大阪府","兵庫県","奈良県","和歌山県","鳥取県","島根県","岡山県","広島県","山口県","徳島県","香川県","愛媛県","高知県","福岡県","佐賀県","長崎県","熊本県","大分県","宮崎県","鹿児島県","沖縄県"]
    todouhuken = str(number)
    todouhuken_url = 'ps_' + todouhuken + '/'
    URL = "https://baitonet.jp/search/" + todouhuken_url
    #print("URL:",URL) 
    driver.get(URL)
    ahtml = driver.page_source
    #print("ahtml:",ahtml)
    apage = pagecount(ahtml)
    #url_sagasu="https://baitonet.jp/search/?page="
    url_sagasu="https://baitonet.jp/search/" + todouhuken_url + "?page="
    jobURL = sagasu(apage,'job_[0-9]{7}/',url_sagasu)
    ajob = sigotonaiyoucount(jobURL)
    
    #jobURL_matome =sagasu(apage,'job_group_[0-9]{3}/',"https://baitonet.jp/search/?page=")
    jobURL_matome =sagasu(apage,'job_group_[0-9]{3}/',"https://baitonet.jp/search/" + todouhuken_url + "?page=")
    bjob = []

    for k in jobURL_matome:
     jobURL_motome_k = 'https://baitonet.jp/' + k +  todouhuken_url
     url_sagasu=jobURL_motome_k+"/?page="
     driver.get(jobURL_motome_k)
     bhtml = driver.page_source
     bpage = pagecount(bhtml)
     if bpage>=2:
        jobURL_b = sagasu(bpage,'job_[0-9]{7}/',url_sagasu)
        bjob = bjob + sigotonaiyoucount(jobURL_b)

    cjob = ajob + bjob
    return(cjob)

class item(BaseModel):
    count : int
    prefecture : str

class item2(BaseModel):
    prefecture : str

app = FastAPI()


@app.post("/search/")
def select(item:item): 
    with sqlite3.connect('baitonetto.db') as conn:
        cur = conn.cursor()
        #sql = f"SELECT * FROM numbers WHERE count <= (?) and prefecture = (?)"
        sql = f"SELECT * FROM numbers WHERE count <= (?) and prefecture = (?) ORDER BY count"

        numbers_lis = cur.execute(sql, (item.count, item.prefecture)).fetchall()
        conn.commit()
        dic_list=[]
        print(numbers_lis)
        for row in numbers_lis:
            dic={"id":row[0],"kid":row[1], "prefecture":row[2], "count":row[3], "content":row[4]}
            dic_list.append(dic)
        #dic_list.sort(key=lambda x: x[3])
        param =  {'number':dic_list}
        return JSONResponse(content=param)
    
@app.patch("/makedb/")
def change(item2:item2):
    p = [1,"北海道", "青森県","岩手県","宮城県","秋田県","山形県","福島県","茨城県","栃木県","群馬県","埼玉","千葉県","東京都","神奈川県","新潟県","富山県","石川県","福井県","山梨県","長野県","岐阜県","静岡県","愛知県","三重県","滋賀県","京都府","大阪府","兵庫県","奈良県","和歌山県","鳥取県","島根県","岡山県","広島県","山口県","徳島県","香川県","愛媛県","高知県","福岡県","佐賀県","長崎県","熊本県","大分県","宮崎県","鹿児島県","沖縄県"]
    number = p.index(item2.prefecture)
    job_list = sql_update.search(number)

    if len(job_list) == 0:
        message='更新しました。(ちなみに０件です。)'
        param =  {'message':message}
        return JSONResponse(content=param)

    with sqlite3.connect('baitonetto.db') as conn:
        cur = conn.cursor()
        for l in job_list:
            print(l[0])
            
            naiyo_list = cur.execute("SELECT * FROM numbers WHERE kid = (?)", (int(l[0]),)).fetchall()
            conn.commit()
            if len(naiyo_list) == 0:
                cur.execute("insert into numbers (kid,prefecture,count,content) values(?,?,?,?)", (l[0],number,l[1],l[2]))
            else:
                cur.execute("UPDATE numbers SET kid=(?),prefecture=(?),count=(?),content=(?) WHERE id LIKE (?)", (l[0],number,l[1],l[2],naiyo_list[0]))
            
            conn.commit()
        message='更新しました。'
        param =  {'message':message}
        return JSONResponse(content=param)
