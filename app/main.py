from fastapi import FastAPI, File, UploadFile
import insightface
from app.helper import url_to_image
import numpy as np
import io
import cv2

app = FastAPI(title = "Insightface API")

fa = insightface.app.FaceAnalysis()
fa.prepare(ctx_id = -1, nms=0.4)


@app.get("/")
def root():
    return {"message": "Insightface API web service is running"}


@app.post("/analyze-image-url-gender-age")
async def analyze_image_url_gender_age(url: str):
    # Supports multiple faces in a single image
    
    img = url_to_image(url)
    faces = fa.get(img)
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


@app.post("/analyze-image-file-gender-age")
async def analyze_image_file_gender_age(file: bytes = File(...)):
    # Supports multiple faces in a single image

    nparr = np.fromstring(file, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    faces = fa.get(image)
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


@app.post("/compute-similarity")
async def compute_similarity(file1: bytes = File(...), file2: bytes = File(...)):
    # Limited to one face for each images
    
    nparr = np.fromstring(file1, np.uint8)
    image1 = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    nparr = np.fromstring(file2, np.uint8)
    image2 = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    faces1 = fa.get(image1)
    faces2 = fa.get(image2)

    emb1 = faces1[0].embedding
    emb2 = faces2[0].embedding
    sim = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))

    return {
        "message": "Success",
        "similarity": str(sim)
    }


class Face(object):
    def __init__(self, age, gender):
        self.age = age
        self.gender = gender