from fastapi import FastAPI, File, UploadFile
import insightface
from app.helper import url_to_image
import numpy as np
import io
import cv2
import app.logger as log

from sqlalchemy import create_engine
from app.settings import DATABASE_URL
from app.models import Face
from sqlalchemy.orm import sessionmaker
from datetime import datetime, date
from typing import Optional
from app.database import create_database


app = FastAPI(title = "Insightface API")

log.debug("Constructing FaceAnalysis model.")
fa = insightface.app.FaceAnalysis()
log.debug("Preparing FaceAnalysis model.")
fa.prepare(ctx_id = -1, nms=0.4)


engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

create_database(engine)


@app.get("/")
def root():
    return {"message": "Insightface API web service is running"}


@app.post("/analyze-image-url-gender-age")
async def analyze_image_url_gender_age(url: str):
    # Supports multiple faces in a single image
    
    log.debug("Calling analyze_image_url_gender_age.")

    img = url_to_image(url)
    faces = fa.get(img)
    flatenned_faces = []
    for _, face in enumerate(faces):
        log.info("Processing face.")
        gender = 'M'
        if face.gender==0:
            gender = 'F'
        flatenned_faces.append(Face(age = face.age, gender = gender))
        
    return {
        "message": "Success",
        "faces": flatenned_faces
    }


@app.post("/analyze-image-file-gender-age")
async def analyze_image_file_gender_age(file: bytes = File(...)):
    # Supports multiple faces in a single image

    log.debug("Calling analyze_image_file_gender_age.")

    nparr = np.fromstring(file, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    faces = fa.get(image)
    flatenned_faces = []
    for _, face in enumerate(faces):
        gender = 'M'
        if face.gender==0:
            gender = 'F'
        flatenned_faces.append(Face(age = face.age, gender = gender))
    return {
        "message": "Success",
        "faces": flatenned_faces
    }


@app.post("/compute-similarity")
async def compute_similarity(file1: bytes = File(...), file2: bytes = File(...)):
    # Limited to one face for each images
    
    log.debug("Calling compute_similarity.")

    log.debug("Decoding first image.")
    nparr = np.fromstring(file1, np.uint8)
    image1 = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    log.debug("Decoding second image.")
    nparr = np.fromstring(file2, np.uint8)
    image2 = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    log.debug("Processing first image.")
    faces1 = fa.get(image1)
    emb1 = faces1[0].embedding

    log.debug("Processing second image.")
    faces2 = fa.get(image2)
    emb2 = faces2[0].embedding

    log.debug("Calculating similarity.")
    sim = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))

    return {
        "message": "Success",
        "similarity": str(sim)
    }

