import tkinter as tk
from tkinter import *
import os, cv2
import shutil
import csv
import numpy as np
from PIL import ImageTk, Image
import pandas as pd
import datetime
import time
import tkinter.ttk as tkk
import tkinter.font as font
import checkpoint_attendance  # NEW: Import checkpoint system
# from improved_face_recognition import ImprovedFaceRecognizer  # NEW: Improved face recognition

haarcasecade_path = "haarcascade_frontalface_default.xml"
trainimagelabel_path = (
    "TrainingImageLabel/Trainner.yml"
)
trainimage_path = "TrainingImage"
studentdetail_path = (
    "StudentDetails/studentdetails.csv"
)
attendance_path = "Attendance"
# for choose subject and fill attendance
def subjectChoose(text_to_speech):
    def FillAttendance():
        sub = tx.get()
        if sub == "":
            t = "Please enter the subject name!!!"
            text_to_speech(t)
        else:
            try:
                # Load Haarcascade face detector
                face_cascade = cv2.CascadeClassifier(haarcasecade_path)
                if face_cascade.empty():
                    text_to_speech("Failed to load face cascade.")
                    return

                # Open camera (Windows-friendly with fallbacks)
                cam = None
                for src, api in [(0, cv2.CAP_DSHOW), (0, None), (1, cv2.CAP_DSHOW), (1, None)]:
                    tmp = cv2.VideoCapture(src, api) if api is not None else cv2.VideoCapture(src)
                    if tmp.isOpened():
                        cam = tmp
                        break
                if cam is None or not cam.isOpened():
                    text_to_speech("Unable to access camera. Please connect a camera and try again.")
                    return
                try:
                    Notifica.configure(text="Camera started. 3 scan instances will run.")
                except Exception:
                    pass
                # Run three scan instances with gaps, without marking/saving attendance
                total_instances = 3
                scan_duration = 5        # seconds per scan instance
                gap_duration = 10        # seconds gap between scans

                early_exit = False

                for instance in range(1, total_instances + 1):
                    instance_end = time.time() + scan_duration
                    try:
                        Notifica.configure(text=f"Scanning INSTANCE {instance}/{total_instances}...")
                    except Exception:
                        pass

                    while time.time() < instance_end:
                        ret, frame = cam.read()
                        if not ret or frame is None:
                            continue

                        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

                        # Draw rectangles around detected faces
                        for (x, y, w, h) in faces:
                            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                        # Overlay current instance label
                        cv2.putText(
                            frame,
                            f"INSTANCE {instance}/{total_instances}",
                            (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            1,
                            (0, 255, 255),
                            2,
                            cv2.LINE_AA,
                        )

                        cv2.imshow("Attendance Scanning", frame)
                        key = cv2.waitKey(30) & 0xFF
                        if key == 27:  # ESC
                            early_exit = True
                            break

                    if early_exit:
                        break

                    # If not the last instance, show gap countdown
                    if instance < total_instances:
                        gap_start_text = f"Next scan in {gap_duration} seconds"
                        try:
                            Notifica.configure(text=gap_start_text)
                        except Exception:
                            pass

                        for remaining in range(gap_duration, 0, -1):
                            ret, frame = cam.read()
                            if not ret or frame is None:
                                # Create a blank frame if camera read fails
                                frame = np.zeros((480, 640, 3), dtype=np.uint8)

                            msg = f"Next scan in {remaining} seconds"
                            cv2.putText(
                                frame,
                                msg,
                                (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                1,
                                (0, 255, 255),
                                2,
                                cv2.LINE_AA,
                            )
                            cv2.putText(
                                frame,
                                f"Upcoming: INSTANCE {instance + 1}/{total_instances}",
                                (10, 70),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                1,
                                (0, 255, 255),
                                2,
                                cv2.LINE_AA,
                            )

                            cv2.imshow("Attendance Scanning", frame)
                            key = cv2.waitKey(1000) & 0xFF  # 1 second per loop
                            if key == 27:  # ESC
                                early_exit = True
                                break

                        if early_exit:
                            break

                cam.release()
                cv2.destroyAllWindows()

                try:
                    if early_exit:
                        Notifica.configure(text="Scanning stopped early by user (ESC).")
                    else:
                        Notifica.configure(text="Scanning finished. 3 instances completed.")
                except Exception:
                    pass
            except:
                f = "Error during scanning"
                text_to_speech(f)
                cv2.destroyAllWindows()

    # Modern Theme Constants (matching main app)
    BG_GRADIENT_START = "#0f0f23"
    BG_GRADIENT_END = "#1a1a2e"
    BG_DARK = "#16213e"
    BG_PANEL = "#1e3a5f"
    BG_CARD = "#2c5282"
    FG_PRIMARY = "#00d4ff"
    FG_SECONDARY = "#ffffff"
    FG_ACCENT = "#ffd700"
    BTN_PRIMARY = "#4299e1"
    BTN_PRIMARY_HOVER = "#3182ce"
    BTN_SUCCESS = "#38a169"
    BTN_SUCCESS_HOVER = "#2f855a"
    BTN_WARNING = "#ed8936"
    BTN_WARNING_HOVER = "#dd6b20"

    def create_gradient_frame(parent, width, height, color1, color2):
        """Create a gradient background effect. Caller should place/lower it."""
        canvas = tk.Canvas(parent, width=width, height=height, highlightthickness=0)
        
        for i in range(height):
            ratio = i / height
            r1, g1, b1 = int(color1[1:3], 16), int(color1[3:5], 16), int(color1[5:7], 16)
            r2, g2, b2 = int(color2[1:3], 16), int(color2[3:5], 16), int(color2[5:7], 16)
            
            r = int(r1 + (r2 - r1) * ratio)
            g = int(g1 + (g2 - g1) * ratio)
            b = int(b1 + (b2 - b1) * ratio)
            
            color = f"#{r:02x}{g:02x}{b:02x}"
            canvas.create_line(0, i, width, i, fill=color)
        
        return canvas

    def style_button(btn, bg=BTN_PRIMARY, hover_bg=BTN_PRIMARY_HOVER, fg=FG_SECONDARY):
        """Enhanced button styling"""
        btn.configure(
            bg=bg,
            fg=fg,
            activebackground=hover_bg,
            activeforeground=fg,
            bd=0,
            relief=FLAT,
            highlightthickness=0,
            cursor="hand2",
            font=("Segoe UI", 12, "bold"),
            padx=20,
            pady=10
        )

        def on_enter(event):
            btn.configure(bg=hover_bg, relief=RAISED, bd=2)

        def on_leave(event):
            btn.configure(bg=bg, relief=FLAT, bd=0)

        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

    # Modern subject selection window
    subject = Toplevel()
    subject.title("📊 Take Attendance - CLASS VISION")
    subject.geometry("700x500")
    subject.resizable(0, 0)
    subject.configure(background=BG_GRADIENT_START)
    
    try:
        subject.iconbitmap("AMS.ico")
    except:
        pass

    # Create gradient background and place it behind other widgets
    gradient_canvas = create_gradient_frame(subject, 700, 500, BG_GRADIENT_START, BG_GRADIENT_END)
    try:
        gradient_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        gradient_canvas.lower()
    except Exception:
        pass

    # Header
    header_frame = tk.Frame(subject, bg=BG_PANEL, height=80)
    header_frame.pack(fill=X, padx=20, pady=20)
    header_frame.pack_propagate(False)

    header_title = tk.Label(
        header_frame,
        text="📊 Automated Attendance",
        bg=BG_PANEL,
        fg=FG_PRIMARY,
        font=("Segoe UI", 24, "bold")
    )
    header_title.pack(pady=20)

    # Main content card
    content_card = tk.Frame(subject, bg=BG_CARD, relief=FLAT, bd=0)
    content_card.pack(fill=BOTH, expand=True, padx=40, pady=20)

    # Instructions
    instruction_label = tk.Label(
        content_card,
        text="Attendence is turned on",
        bg=BG_CARD,
        fg=FG_SECONDARY,
        font=("Segoe UI", 14),
        pady=20
    )
    instruction_label.pack()

    # Subject input section
    input_frame = tk.Frame(content_card, bg=BG_CARD)
    input_frame.pack(pady=30)

    sub_label = tk.Label(
        input_frame,
        text="📚 Subject Name:",
        bg=BG_CARD,
        fg=FG_ACCENT,
        font=("Segoe UI", 16, "bold")
    )
    sub_label.pack(pady=(0, 10))

    tx = tk.Entry(
        input_frame,
        width=25,
        bd=2,
        bg=BG_PANEL,
        fg=FG_PRIMARY,
        relief=SOLID,
        font=("Segoe UI", 16),
        insertbackground=FG_PRIMARY,
        highlightthickness=1,
        highlightcolor=FG_PRIMARY,
        justify=CENTER
    )
    tx.pack(ipady=10)

    # Notification area
    notification_frame = tk.Frame(content_card, bg=BG_CARD)
    notification_frame.pack(pady=20, fill=X, padx=20)

    Notifica = tk.Label(
        notification_frame,
        text="Ready to start attendance capture...",
        bg=BG_PANEL,
        fg=FG_ACCENT,
        font=("Segoe UI", 12),
        relief=SOLID,
        bd=2,
        pady=10
    )
    Notifica.pack(fill=X)

    # Buttons frame
    buttons_frame = tk.Frame(content_card, bg=BG_CARD)
    buttons_frame.pack(pady=30)

    def open_folder():
        sub = tx.get()
        if sub == "":
            t = "Please enter the subject name!!!"
            text_to_speech(t)
        else:
            try:
                os.startfile(f"Attendance\\{sub}")
            except:
                t = f"Folder for {sub} not found!"
                text_to_speech(t)

    # Start Attendance button
    def start_attendance(event=None):
        FillAttendance()

    fill_btn = tk.Button(
        buttons_frame,
        text="🎥 Start Attendance",
        command=start_attendance,
        font=("Segoe UI", 14, "bold"),
        height=2,
        width=18,
    )
    style_button(fill_btn, bg=BTN_SUCCESS, hover_bg=BTN_SUCCESS_HOVER)
    fill_btn.pack(side=LEFT, padx=15)

    # Bind Enter key to start attendance
    tx.bind('<Return>', start_attendance)

    # Open Folder button
    folder_btn = tk.Button(
        buttons_frame,
        text="📁 Open Folder",
        command=open_folder,
        font=("Segoe UI", 14, "bold"),
        height=2,
        width=15,
    )
    style_button(folder_btn, bg=BTN_WARNING, hover_bg=BTN_WARNING_HOVER)
    folder_btn.pack(side=LEFT, padx=15)

    # Instructions section
    instructions_frame = tk.Frame(content_card, bg=BG_PANEL, relief=FLAT, bd=2)
    instructions_frame.pack(fill=X, padx=20, pady=20)

    instructions_label = tk.Label(
        instructions_frame,
        text="📋 Instructions:\n• Make sure your camera is connected and working\n• Students should look directly at the camera\n• The system will run 3 scan instances\n• Each instance scans for ~5 seconds\n• There is a 10‑second gap between scans\n• No attendance will be saved in this mode\n• Press ESC to stop early if needed",
        bg=BG_PANEL,
        fg=FG_SECONDARY,
        font=("Segoe UI", 10),
        justify=LEFT
    )
    instructions_label.pack(pady=15)

    subject.mainloop()
