import numpy as np
import app.logger as log

def compute_similarity(embedding1, embedding2):
    log.debug("Calculating similarity.")
    try:
        sim = np.dot(embedding1, embedding2) / (np.linalg.norm(embedding1) * np.linalg.norm(embedding2))
        return sim
    except Exception as exc:
        log.error(exc)
        return -99