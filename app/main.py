from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import text
from .database import Base, engine, get_db
from .models import Task
from .schemas import TaskCreate, TaskResponse, TaskUpdate

Base.metadata.create_all(bind=engine)
app = FastAPI(title="TaskFlow API", version="1.0.0")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/", include_in_schema=False)
def home(): return FileResponse("app/static/index.html")

@app.get("/health")
def health(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1")); return {"status":"healthy","service":"taskflow-api"}

@app.get("/api/tasks", response_model=list[TaskResponse])
def list_tasks(db: Session = Depends(get_db)):
    return db.query(Task).order_by(Task.created_at.desc()).all()

@app.post("/api/tasks", response_model=TaskResponse, status_code=201)
def create_task(payload: TaskCreate, db: Session = Depends(get_db)):
    task=Task(title=payload.title, description=payload.description); db.add(task); db.commit(); db.refresh(task); return task

@app.patch("/api/tasks/{task_id}", response_model=TaskResponse)
def update_task(task_id:int,payload:TaskUpdate,db:Session=Depends(get_db)):
    task=db.query(Task).filter(Task.id==task_id).first()
    if not task: raise HTTPException(404,"Task not found")
    for field in ["title","description","status"]:
        value=getattr(payload,field)
        if value is not None: setattr(task,field,value)
    db.commit(); db.refresh(task); return task

@app.delete("/api/tasks/{task_id}", status_code=204)
def delete_task(task_id:int,db:Session=Depends(get_db)):
    task=db.query(Task).filter(Task.id==task_id).first()
    if not task: raise HTTPException(404,"Task not found")
    db.delete(task); db.commit()
