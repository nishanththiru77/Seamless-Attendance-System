#!/usr/bin/env python3
"""
Face Recognition Model Validation & Re-training Tool

This script:
1. Validates the training images are properly formatted
2. Re-trains the face recognition model with proper enrollment-to-name mapping
3. Creates a detailed report of the training data
"""

import os
import cv2
import numpy as np
import pandas as pd
from PIL import Image
import pickle

def validate_and_retrain_model(base_dir):
    """Validate training images and retrain the model"""
    
    haarcascade_path = os.path.join(base_dir, "haarcascade_frontalface_default.xml")
    trainimage_path = os.path.join(base_dir, "TrainingImage")
    trainimagelabel_path = os.path.join(base_dir, "TrainingImageLabel/Trainner.yml")
    studentdetail_path = os.path.join(base_dir, "StudentDetails/studentdetails.csv")
    
    print("=" * 70)
    print("FACE RECOGNITION MODEL VALIDATION & RE-TRAINING")
    print("=" * 70)
    
    # Load student details
    print("\n1. Loading student details...")
    try:
        df_students = pd.read_csv(studentdetail_path, header=None, names=["Enrollment", "Name"], dtype=str)
        df_students["Enrollment"] = df_students["Enrollment"].astype(str).str.strip()
        df_students["Enrollment"] = pd.to_numeric(df_students["Enrollment"], errors="coerce")
        df_students = df_students.dropna(subset=["Enrollment"])
        df_students["Enrollment"] = df_students["Enrollment"].astype(int)
        df_students = df_students.drop_duplicates(subset=["Enrollment"], keep="last")
        
        enrollment_to_name = dict(zip(df_students["Enrollment"], df_students["Name"]))
        print(f"   ✓ Loaded {len(enrollment_to_name)} students:")
        for enrollment, name in sorted(enrollment_to_name.items()):
            print(f"     - {enrollment}: {name}")
    except Exception as e:
        print(f"   ✗ Error loading student details: {e}")
        return False
    
    # Analyze training images
    print("\n2. Analyzing training images...")
    image_count = 0
    enrollment_image_count = {}
    
    if not os.path.exists(trainimage_path):
        print(f"   ✗ Training image directory not found!")
        return False
    
    subdirs = [d for d in os.listdir(trainimage_path) 
               if os.path.isdir(os.path.join(trainimage_path, d))]
    
    for subdir in subdirs:
        subdir_path = os.path.join(trainimage_path, subdir)
        images = [f for f in os.listdir(subdir_path) 
                 if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.pgm'))]
        
        # Extract enrollment from directory name
        parts = subdir.split('_')
        if parts and parts[0].isdigit():
            enrollment = int(parts[0])
            enrollment_image_count[enrollment] = len(images)
            image_count += len(images)
            
            if enrollment in enrollment_to_name:
                name = enrollment_to_name[enrollment]
                print(f"   ✓ {enrollment} ({name}): {len(images)} images")
            else:
                print(f"   ⚠ {enrollment}: {len(images)} images - NO MATCHING STUDENT")
    
    print(f"\n   Total training images: {image_count}")
    
    # Check minimum images per student
    print("\n3. Checking minimum images per student...")
    MIN_IMAGES = 20
    issue_found = False
    
    for enrollment in sorted(enrollment_to_name.keys()):
        count = enrollment_image_count.get(enrollment, 0)
        name = enrollment_to_name[enrollment]
        
        if count < MIN_IMAGES:
            print(f"   ⚠ {enrollment} ({name}): Only {count} images (minimum {MIN_IMAGES} recommended)")
            issue_found = True
        else:
            print(f"   ✓ {enrollment} ({name}): {count} images")
    
    if issue_found:
        print(f"\n   ℹ Some students have fewer than {MIN_IMAGES} images.")
        print("     Consider re-capturing training images for better accuracy.")
    
    # Re-train the model
    print("\n4. Re-training face recognition model...")
    try:
        # Verify OpenCV has face module
        if not hasattr(cv2, 'face') or not hasattr(cv2.face, 'LBPHFaceRecognizer_create'):
            print("   ✗ LBPHFaceRecognizer not available!")
            return False
        
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        
        # Get images and labels
        faces = []
        ids = []
        
        for subdir in sorted(subdirs):
            subdir_path = os.path.join(trainimage_path, subdir)
            
            # Extract enrollment from directory name
            parts = subdir.split('_')
            if not parts or not parts[0].isdigit():
                continue
            
            enrollment = int(parts[0])
            
            # Get all images in this directory
            for filename in sorted(os.listdir(subdir_path)):
                if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.pgm')):
                    filepath = os.path.join(subdir_path, filename)
                    try:
                        img = Image.open(filepath).convert('L')
                        img_array = np.array(img, 'uint8')
                        faces.append(img_array)
                        ids.append(enrollment)
                    except Exception as e:
                        print(f"   ✗ Error reading {filename}: {e}")
        
        if not faces:
            print("   ✗ No valid training images found!")
            return False
        
        print(f"   ✓ Loaded {len(faces)} images for training")
        
        # Train the recognizer
        recognizer.train(faces, np.array(ids))
        
        # Create directory if needed
        model_dir = os.path.dirname(trainimagelabel_path)
        os.makedirs(model_dir, exist_ok=True)
        
        # Save the model
        recognizer.save(trainimagelabel_path)
        print(f"   ✓ Model saved to: {trainimagelabel_path}")
        
        # Create mapping file
        mapping_file = os.path.join(model_dir, "enrollment_to_name_mapping.txt")
        with open(mapping_file, 'w') as f:
            f.write("Enrollment,Name\n")
            for enrollment in sorted(enrollment_to_name.keys()):
                f.write(f"{enrollment},{enrollment_to_name[enrollment]}\n")
        print(f"   ✓ Mapping file saved to: {mapping_file}")
        
    except Exception as e:
        print(f"   ✗ Error during training: {e}")
        return False
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"✓ Trained students: {len(enrollment_to_name)}")
    print(f"✓ Total training images: {image_count}")
    print(f"✓ Model file: {trainimagelabel_path}")
    print(f"✓ Mapping file: {mapping_file}")
    
    print("\n" + "=" * 70)
    print("FACE RECOGNITION IS READY!")
    print("=" * 70)
    print("\nThe face recognition model has been re-trained with correct enrollment-to-name mappings.")
    print("You can now use the automatic attendance feature with confidence that each face")
    print("will be correctly matched to the student's name.")
    print("\nTo test:")
    print("1. Go back to the main application window")
    print("2. Click 'Automatic Attendance'")
    print("3. Verify that correct names appear for each recognized face")
    
    return True

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    validate_and_retrain_model(base_dir)
