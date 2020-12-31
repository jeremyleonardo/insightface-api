from fastapi import FastAPI, File
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

import insightface
import json
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.helper import url_to_image, file_to_image, string_to_nparray

import app.logger as log
import app.settings as settings
from app.exception import *
from app.exception.handling import *
from app.database.models import Face
from app.database import init as init_db, wait as wait_db
from app.analyze import *


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
    assert fa
    json_resp = JSONResponse(content={
        "status_code": 200,
        "message": "Insightface API web service is running"
        })

    return json_resp


@app.post("/analyze-image-url")
async def analyze_image_url(url: str):
    # Supports multiple faces in a single image
    
    log.debug("Calling analyze_image_url.")

    image = url_to_image(url)
    faces = analyze_image(image, fa)
    res_faces = []
    for face in faces:
        res_faces.append({
            "age": face.age, 
            "gender": face.gender, 
            "embedding": json.dumps(face.embedding.tolist())
            })
    json_compatible_faces = jsonable_encoder(res_faces)
    result = {"faces": json_compatible_faces}

    json_resp = JSONResponse(content={
        "status_code": 200,
        "result": result
        })

    return json_resp


@app.post("/analyze-image-file")
async def analyze_image_file(file: bytes = File(...)):
    # Supports multiple faces in a single image

    log.debug("Calling analyze_image_file.")

    image = file_to_image(file)
    faces = analyze_image(image, fa)
    
    res_faces = []
    for face in faces:
        res_faces.append({
            "age": face.age, 
            "gender": face.gender, 
            "embedding": json.dumps(face.embedding.tolist())
            })
    result = jsonable_encoder(res_faces)

    json_resp = JSONResponse(content={
        "status_code": 200,
        "result": result
        })
    return json_resp


@app.post("/upload-selfie")
async def upload_selfie(name: str, file: bytes = File(...)):
    # Supports single face in a single image

    log.debug("Calling upload_selfie.")
    session = Session()

    name = name.lower()
    db_face = session.query(Face).filter_by(name = name).first()
    if db_face is not None:
        raise ValidationError("Name must be unique.")

    image = file_to_image(file)
    fa_faces = analyze_image(image, fa)

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

    json_resp = JSONResponse(content={
        "status_code": 200,
        "result": result
        })

    session.close()
    return json_resp


@app.put("/faces")
async def update_face(id: int, name: str = None, file: bytes = File(None)):
    # Supports single face in a single image

    log.debug("Calling update_face.")
    session = Session()

    db_face = session.query(Face).get(id)
    if(db_face is None):
        raise NotFoundError("Face not found.") 

    if(file is not None):
        image = file_to_image(file)
        fa_faces = analyze_image(image, fa)
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

    json_resp = JSONResponse(content={
        "status_code": 200,
        "result": result
        })

    session.close()
    return json_resp


@app.post("/face-verification")
async def face_verification(name: str, file: bytes = File(...)):
    # Supports single face in a single image

    log.debug("Calling face_verification.")
    session = Session()
    
    name = name.lower()
    target_face = session.query(Face).filter_by(name = name).first()
    if target_face != None:
        raise NotFoundError("Face with that name does not exist in database.")

    image = file_to_image(file)

    fa_faces = analyze_image(image, fa)
    inp_face = fa_faces[0]

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

    json_resp = JSONResponse(content={
        "status_code": 200,
        "result": result
        })

    session.close()
    return json_resp


@app.post("/face-search")
async def face_search(file: bytes = File(...)):
    # Supports single face in a single image

    log.debug("Calling face_search.")
    session = Session()

    image = file_to_image(file)

    fa_faces = analyze_image(image, fa)
    inp_face = fa_faces[0]

    fa_emb_str = str(json.dumps(inp_face.embedding.tolist()))
    emb = "cube(ARRAY" + fa_emb_str+ ")"
    query = (
        "SELECT sub.* "
        "FROM "
        "( "
            "SELECT *, (1-(POWER(( embedding <-> " + emb + " ),2)/2))*100 AS similarity "
            "FROM faces "
        ") AS sub "
        "WHERE sub.gender = '" + inp_face.gender + "' AND sub.similarity > 60 "
        "ORDER BY sub.similarity DESC;"
        )
    
    query_res = session.execute(query)

    rows_proxy = query_res.fetchall()
    
    dict, arr = {}, []
    for row_proxy in rows_proxy:
        for column, value in row_proxy.items():
            dict = {**dict, **{column: value}}
            print(dict)
        arr.append(dict)

    result = jsonable_encoder({
        "similar_faces": arr
        })

    json_resp = JSONResponse(content={
        "status_code": 200,
        "result": result
        })
        
    session.close()
    return json_resp


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

    sim = compute_similarity(emb1, emb2)
    assert(sim != -99) 
    sim *= 100
    result = {
        "similarity": int(sim)
    }

    json_resp = JSONResponse(content={
        "status_code": 200,
        "result": result
        })

    return json_resp
        

@app.get("/faces")
async def get_faces(limit: int = 10):
    # Get faces from db
    
    log.debug("Calling get_faces.")
    session = Session()
        
    if(limit > 100 or limit <= 0):
        raise ValidationError("Limit must be more than 0 and less or equals 100.") 
    
    faces = session.query(Face).limit(limit).all()
    
    json_compatible_faces = jsonable_encoder(faces)
    result = {
        "faces": json_compatible_faces
        }

    json_resp = JSONResponse(content={
        "status_code": 200,
        "result": result
        })
    session.close()
    return json_resp


@app.delete("/faces")
async def delete_face(name: str):
    # Delete face from db

    log.debug("Calling delete_face.")
    session = Session()

    target_face = session.query(Face).filter_by(name = name).first()
    if(target_face is None):
        raise NotFoundError("Not found in the database.") 
    json_compatible_face = jsonable_encoder(target_face)
    result = {
        "face": json_compatible_face
    }
    session.delete(target_face)
    session.commit()

    json_resp = JSONResponse(content={
        "status_code": 200,
        "result": result
        })

    session.close()
    return json_resp


@app.exception_handler(NotFoundError)
async def not_found_error_handler(request, exc):
    log.error(str(exc))
    json_resp = get_error_response(status_code=404, message=str(exc))
    return json_resp


@app.exception_handler(ValidationError)
async def validation_error_handler(request, exc):
    log.error(str(exc))
    json_resp = get_error_response(status_code=422, message=str(exc))
    return json_resp


@app.exception_handler(RequestValidationError)
async def request_validation_error_handler(request, exc):
    log.error(str(exc))
    json_resp = get_error_response(status_code=400, message=str(exc))
    return json_resp


@app.exception_handler(Exception)
async def exception_handler(request, exc):
    log.error(str(exc))
    json_resp = get_default_error_response()
    return json_resp