from flask import Flask, redirect, render_template, request, session, url_for

from selenium import webdriver
from selenium.webdriver.common.by import By
import re


djob=[]

options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument('--disable-dev-shm-usage')
options.add_argument("--no-sandbox")

driver = webdriver.Chrome(
            options=options
        )


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
        joblist.append([jobname,elementcount,job_only_url])
  return(joblist)

app = Flask(__name__) 
app.config["SECRET_KEY"] = 'secret_key' 


@app.route('/', methods=['GET', 'POST']) 
def index(): 
    if request.method == 'POST':

        session['todouhuken'] = request.form['todouhuken']
        session['count'] = request.form['count']
        todouhuken = session['todouhuken']
        count = int (session['count'])
        todouhuken_url = 'ps_' + todouhuken + '/'

        #URL = "https://baitonet.jp/search/"
        URL = "https://baitonet.jp/search/" + todouhuken_url



        driver.get(URL)
        ahtml = driver.page_source
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

        cjob.sort(key=lambda x: x[1])

        #djob = []
        #for m in cjob[0][1]:
        for m in cjob:
         num=m[1]
         if num <= count : 
            djob.append(m)
            #print(djob)
         else:
            break

        #title = driver.title
        driver.close()
        #return render_template('work.html', arr=arr1d)
        return redirect(url_for('work')) 
    return render_template('search.html') 

@app.route('/work') 
def work(): 
  return render_template('work.html', arr=djob) 
  #return render_template('work.html') 
 
 
if __name__ == '__main__':
  app.run(debug=True,port=80) 