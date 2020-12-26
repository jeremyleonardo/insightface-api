import cv2
import numpy as np
import urllib
import urllib.request
import app.logger as log

def url_to_image(url):
    try:
        resp = urllib.request.urlopen(url)
        image = np.asarray(bytearray(resp.read()), dtype="uint8")
        image = cv2.imdecode(image, cv2.IMREAD_COLOR)
        return image
    except Exception as exc:
        log.error(exc)
        return None


def file_to_image(file):
    try:
        nparr = np.fromstring(file, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return image
    except Exception as exc:
        log.error(exc)
        return None


def string_to_nparray(string):
    log.debug("Converting string to nparray")
    try:
        rpr = string.replace("[", "")
        rpr = rpr.replace("]", "")
        res = np.fromstring(rpr, dtype=float, sep=',')
        return res
    except Exception as exc:
        log.error(exc)
        return None