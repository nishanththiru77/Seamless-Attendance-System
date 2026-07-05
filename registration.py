import csv
import os, cv2
import numpy as np
import pandas as pd
import datetime
import time



# take Image of user
def TakeImage(l1, l2, haarcasecade_path, trainimage_path, message, err_screen,text_to_speech):
    if (l1 == "") and (l2==""):
        t='Please Enter the your Enrollment Number and Name.'
        text_to_speech(t)
    elif l1=='':
        t='Please Enter the your Enrollment Number.'
        text_to_speech(t)
    elif l2 == "":
        t='Please Enter the your Name.'
        text_to_speech(t)
    else:
        try:
            # Try common camera backends/indices (improves Windows reliability)
            cam = None
            # try a sequence of indices and APIs, log attempts for debugging
            for src, api in [(0, cv2.CAP_DSHOW), (0, cv2.CAP_MSMF), (0, cv2.CAP_ANY),
                             (1, cv2.CAP_DSHOW), (1, cv2.CAP_MSMF), (1, cv2.CAP_ANY)]:
                try:
                    if api is not None:
                        print(f"Trying camera source {src} with api {api}")
                        cap = cv2.VideoCapture(src, api)
                    else:
                        print(f"Trying camera source {src} with default API")
                        cap = cv2.VideoCapture(src)
                except Exception as exc:
                    print(f"Exception opening camera {src} api {api}: {exc}")
                    cap = None
                if cap is not None and cap.isOpened():
                    cam = cap
                    print(f"Camera initialized on source {src} api {api}")
                    break

            if cam is None or not cam.isOpened():
                # speak and update the UI label to inform the user
                text_to_speech("Unable to access camera. Please connect a camera and try again.")
                try:
                    message.configure(text="Camera not found")
                except Exception:
                    pass
                print("Error: camera could not be opened by any of the tried backends.")
                return

            detector = cv2.CascadeClassifier(haarcasecade_path)
            Enrollment = l1
            Name = l2
            sampleNum = 0
            directory = Enrollment + "_" + Name
            path = os.path.join(trainimage_path, directory)
            os.makedirs(path, exist_ok=True)

            # show live feed even before any face is detected so user knows camera is working
            cv2.namedWindow("Frame", cv2.WINDOW_NORMAL)
            while True:
                ret, img = cam.read()
                if not ret or img is None:
                    # camera gave no frame; wait a bit and retry
                    time.sleep(0.05)
                    continue

                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                faces = detector.detectMultiScale(gray, 1.3, 5)
                # draw rectangles and save on every detected face
                for (x, y, w, h) in faces:
                    cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
                    sampleNum += 1
                    try:
                        cv2.imwrite(
                            os.path.join(path, f"{Name}_{Enrollment}_{sampleNum}.jpg"),
                            gray[y : y + h, x : x + w],
                        )
                    except Exception:
                        pass
                # always show the current frame so the user sees the camera feed
                cv2.imshow("Frame", img)

                key = cv2.waitKey(1) & 0xFF
                if key == ord("q"):
                    break
                elif sampleNum > 50:
                    break

            try:
                cam.release()
            except Exception:
                pass
            try:
                cv2.destroyAllWindows()
            except Exception:
                pass

            row = [Enrollment, Name]
            os.makedirs(os.path.dirname("StudentDetails/studentdetails.csv"), exist_ok=True)
            with open("StudentDetails/studentdetails.csv", "a+",) as csvFile:
                writer = csv.writer(csvFile, delimiter=",")
                writer.writerow(row)

            res = "Images Saved for ER No:" + Enrollment + " Name:" + Name
            try:
                message.configure(text=res)
            except Exception:
                pass
            text_to_speech(res)
        except Exception as e:
            # Print full error to console for debugging, speak only a friendly message
            import traceback
            error_details = traceback.format_exc()
            print(f"ERROR in TakeImage: {error_details}")
            
            # Speak a user-friendly message, not the raw exception
            text_to_speech("An error occurred while capturing images. Please try again.")
            try:
                message.configure(text="Error: Please check console logs and try again")
            except Exception:
                pass
            try:
                cam.release()
            except Exception:
                pass
            try:
                cv2.destroyAllWindows()
            except Exception:
                pass
