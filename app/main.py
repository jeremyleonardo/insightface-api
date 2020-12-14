from fastapi import FastAPI, File, UploadFile
import insightface
from app.helper import url_to_image
import numpy as np
import io
import cv2

app = FastAPI(title = "Insightface API")
model = insightface.app.FaceAnalysis()
model.prepare(ctx_id = -1, nms=0.4)

@app.get("/")
def root():
    return {"message": "Insightface API web service is running"}

@app.post("/analyze-image-url")
async def analyze_image_url(url: str):
    img = url_to_image(url)
    faces = model.get(img)
    flatenned_faces = []
    for _, face in enumerate(faces):
        gender = 'Male'
        if face.gender==0:
            gender = 'Female'
        flatenned_faces.append(Face(age = face.age, gender = gender))
        
    return {
        "message": "Success",
        "faces": flatenned_faces
    }

@app.post("/analyze-image-file")
async def analyze_image_file(file: bytes = File(...)):
    nparr = np.fromstring(file, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    faces = model.get(image)
    flatenned_faces = []
    for _, face in enumerate(faces):
        gender = 'Male'
        if face.gender==0:
            gender = 'Female'
        flatenned_faces.append(Face(age = face.age, gender = gender))
    return {
        "message": "Success",
        "faces": flatenned_faces
    }

class Face(object):
    def __init__(self, age, gender):
        self.age = age
        self.gender = gender