import app.logger as log
import numpy as np
from app.database.models import Face

def analyze_image(img, fa):
    res_faces = []
    try:
        faces = fa.get(img)
        for _, face in enumerate(faces):
            log.debug("Processing face.")
            gender = 'M'
            if face.gender==0:
                gender = 'F'
            emb = face.embedding / np.linalg.norm(face.embedding)
            res_faces.append(Face(age = face.age, gender = gender, embedding = emb))
    except Exception as exc:
        log.error(exc)
    finally:
        return res_faces