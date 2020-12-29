from fastapi import FastAPI, File, HTTPException
import insightface
import json

from sqlalchemy.sql.elements import Null
from app.helper import url_to_image, file_to_image, string_to_nparray
import numpy as np
import cv2
import app.logger as log
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from sqlalchemy import create_engine, exc
from sqlalchemy.exc import IntegrityError
import app.settings as settings
from app.database.models import Face
from sqlalchemy.orm import sessionmaker
from datetime import datetime, date
from typing import List, Optional
from app.database import init as init_db, wait as wait_db


app = FastAPI(title = "Insightface API")

log.debug("Constructing FaceAnalysis model.")
fa = insightface.app.FaceAnalysis()
log.debug("Preparing FaceAnalysis model.")
fa.prepare(ctx_id = -1, nms=0.4)


engine = create_engine(settings.DATABASE_URL)
Session = sessionmaker(bind=engine)

wait_db(engine)
init_db(engine)


@app.get("/")
def root():
    json_resp = {"message": "Server Error"}
    try:
        assert fa
        json_resp = JSONResponse(content={
            "status_code": 200,
            "message": "Insightface API web service is running"
            })
    except Exception as exc:
        log.debug(exc)
        json_resp = JSONResponse(status_code=400, content={
            "status_code": 400,
            "message": "Data integrity error"
            })
    finally:
        return json_resp


@app.post("/analyze-image-url")
async def analyze_image_url(url: str):
    # Supports multiple faces in a single image
    
    log.debug("Calling analyze_image_url.")

    json_resp = {"message": "Server Error"}
    try:
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
        result = {"faces": json_compatible_faces}
    except Exception as exc:
        log.debug(exc)
        json_resp = JSONResponse(status_code=400, content={
            "status_code": 400,
            "message": "Data integrity error"
            })
    else:
        json_resp = JSONResponse(content={
            "status_code": 200,
            "result": result
            })
    finally:
        return json_resp


@app.post("/analyze-image-file")
async def analyze_image_file(file: bytes = File(...)):
    # Supports multiple faces in a single image

    log.debug("Calling analyze_image_file.")
    json_resp = {"message": "Server Error"}
    try:
        image = file_to_image(file)
        faces = analyze_image(image)
        
        res_faces = []
        for face in faces:
            res_faces.append({
                "age": face.age, 
                "gender": face.gender, 
                "embedding": json.dumps(face.embedding.tolist())
                })
        result = jsonable_encoder(res_faces)

    except Exception as exc:
        log.debug(exc)
        json_resp = JSONResponse(status_code=400, content={
            "status_code": 400,
            "message": "Data integrity error"
            })
    else:
        json_resp = JSONResponse(content={
            "status_code": 200,
            "result": result
            })
    finally:
        return json_resp


@app.post("/upload-selfie")
async def upload_selfie(name: str, file: bytes = File(...)):
    # Supports single face in a single image

    log.debug("Calling upload_selfie.")

    json_resp = {"message": "Server Error"}
    session = Session()
    try:
        name = name.lower()
        db_face = session.query(Face).filter_by(name = name).first()
        assert db_face is None

        image = file_to_image(file)
        fa_faces = analyze_image(image)

        fa_emb_str = str(json.dumps(fa_faces[0].embedding.tolist()))
        emb = "cube(ARRAY" + fa_emb_str+ ")"

        face = Face(name = name, age = fa_faces[0].age, gender = fa_faces[0].gender,  created_at = datetime.today())
        session.add(face)

        update_query = "UPDATE faces SET embedding = " + emb + " WHERE name = '" + str(face.name) + "';"
        session.commit()

        session.execute(update_query)
        session.commit()
        
        res_face = {"name": face.name, "age": face.age, "gender": face.gender, "embedding": face.embedding}
        json_compatible_faces = jsonable_encoder(res_face)

        result = json_compatible_faces

    except Exception as exc:
        if(isinstance(exc, IntegrityError)):
            log.debug(exc)
            json_resp = JSONResponse(status_code=400, content={
                "status_code": 400,
                "message": "Data integrity error"
                })
        else:
            log.error(exc)
            json_resp = json_resp = getDefaultError()
    else:
        json_resp = JSONResponse(content={
            "status_code": 200,
            "result": result
            })
    finally:
        session.close()
        return json_resp


@app.put("/faces")
async def update_face(id: int, name: str = None, file: bytes = File(None)):
    # Supports single face in a single image

    log.debug("Calling update_face.")

    json_resp = {"message": "Server Error"}
    session = Session()
    try:

        db_face = session.query(Face).get(id)
        if(db_face is None):
            return getDefaultError(status_code=404, message="Face not found.") 

        if(file is not None):
            image = file_to_image(file)
            fa_faces = analyze_image(image)
            fa_emb_str = str(json.dumps(fa_faces[0].embedding.tolist()))
            emb = "cube(ARRAY" + fa_emb_str+ ")"
            update_query = "UPDATE faces SET embedding = " + emb + " WHERE id = '" + str(db_face.id) + "';"
            session.execute(update_query)
            session.commit()

        if(name is not None):
            name = name.lower()
            db_face.name = name
        
        db_face.updated_at = datetime.today()
        session.commit()
        res_face = {"id": db_face.id, "name": db_face.name, "age": db_face.age, "gender": db_face.gender, "embedding": db_face.embedding}
        json_compatible_faces = jsonable_encoder(res_face)

        result = json_compatible_faces

    except Exception as exc:
        log.error(exc)
        json_resp = getDefaultError()
    else:
        json_resp = JSONResponse(content={
            "status_code": 200,
            "result": result
            })
    finally:
        session.close()
        return json_resp


@app.post("/face-verification")
async def face_verification(name: str, file: bytes = File(...)):
    # Supports single face in a single image

    log.debug("Calling face_verification.")

    json_resp = {"message": "Server Error"}
    session = Session()
    
    try:
        name = name.lower()
        target_face = session.query(Face).filter_by(name = name).first()
        assert target_face != None
    except Exception as exc:
        log.debug(exc)
        return JSONResponse(status_code=400, content={
            "status_code": 400,
            "message": "Name not found"
            })

    image = file_to_image(file)

    fa_faces = analyze_image(image)
    inp_face = fa_faces[0]

    try:
        target_emb = string_to_nparray(target_face.embedding)

        sim = compute_similarity(inp_face.embedding, target_emb)
        assert(sim != -99) 
        sim *= 100
        if(sim >= 60): status = True
        else: status = False
        result = {
            "similarity": int(sim),
            "status": status
            }

    except Exception as exc:
        log.error(exc)
        json_resp = getDefaultError()
    else:
        json_resp = JSONResponse(content={
            "status_code": 200,
            "result": result
            })
    finally:
        session.close()
        return json_resp


@app.post("/compute-selfie-image-files-similarity")
async def compute_selfie_image_files_similarity(file1: bytes = File(...), file2: bytes = File(...)):
    # Limited to one face for each images
    
    log.debug("Calling compute_selfie_image_files_similarity.")
    json_resp = {"message": "Server Error"}
    try:
        image1 = file_to_image(file1)
        image2 = file_to_image(file2)

        log.debug("Processing first image.")
        faces1 = fa.get(image1)
        emb1 = faces1[0].embedding

        log.debug("Processing second image.")
        faces2 = fa.get(image2)
        emb2 = faces2[0].embedding

        sim = compute_similarity(emb1, emb2)
        assert(sim != -99) 
        sim *= 100
        result = {
            "similarity": int(sim)
        }
    except Exception as exc:
        log.error(exc)
        json_resp = getDefaultError()
    else:
        json_resp = JSONResponse(content={
            "status_code": 200,
            "result": result
            })
    finally:
        return json_resp
        

@app.get("/faces")
async def get_faces(limit: int = 10):
    # Get faces from db
    
    log.debug("Calling get_faces.")
    
    session = Session()
    json_resp = {"message": "Server Error"}
    try:
        
        if(limit > 100 | limit <= 0):
            return getDefaultError(status_code=422, message="Limit must be more than 0 and less or equals 100.") 
        
        faces = session.query(Face).limit(limit).all()
        
        json_compatible_faces = jsonable_encoder(faces)
        result = {
            "faces": json_compatible_faces
            }
    except Exception as exc:
        log.error(exc)
        json_resp = getDefaultError()
    else:
        json_resp = JSONResponse(content={
            "status_code": 200,
            "result": result
            })
    finally:
        session.close()
        return json_resp


@app.delete("/faces")
async def delete_face(name: str):
    # Delete face from db

    log.debug("Calling delete_face.")

    session = Session()

    json_resp = None
    try:
        target_face = session.query(Face).filter_by(name = name).first()
        if(target_face is None):
            return getDefaultError(status_code=404, message="Not found in the database.") 
        json_compatible_face = jsonable_encoder(target_face)
        result = {
            "face": json_compatible_face
        }
        session.delete(target_face)
        session.commit()
    except Exception as exc:
        log.error(exc)
        json_resp = getDefaultError()
    else:
        json_resp = JSONResponse(content={
            "status_code": 200,
            "result": result
            })
    finally:
        session.close()
        return json_resp


def compute_similarity(embedding1, embedding2):
    log.debug("Calculating similarity.")
    try:
        sim = np.dot(embedding1, embedding2) / (np.linalg.norm(embedding1) * np.linalg.norm(embedding2))
        return sim
    except Exception as exc:
        log.error(exc)
        return -99


def analyze_image(img):
    res_faces = []
    try:
        faces = fa.get(img)
        for _, face in enumerate(faces):
            log.debug("Processing face.")
            gender = 'M'
            if face.gender==0:
                gender = 'F'
            res_faces.append(Face(age = face.age, gender = gender, embedding = face.embedding))
    except Exception as exc:
        log.error(exc)
    finally:
        return res_faces


def getDefaultError(status_code=500, message="Internal Server Error"):
    return JSONResponse(status_code=status_code, content={
        "status_code": status_code,
        "message": message
        })