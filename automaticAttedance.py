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
        now = time.time()
        future = now + 20
        print(now)
        print(future)
        if sub == "":
            t = "Please enter the subject name!!!"
            text_to_speech(t)
        else:
            try:
                # Validate recognizer availability and load model
                if not hasattr(cv2, "face") or not hasattr(cv2.face, "LBPHFaceRecognizer_create"):
                    text_to_speech("Face recognizer not available. Please install opencv-contrib-python.")
                    return
                recognizer = cv2.face.LBPHFaceRecognizer_create()
                if not os.path.exists(trainimagelabel_path):
                    text_to_speech("Model not found, please train the model first.")
                    return
                try:
                    recognizer.read(trainimagelabel_path)
                except Exception:
                    text_to_speech("Failed to load the model. Please retrain.")
                    return
                facecasCade = cv2.CascadeClassifier(haarcasecade_path)
                if facecasCade.empty():
                    text_to_speech("Failed to load face cascade.")
                    return
                df_raw = pd.read_csv(studentdetail_path, header=None, names=["Enrollment", "Name"], dtype={"Enrollment": int, "Name": str})
                df = df_raw.drop_duplicates(subset=["Enrollment"], keep="last")
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
                    Notifica.configure(text="Camera started. Press ESC to stop.")
                except Exception:
                    pass
                font = cv2.FONT_HERSHEY_SIMPLEX
                col_names = ["Enrollment", "Name"]
                attendance = pd.DataFrame(columns=col_names)
                while True:
                    ret, im = cam.read()
                    if not ret or im is None:
                        continue
                    gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
                    faces = facecasCade.detectMultiScale(gray, 1.2, 5)
                    for (x, y, w, h) in faces:
                        Id, conf = recognizer.predict(gray[y : y + h, x : x + w])
                        if conf < 70:
                            name_values = df.loc[df["Enrollment"] == Id]["Name"].values
                            display_name = str(name_values[0]) if len(name_values) > 0 else "Unknown"
                            tt = f"{Id}-{display_name}"
                            attendance.loc[len(attendance)] = [Id, display_name]
                            cv2.rectangle(im, (x, y), (x + w, y + h), (0, 260, 0), 4)
                            cv2.putText(im, str(tt), (x + h, y), font, 1, (255, 255, 0,), 4)
                        else:
                            Id = "Unknown"
                            tt = str(Id)
                            cv2.rectangle(im, (x, y), (x + w, y + h), (0, 25, 255), 7)
                            cv2.putText(im, str(tt), (x + h, y), font, 1, (0, 25, 255), 4)
                    if time.time() > future:
                        break
                    cv2.imshow("Filling Attendance...", im)
                    key = cv2.waitKey(30) & 0xFF
                    if key == 27:
                        break
                ts = time.time()
                date = datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
                timeStamp = datetime.datetime.fromtimestamp(ts).strftime("%H:%M:%S")
                attendance[date] = 1
                Hour, Minute, Second = timeStamp.split(":")
                path = os.path.join(attendance_path, sub)
                if not os.path.exists(path):
                    os.makedirs(path)
                fileName = (
                    f"{path}/"
                    + sub
                    + "_"
                    + date
                    + "_"
                    + Hour
                    + "-"
                    + Minute
                    + "-"
                    + Second
                    + ".csv"
                )
                attendance = attendance.drop_duplicates(["Enrollment"], keep="first")
                print(attendance)
                attendance.to_csv(fileName, index=False)
                m = f"Attendance Filled Successfully for {sub}"
                text_to_speech(m)
                cam.release()
                cv2.destroyAllWindows()

                # Modern attendance display
                import csv
                import tkinter
                from tkinter import ttk

                root = tkinter.Tk()
                root.title(f"✅ Attendance Captured - {sub}")
                root.geometry("800x500")
                root.configure(background="#0f0f23")
                
                try:
                    root.iconbitmap("AMS.ico")
                except:
                    pass

                # Header
                header_frame = tkinter.Frame(root, bg="#1e3a5f", height=60)
                header_frame.pack(fill=tkinter.X, padx=10, pady=10)
                header_frame.pack_propagate(False)

                header_title = tkinter.Label(
                    header_frame,
                    text=f"✅ {sub} - Attendance Successfully Captured",
                    bg="#1e3a5f",
                    fg="#00d4ff",
                    font=("Segoe UI", 16, "bold")
                )
                header_title.pack(pady=15)

                # Scrollable content
                main_frame = tkinter.Frame(root, bg="#2c5282")
                main_frame.pack(fill=tkinter.BOTH, expand=True, padx=10, pady=10)

                canvas = tkinter.Canvas(main_frame, bg="#2c5282", highlightthickness=0)
                scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
                scrollable_frame = tkinter.Frame(canvas, bg="#2c5282")

                scrollable_frame.bind(
                    "<Configure>",
                    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
                )

                canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
                canvas.configure(yscrollcommand=scrollbar.set)

                cs = fileName
                print(cs)
                with open(cs, newline="") as file:
                    reader = csv.reader(file)
                    data = list(reader)
                    
                    if data:
                        # Header row
                        header_row = tkinter.Frame(scrollable_frame, bg="#1e3a5f", relief=tkinter.FLAT, bd=2)
                        header_row.pack(fill=tkinter.X, padx=5, pady=5)
                        
                        for col_idx, header in enumerate(data[0]):
                            header_label = tkinter.Label(
                                header_row,
                                text=header,
                                bg="#1e3a5f",
                                fg="#ffd700",
                                font=("Segoe UI", 12, "bold"),
                                width=15,
                                height=2,
                                relief=tkinter.FLAT
                            )
                            header_label.grid(row=0, column=col_idx, padx=2, pady=2, sticky="ew")
                        
                        # Data rows
                        for row_idx, row_data in enumerate(data[1:], 1):
                            row_bg = "#2c5282" if row_idx % 2 == 0 else "#16213e"
                            data_row = tkinter.Frame(scrollable_frame, bg=row_bg, relief=tkinter.FLAT, bd=1)
                            data_row.pack(fill=tkinter.X, padx=5, pady=2)
                            
                            for col_idx, cell_data in enumerate(row_data):
                                cell_label = tkinter.Label(
                                    data_row,
                                    text=cell_data,
                                    bg=row_bg,
                                    fg="#ffffff",
                                    font=("Segoe UI", 11),
                                    width=15,
                                    height=1,
                                    relief=tkinter.FLAT
                                )
                                cell_label.grid(row=0, column=col_idx, padx=2, pady=2, sticky="ew")

                canvas.pack(side="left", fill="both", expand=True)
                scrollbar.pack(side="right", fill="y")

                root.mainloop()
                print(attendance)
            except:
                f = "No Face found for attendance"
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
        text="Enter the subject name to start automated face recognition attendance",
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
        text="📋 Instructions:\n• Make sure your camera is connected and working\n• Students should look directly at the camera\n• Attendance will be captured for 20 seconds\n• Press ESC to stop early if needed",
        bg=BG_PANEL,
        fg=FG_SECONDARY,
        font=("Segoe UI", 10),
        justify=LEFT
    )
    instructions_label.pack(pady=15)

    subject.mainloop()
