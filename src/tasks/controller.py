from src.tasks.dtos import TaskSchema, TaskOut
from sentence_transformers import SentenceTransformer
from sqlalchemy.orm import Session
from src.tasks.models import TaskModel
from fastapi import HTTPException
from src.user.models import UserModel
from src.generate_embeddings import get_embedding
import traceback
import numpy as np

def cosine_distance(a, b):
    a = np.array(a)
    b = np.array(b)
    return 1 - np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def create_task(body:TaskSchema, db:Session, user:UserModel):

    data=body.model_dump()
    # Combine text for embedding
    text = f"{data['title']} {data['description']}"

    # Generate embedding vector

    embedding = get_embedding(text)

    new_task=TaskModel(title=data["title"],
                       description=data["description"],
                       is_completed=data["is_completed"],
                       user_id=user.id,
                       embedding=embedding
                       )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)


    # return {"status":"Task Created Successfully...","data":new_task}
    return new_task


def get_tasks(db:Session, user:UserModel):
    tasks=db.query(TaskModel).filter(TaskModel.user_id==user.id).all()
    return tasks

def search_tasks(query: str, db: Session, user:UserModel):

    try:
        # 1. Convert query to embedding vector
        query_vector = get_embedding(query)

        # 2. Fetch tasks ordered by similarity
        tasks = (
            db.query(TaskModel)
            .filter(TaskModel.user_id == user.id)
            .all()
        )

        # 🔥 filter AFTER ranking
        
        filtered= [
            task for task in tasks
            if cosine_distance(task.embedding, query_vector) < 0.7
        ]

        # 3. Convert ORM objects → Pydantic models (IMPORTANT FIX)
        return [
            TaskOut.model_validate(task)
            for task in filtered
        ]

    except Exception as e:

        error_message = traceback.format_exc()

        raise HTTPException(
            status_code=500,
            detail=error_message
        )
def update_task(body:TaskSchema, task_id:int, db:Session, user:UserModel):
    one_task:TaskModel=db.query(TaskModel).get(task_id)
    if not one_task:
        raise HTTPException(404, detail="Task ID is Incorrect")
    
    if one_task.user_id!=user.id:
        raise HTTPException(401, detail="You are not allowed to update this task")
    
    # one_task.title=body.title
    # one_task.description=body.description
    # one_task.is_completed=body.is_completed
    body=body.model_dump()
    for field, value in body.items():
        setattr(one_task, field,value)

    db.add(one_task)
    db.commit()
    db.refresh(one_task)

    return one_task

def delete_task(task_id:int,db:Session, user:UserModel):
    one_task=db.query(TaskModel).get(task_id)
    if not one_task:
        raise HTTPException(404, detail="Task ID is Incorrect")
    
    if one_task.user_id!=user.id:
        raise HTTPException(401, detail="You are not allowed to delete this task")

    db.delete(one_task)
    db.commit()

    # return{"status":"Task Deleted Successfully","data":one_task}
    return None