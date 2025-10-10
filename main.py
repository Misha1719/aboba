from http.client import HTTPException

from fastapi import FastAPI, Form, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
from pydantic import BaseModel
import sqlite3


from db_helper import DATABASE, connect, init_db

app = FastAPI()

app.mount('/static',StaticFiles(directory='static'),name='static')

templates = Jinja2Templates(directory="templates")

ids = []
id = None

class create_task(BaseModel):
    title: str
    description: str | None=None

class update_task(BaseModel):
    id: int
    title: str
    description: str

class delete_task(BaseModel):
    id: int


def min_(a):
    b = ids[0]
    i = 0
    id_=0
    for id in a:
        if id<b:
            b = id
            id_ = i
        i+=1
    return [b, id_]


init_db()

@app.get('/',response_class=HTMLResponse)
async def root(request: Request):
    return RedirectResponse(url='/tasks')

@app.get("/create_task", response_class=HTMLResponse)
async def get_create_task(request: Request):
    return templates.TemplateResponse("index.html", context={"request": request})

@app.post("/post_create_task")
def post_create_task(title: str = Form(...), description: str = Form(...), task_time: str = Form(...)):
    con = connect()
    cur = con.cursor()
    if ids == []:
        cur.execute('SELECT COUNT(*) FROM tasks')
        id = cur.fetchone()[0]+1
    else:
        id = min_(ids)[0]
        ids.pop(min_(ids)[1])

    cur.execute('INSERT INTO tasks (id, title, description,task_time) VALUES (?, ?, ?, ?)',(id,title,description,task_time))
    con.commit()
    return RedirectResponse(url='/tasks', status_code=303)

@app.get("/tasks", response_class=HTMLResponse)
async def read_tasks(request: Request):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks ORDER BY task_time ASC")
    tasks = cursor.fetchall()
    conn.close()
    return templates.TemplateResponse("tasks.html", {
        "request": request,
        "tasks": tasks
    })

@app.get('/task/{id}')
def task(id: int):
    con = connect()
    cur = con.cursor()
    cur.execute('SELECT * FROM tasks WHERE id == ?', (id,))

    task=cur.fetchall()
    return task


@app.get("/update_task/{task_id}", response_class=HTMLResponse)
async def get_update_page(request: Request, task_id: int):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    task = cursor.fetchone()
    conn.close()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return templates.TemplateResponse("update_task.html", {
        "request": request,
        "task": task
    })


@app.post("/update_task/{task_id}")
async def update_task(
        task_id: int,
        title: str = Form(...),
        description: str = Form(None),
        task_time: str = Form(...)
):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Проверяем существование задачи
    cursor.execute("SELECT id FROM tasks WHERE id = ?", (task_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Task not found")

    # Обновляем задачу
    cursor.execute(
        "UPDATE tasks SET title = ?, description = ?, task_time = ? WHERE id = ?",(title, description, task_time, task_id))
    conn.commit()
    conn.close()

    return RedirectResponse(url="/tasks", status_code=303)


#Обработчик удаления задачи
@app.post("/delete_task/{task_id}")
async def delete_task(task_id: int):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    ids.append(task_id)
    conn.commit()
    conn.close()
    return RedirectResponse(url="/tasks", status_code=303)


@app.get('/test/{id}')
def test(id: int):
    con = connect()
    cur = con.cursor()
    cur.execute('SELECT * FROM tasks WHERE id == ?', (id,))
    if cur.fetchall() == []:
        ret = 'Такого id не существует'
    else:
        ret = 'Такой id Существует'
    return ret

@app.get('/tasks_title')
def titles():
    con = connect()
    cur = con.cursor()
    cur.execute('SELECT title FROM tasks')
    return cur.fetchall()









