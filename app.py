import sqlite3
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

class item(BaseModel):
    count : int
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