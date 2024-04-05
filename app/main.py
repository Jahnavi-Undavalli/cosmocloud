from fastapi import FastAPI, HTTPException, Query
from starlette.responses import RedirectResponse
from pydantic import BaseModel
from pymongo import MongoClient
from bson import ObjectId
from typing import Optional

app = FastAPI()

# Connect to MongoDB Atlas cluster
client = MongoClient("mongodb+srv://undavallijahnavi354:nOLRg7qj0Nr9A1CF@cluster0.oy5ozvu.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["library"]
students_collection = db["students"]

class StudentUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    address: Optional[dict] = None

class Address(BaseModel):
    city: str
    country: str

class StudentCreate(BaseModel):
    name: str
    age: int
    address: Address

class StudentResponse(BaseModel):
    message: str

class Student(BaseModel):
    id: str
    name: str
    age: int
    address: Address

@app.post("/students", response_model=StudentResponse, status_code=201)
def create_student(student: StudentCreate):
    student_data = student.dict()
    result = students_collection.insert_one(student_data)
    if result.inserted_id:
        return {"message": "Student added successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to add student")

@app.get("/students", response_model=list[Student])
def list_students(country: str = Query(None), age: int = Query(None)):
    filter_criteria = {}
    if country:
        filter_criteria["address.country"] = country
    if age is not None:
        filter_criteria["age"] = {"$gte": age}  
    students = students_collection.find(filter_criteria)
    student_list = [{"id": str(student["_id"]), "name": student["name"], "age": student["age"], "address": student["address"]} for student in students]
    return student_list

@app.get("/students/{id}", response_model=Student)
def get_student(id: str):
    student = students_collection.find_one({"_id": ObjectId(id)})
    if student:
        return {"id": str(student["_id"]), "name": student["name"], "age": student["age"], "address": student["address"]}
    else:
        raise HTTPException(status_code=404, detail="Student not found")

@app.patch("/students/{id}", status_code=202)
def update_student(id: str, student: StudentUpdate):
    updated_student_data = student.dict(exclude_unset=True)
    result = students_collection.update_one({"_id": ObjectId(id)}, {"$set": updated_student_data})
    if result.modified_count ==1:
        return {"message": "Student details updated successfully"}
    else:
        raise HTTPException(status_code=404, detail="Student not found")

@app.delete("/students/{id}", response_model=dict)
def delete_student(id: str):
    result = students_collection.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 1:
        return {"message": "Student deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Student not found")

@app.get("/")
def root():
    return RedirectResponse(url="/students")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
