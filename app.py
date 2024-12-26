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
import sql_def

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
    job_list = sql_def.search(number)

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
