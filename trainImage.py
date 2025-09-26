import csv
import os
import cv2
import numpy as np
import pandas as pd
import datetime
import time
from PIL import ImageTk, Image

# Train Image
def TrainImage(haarcasecade_path, trainimage_path, trainimagelabel_path, message, text_to_speech):
    try:
        # Ensure cv2.face is available
        if not hasattr(cv2, 'face') or not hasattr(cv2.face, 'LBPHFaceRecognizer_create'):
            raise AttributeError("LBPHFaceRecognizer_create not found. Please install opencv-contrib-python.")
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        faces, Id = getImagesAndLables(trainimage_path)
        if not faces:
            res = "No training images found. Please register students first."
            message.configure(text=res)
            text_to_speech(res)
            return
        recognizer.train(faces, np.array(Id))
        os.makedirs(os.path.dirname(trainimagelabel_path), exist_ok=True)
        recognizer.save(trainimagelabel_path)
        res = "Image Trained successfully"
        message.configure(text=res)
        text_to_speech(res)
    except Exception as e:
        res = f"Error during training: {str(e)}"
        message.configure(text=res)
        text_to_speech(res)

def getImagesAndLables(path):
    # Collect image paths from subdirectories, filtering valid image files
    if not os.path.isdir(path):
        return [], []

    subdirs = [
        os.path.join(path, d)
        for d in os.listdir(path)
        if os.path.isdir(os.path.join(path, d))
    ]
    image_paths = []
    valid_ext = (".jpg", ".jpeg", ".png", ".bmp", ".pgm")
    for d in subdirs:
        for f in os.listdir(d):
            if f.lower().endswith(valid_ext):
                image_paths.append(os.path.join(d, f))

    faces = []
    Ids = []
    for img_path in image_paths:
        try:
            pilImage = Image.open(img_path).convert("L")
            imageNp = np.array(pilImage, "uint8")
            # Expect filename format: Name_Enrollment_Index.ext
            base = os.path.basename(img_path)
            parts = base.split("_")
            if len(parts) < 3:
                continue
            enrollment_str = parts[1]
            Id = int(enrollment_str)
            faces.append(imageNp)
            Ids.append(Id)
        except Exception:
            # Skip unreadable/corrupt files or bad names
            continue
    return faces, Ids