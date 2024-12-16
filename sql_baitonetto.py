import sqlite3
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import JSONResponse
import datetime
from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

class item(BaseModel):
    title : str
    making_time : str
    serves : str
    ingredients : str
    cost : int

app = FastAPI()

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=200,
        content=jsonable_encoder({"message": "Recipe creation failed!","required": "title, making_time, serves, ingredients, cost"}),
    )

@app.post("/recipes")
def make(item:item):
    '''
    if item.title is None or item.making_time is None or item.serves is None or item.ingredients is None or item.cost is None :
        param = {"message": "Recipe creation failed!", "required": "title, making_time, serves, ingredients, cost"}
        return JSONResponse(status_code=200, content=param)
    '''
    with sqlite3.connect('recipes.db') as conn:
        '''
        cur = conn.cursor()
        sql = f"SELECT * FROM recipes WHERE id LIKE (?)"
        recipes_lis = cur.execute(sql, (item.id,)).fetchall()
        conn.commit()
        count = len(recipes_lis)
        if count == 0:
        '''
        cur = conn.cursor()
        now = datetime.datetime.now()
        now_str = now.strftime("%Y-%m-%d %H:%M:%S")
        data = (item.title,item.making_time, item.serves, item.ingredients, item.cost, now_str, now_str)
        sql = f"INSERT INTO recipes (title,making_time,serves,ingredients,cost,created_at,updated_at) values (?,?,?,?,?,?,?)"
        cur.execute(sql, data)
        conn.commit()
        sql2 = f"SELECT * FROM recipes WHERE id  = (select max(id) from recipes)"
        recipes_lis = cur.execute(sql2).fetchall()
        dic_list=[]
        for row in recipes_lis:
          dic={"id":row[0], "title":row[1], "making_time":row[2], "serves":row[3], "ingredients":row[4], "cost":row[5], "created_at":row[6], "updated_at":row[7]}
          dic_list.append(dic)
          param =  {'message':"Recipe successfully created!",'recipe':dic_list}
        return JSONResponse(status_code=200, content=param)
        '''
        else:
            param = {"message": "Recipe creation failed!", "required": "title, making_time, serves, ingredients, cost"}
            return JSONResponse(status_code=404, content=param)
        '''
@app.get("/recipes")
def all(): 
    with sqlite3.connect('recipes.db') as conn:
        cur = conn.cursor()
        recipes_lis = cur.execute('SELECT * FROM recipes').fetchall()
        conn.commit()
        dic_list=[]
        for row in recipes_lis:
            dic={"id":row[0], "title":row[1], "making_time":row[2], "serves":row[3], "ingredients":row[4], "cost":row[5]}
            dic_list.append(dic)
        param =  {'recipes':dic_list}
        return JSONResponse(status_code=200, content=param)
    
@app.get("/v1/stocks")
def select(id:int): 
    with sqlite3.connect('recipes.db') as conn:
        cur = conn.cursor()
        sql = f"SELECT * FROM recipes WHERE id LIKE (?)"
        recipes_lis = cur.execute(sql, (id,)).fetchall()
        conn.commit()
        dic_list=[]
        for row in recipes_lis:
            dic={"id":row[0], "title":row[1], "making_time":row[2], "serves":row[3], "ingredients":row[4], "cost":row[5]}
            dic_list.append(dic)
        param =  {'message':"Recipe details by id",'recipe':dic_list}
        return JSONResponse(status_code=200, content=param)
    
@app.patch("/recipes/{id}")
def change(id:int, item:item): 
    with sqlite3.connect('recipes.db') as conn:
        now = datetime.datetime.now()
        now_str = now.strftime("%Y-%m-%d %H:%M:%S")
        cur = conn.cursor()
        data = (item.title,item.making_time, item.serves, item.ingredients, item.cost, now_str, id)
        sql = f"UPDATE recipes SET title=(?),making_time=(?),serves=(?),ingredients=(?),cost=(?),updated_at=(?) WHERE id LIKE (?)"
        cur.execute(sql, data).fetchall()
        conn.commit()
        #cur = conn.cusor()
        sql2 = f"SELECT * FROM recipes WHERE id LIKE (?)"
        recipes_lis = cur.execute(sql2, (id,)).fetchall()
        conn.commit()
        dic_list=[]
        for row in recipes_lis:
            dic={"id":row[0], "title":row[1], "making_time":row[2], "serves":row[3], "ingredients":row[4], "cost":row[5]}
            dic_list.append(dic)
            param =  {'message':"Recipe successfuliy updated!",'recipe':dic_list}
        return JSONResponse(status_code=200, content=param)
        
@app.delete("/recipes/{id}")
def out(id:int): 
    with sqlite3.connect('recipes.db') as conn:
        cur = conn.cursor()
        sql = f"SELECT * FROM recipes WHERE id LIKE (?)"
        recipes_lis = cur.execute(sql, (id,)).fetchall()
        conn.commit()
        count = len(recipes_lis)
        if count == 0:
            param = { "message":"No Recipe found" }
            return JSONResponse(status_code=404, content=param)
        else:
            cur = conn.cursor()
            sql = f"DELETE FROM recipes WHERE id LIKE (?)"
            cur.execute(sql, (id,)).fetchall()
            conn.commit()
            param = {  "message": "Recipe successfully removed!" }
            return JSONResponse(status_code=200, content=param)
