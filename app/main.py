from fastapi import FastAPI, File
import insightface
import json
from app.helper import url_to_image, file_to_image
import numpy as np
import cv2
import app.logger as log
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from sqlalchemy import create_engine
from app.settings import DATABASE_URL
from app.models import Face
from sqlalchemy.orm import sessionmaker
from datetime import datetime, date
from typing import List, Optional
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
    res = {"message": "Insightface API web service is running"}
    return JSONResponse(content=res)


@app.post("/analyze-image-url")
async def analyze_image_url(url: str):
    # Supports multiple faces in a single image
    
    log.debug("Calling analyze_image_url.")

    image = url_to_image(url)
    faces = analyze_image(image)

    res_faces = []
    for face in faces:
        res_faces.append({
            "age": face.age, 
            "gender": face.gender, 
            "embedding": json.dumps(face.embedding.tolist())
            })
    json_compatible_faces = jsonable_encoder(res_faces)

    return JSONResponse(content=json_compatible_faces)


@app.post("/analyze-image-file")
async def analyze_image_file(file: bytes = File(...)):
    # Supports multiple faces in a single image

    log.debug("Calling analyze_image_file.")

    image = file_to_image(file)
    faces = analyze_image(image)
    
    res_faces = []
    for face in faces:
        res_faces.append({
            "age": face.age, 
            "gender": face.gender, 
            "embedding": json.dumps(face.embedding.tolist())
            })
    json_compatible_faces = jsonable_encoder(res_faces)

    return JSONResponse(content=json_compatible_faces)


@app.post("/upload-selfie")
async def upload_selfie(name: str, file: bytes = File(...)):
    # Supports single face in a single image

    log.debug("Calling upload_selfie.")

    image = file_to_image(file)

    fa_faces = analyze_image(image)

    name = name.lower()

    session = Session()

    try:
        face = Face(name = name, age = fa_faces[0].age, gender = fa_faces.gender, created_at = datetime.today())
        session.add(face)
        session.commit()
        res_face = {"name": face.name, "age": face.age, "gender": face.gender, "embedding": json.dumps(face.embedding.tolist())}
        json_compatible_faces = jsonable_encoder(res_face)

        session.close()
        return JSONResponse(content=json_compatible_faces)

    except Exception as exc:
        log.error(exc)
        session.close()
        return JSONResponse(status_code=500)


@app.post("/compute-selfie-image-files-similarity")
async def compute_selfie_image_files_similarity(file1: bytes = File(...), file2: bytes = File(...)):
    # Limited to one face for each images
    
    log.debug("Calling compute_selfie_image_files_similarity.")

    image1 = file_to_image(file1)
    image2 = file_to_image(file2)

    log.debug("Processing first image.")
    faces1 = fa.get(image1)
    emb1 = faces1[0].embedding

    log.debug("Processing second image.")
    faces2 = fa.get(image2)
    emb2 = faces2[0].embedding

    try:
        log.debug("Calculating similarity.")
        sim = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
        res = {
            "similarity": str(sim)
        }
        return JSONResponse(content=res)
    except Exception as exc:
        log.error(exc)
        return JSONResponse(status_code=500)


def analyze_image(img):
    res_faces = []
    try:
        faces = fa.get(img)
        for _, face in enumerate(faces):
            log.info("Processing face.")
            gender = 'M'
            if face.gender==0:
                gender = 'F'
            res_faces.append(Face(age = face.age, gender = gender, embedding = face.embedding))
    except Exception as exc:
        log.error(exc)
    return res_faces