from fastapi import FastAPI,Path,HTTPException,Query
import json
from pydantic import BaseModel,Field,computed_field
from typing import Annotated,Literal
from fastapi.responses import JSONResponse


class Patient(BaseModel):
    
    id : Annotated[str ,Field(..., description='ID of the patient',examples=['P001'])]
    name : Annotated[str,Field(..., description='name of the patient')]
    city : Annotated[str, Field(..., description='name of the city where patient resides')]
    age : Annotated[int, Field(...,gt=0,lt=120, description='Age of the patient')]
    gender : Annotated[Literal['male','female','others'],Field(...,description='Gender of the patient')]
    height : Annotated[float,Field(..., gt=0,description='height of the patient in the meters')]
    weight : Annotated[float,Field(..., gt=0,description='weight of the patient in the kgs')]
                       
    @computed_field
    @property
    def bmi(self) -> float:
        bmi = round(self.weight/(self.height**2),2)
        return bmi

    @computed_field
    @property
    def verdict(self) -> str:
        
        if self.bmi < 18.5 :
            return 'UnderWeight'

        elif self.bmi < 25:
            return 'Normal'

        elif self.bmi < 25:
            return 'Overweight'

        else:
            return 'Obsese'

        
        


app = FastAPI()

def load_data():
    with open('patients.json','r') as f:
        data = json.load(f)
        return data

def save_data(data):
    with open('patients.json','w') as f:
        json.dump(data,f)



@app.get("/")
def hello():
    return {"message":"Patient Management System"}


@app.get("/about")
def about():
    return {"message":"A fully functional API to manage your patient records"}

@app.get("/view")
def view():
    data = load_data()

    return data

@app.get("/view/{patient_id}")
def view_patient(patient_id: str =Path(...,description="ID of patient in the DB",example="P001")):
    # load all the patients
    data = load_data()

    if patient_id in data:
        return data[patient_id]
    raise HTTPException(status_code=404,detail="patient not found")

@app.get('/sort')
def sort_patients(sort_by: str = Query(...,description='sort on the basis of height,weight or bmi'), order: str = Query('asc',description='sort in ascending or descending order')):

    valid_fields =['height','weight','bmi']

    if sort_by not in valid_fields:
        raise HTTPException(status_code=404,detail=f"invalid fields select from {valid_fields}")
    
    if order not in ['asc','desc']:
        raise HTTPException(status_code=404,detail="invalid order select from asc or desc")
    
    data = load_data()

    sort_order = True if order=='desc' else False

    sorted_data = sorted(data.values(), key=lambda x:x.get(sort_by,0),reverse=sort_order)

    return sorted_data
    

@app.post("/create")
def create_patient(patient: Patient):

    # load the existing db
    data = load_data()

    # check for the existance of new patient
    if patient.id in data:
        raise HTTPException(status_code=400, detail="Patient already exist")

    # add the new patient into db
    data[patient.id] = patient.model_dump(exclude=['id'])

    # save new patient in json file
    save_data(data)

    return JSONResponse(status_code =201, content={'message':'new patient details added successfully'})



