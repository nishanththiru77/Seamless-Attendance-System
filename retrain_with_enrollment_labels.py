#!/usr/bin/env python3
"""
Retrain LBPH recognizer using enrollment numbers as labels (so predictions are enrollment IDs).
"""
import os
import cv2
import numpy as np
from pathlib import Path

print("Retraining using enrollment numbers as labels...")
training_path = "TrainingImage"
model_path = "TrainingImageLabel/Trainner.yml"

recognizer = cv2.face.LBPHFaceRecognizer_create(radius=1, neighbors=8, grid_x=8, grid_y=8)
faces = []
labels = []

for person_dir in sorted(os.listdir(training_path)):
    person_path = os.path.join(training_path, person_dir)
    if not os.path.isdir(person_path):
        continue
    # Expect folder format like '033_Nishanth' or '005_Ajay'
    parts = person_dir.split('_', 1)
    if len(parts) < 1:
        continue
    enrollment_str = parts[0]
    try:
        enrollment = int(enrollment_str)
    except ValueError:
        print(f"Skipping folder with non-integer enrollment: {person_dir}")
        continue
    image_count = 0
    for fname in os.listdir(person_path):
        if not fname.lower().endswith('.jpg'):
            continue
        img_path = os.path.join(person_path, fname)
        img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            continue
        try:
            img = cv2.resize(img, (200, 200))
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            img = clahe.apply(img)
            img = cv2.bilateralFilter(img, 9, 75, 75)
            img = cv2.normalize(img, None, 0, 255, cv2.NORM_MINMAX)
            faces.append(img)
            labels.append(enrollment)
            image_count += 1
        except Exception as e:
            print(f"Error processing {img_path}: {e}")
    print(f"Loaded {image_count} images for enrollment {enrollment} ({person_dir})")

if len(faces) == 0:
    print("No training images found. Aborting.")
else:
    recognizer.train(faces, np.array(labels))
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    recognizer.save(model_path)
    print(f"Model saved to {model_path}")
    print(f"Total samples: {len(faces)} | Unique labels: {len(set(labels))}")
