def automatic_attendance():
    animate_button_click(btn_attend, BTN_PRIMARY, BTN_PRIMARY_HOVER)
    automaticAttedance.subjectChoose(text_to_speech)
def exit_application():
    animate_button_click(btn_exit, BTN_DANGER, BTN_DANGER_HOVER)
    window.after(200, window.quit)
import tkinter as tk
from tkinter import *
from tkinter import simpledialog
from tkinter import ttk
import os, cv2
import shutil
import csv
import numpy as np
from PIL import ImageTk, Image
import pandas as pd
import datetime
import time
import tkinter.font as font
import tkinter.messagebox as messagebox
import pyttsx3

# project module
import show_attendance
import takemanually
import trainImage
import automaticAttedance
import checkpoint_attendance
import registration as takeImage


def text_to_speech(user_text):
    engine = pyttsx3.init()
    engine.say(user_text)
    engine.runAndWait()


# Modern Theme Constants
BG_GRADIENT_START = "#0f0f23"
BG_GRADIENT_END = "#1a1a2e"
BG_DARK = "#16213e"
BG_PANEL = "#1e3a5f"
BG_CARD = "#2c5282"
FG_PRIMARY = "#00d4ff"  # Bright cyan
FG_SECONDARY = "#ffffff"
FG_ACCENT = "#ffd700"  # Gold
BTN_PRIMARY = "#4299e1"
BTN_PRIMARY_HOVER = "#3182ce"
BTN_SUCCESS = "#38a169"
BTN_SUCCESS_HOVER = "#2f855a"
BTN_DANGER = "#e53e3e"
BTN_DANGER_HOVER = "#c53030"
BTN_WARNING = "#ed8936"
BTN_WARNING_HOVER = "#dd6b20"
SHADOW_COLOR = "#0a0a0a"


def create_gradient_frame(parent, width, height, color1, color2):
    """Create a gradient background canvas (caller should place it)."""
    canvas = tk.Canvas(parent, width=width, height=height, highlightthickness=0, bd=0)
    
    # Create gradient effect
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


def style_button(btn, bg=BTN_PRIMARY, hover_bg=BTN_PRIMARY_HOVER, fg=FG_SECONDARY, shadow=True):
    """Enhanced button styling with clear borders and hover effects"""
    btn.configure(
        bg=bg,
        fg=fg,
        activebackground=hover_bg,
        activeforeground=fg,
        bd=2,
        relief=RAISED,
        highlightthickness=2,
        highlightbackground=FG_ACCENT,
        highlightcolor=FG_ACCENT,
        cursor="hand2",
        font=("Segoe UI", 12, "bold"),
        padx=20,
        pady=10
    )

    def on_enter(event):
        btn.configure(bg=hover_bg, bd=3)

    def on_leave(event):
        btn.configure(bg=bg, bd=2)

    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)


def create_card_frame(parent, x, y, width, height, title, icon_path=None):
    """Create a modern card-style frame (uses pack layout for reliability)"""
    # Container for spacing
    container = tk.Frame(parent, bg=BG_GRADIENT_START)
    container.pack(side=LEFT, padx=10, pady=10, fill=BOTH, expand=True)

    # Main card frame with fixed size
    card_frame = tk.Frame(container, bg=BG_CARD, height=height, width=width, relief=FLAT, bd=0)
    card_frame.pack()
    card_frame.pack_propagate(False)

    # Card header
    header_frame = tk.Frame(card_frame, bg=BG_PANEL, height=60, width=width)
    header_frame.pack(fill=X, padx=2, pady=2)
    header_frame.pack_propagate(False)
    
    # Icon and title
    if icon_path and os.path.exists(icon_path):
        try:
            icon = Image.open(icon_path)
            icon = icon.resize((40, 40), Image.LANCZOS)
            icon_photo = ImageTk.PhotoImage(icon)
            icon_label = tk.Label(header_frame, image=icon_photo, bg=BG_PANEL)
            icon_label.image = icon_photo
            icon_label.pack(side=LEFT, padx=10, pady=10)
        except:
            pass
    
    title_label = tk.Label(
        header_frame, 
        text=title, 
        bg=BG_PANEL, 
        fg=FG_PRIMARY, 
        font=("Segoe UI", 14, "bold")
    )
    title_label.pack(side=LEFT, padx=10, pady=15)
    
    # Content frame
    content_frame = tk.Frame(card_frame, bg=BG_CARD)
    content_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
    
    return card_frame, content_frame


def animate_button_click(button, original_bg, click_bg):
    """Add click animation to buttons"""
    button.configure(bg=click_bg)
    button.after(100, lambda: button.configure(bg=original_bg))


haarcasecade_path = "haarcascade_frontalface_default.xml"
trainimagelabel_path = (
    "./TrainingImageLabel/Trainner.yml"
)
trainimage_path = "./TrainingImage"
os.makedirs(trainimage_path, exist_ok=True)

studentdetail_path = (
    "./StudentDetails/studentdetails.csv"
)
attendance_path = "Attendance"

# Create main window with modern styling
window = Tk()
window.title("CLASS VISION - Smart Attendance Management System")
window.geometry("1400x750")
window.configure(background=BG_GRADIENT_START)
window.resizable(True, True)

# Create gradient background (pack first so other widgets appear on top)
# Gradient disabled to avoid layering issues that can hide widgets
# gradient_canvas = create_gradient_frame(window, 1400, 800, BG_GRADIENT_START, BG_GRADIENT_END)
# gradient_canvas.place(x=0, y=0, relwidth=1, relheight=1)

# Set window icon
try:
    window.iconbitmap("AMS.ico")
except:
    pass

# Menu bar and key bindings
menubar = tk.Menu(window)
actions_menu = tk.Menu(menubar, tearoff=0)
actions_menu.add_command(label="Register (Ctrl+R)", command=lambda: register_student())
actions_menu.add_command(label="Take Attendance (Ctrl+A)", command=lambda: automatic_attedance())
actions_menu.add_command(label="View Reports (Ctrl+V)", command=lambda: view_attendance())
actions_menu.add_command(label="Past Reports (Ctrl+P)", command=lambda: past_reports.show_past_reports(text_to_speech))
actions_menu.add_separator()
actions_menu.add_command(label="Exit (Esc)", command=lambda: exit_application())
menubar.add_cascade(label="Actions", menu=actions_menu)

help_menu = tk.Menu(menubar, tearoff=0)
help_menu.add_command(label="About", command=lambda: messagebox.showinfo("About", "CLASS VISION\nSmart Attendance Management System"))
menubar.add_cascade(label="Help", menu=help_menu)

window.config(menu=menubar)

# Keyboard shortcuts
window.bind_all("<Control-r>", lambda e: register_student())
window.bind_all("<Control-a>", lambda e: automatic_attedance())
window.bind_all("<Control-v>", lambda e: view_attendance())
window.bind_all("<Control-p>", lambda e: past_reports.show_past_reports(text_to_speech))
window.bind_all("<Escape>", lambda e: exit_application())

# Modern Header Section
header_frame = tk.Frame(window, bg=BG_GRADIENT_START, height=100)
header_frame.pack(fill=X, pady=10)

# Logo and title container
title_container = tk.Frame(header_frame, bg=BG_PANEL, relief=FLAT, bd=0)
title_container.pack(pady=10)

# Logo
try:
    logo = Image.open("UI_Image/0001.png")
    logo = logo.resize((60, 60), Image.LANCZOS)
    logo1 = ImageTk.PhotoImage(logo)
    logo_label = tk.Label(title_container, image=logo1, bg=BG_PANEL)
    logo_label.image = logo1
    logo_label.pack(side=LEFT, padx=20, pady=20)
except:
    pass

# Main title with modern typography
title_frame = tk.Frame(title_container, bg=BG_PANEL)
title_frame.pack(side=LEFT, padx=20, pady=20)

main_title = tk.Label(
    title_frame,
    text="CLASS VISION",
    bg=BG_PANEL,
    fg=FG_PRIMARY,
    font=("Segoe UI", 32, "bold")
)
main_title.pack()

subtitle = tk.Label(
    title_frame,
    text="Smart Attendance Management System",
    bg=BG_PANEL,
    fg=FG_ACCENT,
    font=("Segoe UI", 14, "italic")
)
subtitle.pack()

# Welcome message with animation effect
welcome_frame = tk.Frame(window, bg=BG_GRADIENT_START)
welcome_frame.pack(pady=8)

welcome_label = tk.Label(
    welcome_frame,
    text="🎓 Revolutionizing Attendance with AI-Powered Face Recognition 🎓",
    bg=BG_GRADIENT_START,
    fg=FG_SECONDARY,
    font=("Segoe UI", 18, "bold")
)
welcome_label.pack()

# Main content area with SCROLLING SUPPORT
# Create a canvas with scrollbar for the main content
main_outer_frame = tk.Frame(window, bg=BG_GRADIENT_START)
main_outer_frame.pack(fill=BOTH, expand=True, padx=20, pady=10)

main_canvas = tk.Canvas(main_outer_frame, bg=BG_GRADIENT_START, highlightthickness=0, bd=0)
scrollbar = ttk.Scrollbar(main_outer_frame, orient="vertical", command=main_canvas.yview)
content_frame = tk.Frame(main_canvas, bg=BG_GRADIENT_START)

content_frame.bind(
    "<Configure>",
    lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
)

main_canvas.create_window((0, 0), window=content_frame, anchor="nw")
main_canvas.configure(yscrollcommand=scrollbar.set)

# Enable scrolling with mouse wheel
def _on_mousewheel(event):
    main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

main_canvas.bind_all("<MouseWheel>", _on_mousewheel)

main_canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# Create modern cards for each function with UNIFORM SIZING (ALL IN ONE ROW)
CARD_WIDTH = 270
CARD_HEIGHT = 260

# Container frame for cards with proper alignment - SINGLE ROW
cards_container = tk.Frame(content_frame, bg=BG_GRADIENT_START)
cards_container.pack(fill=BOTH, expand=True, pady=20)

# All cards in one row
cards_row = tk.Frame(cards_container, bg=BG_GRADIENT_START)
cards_row.pack(fill=BOTH, expand=True, pady=10)

card1, content1 = create_card_frame(cards_row, 50, 50, CARD_WIDTH, CARD_HEIGHT, "👤 Student Registration", "UI_Image/register.png")
card2, content2 = create_card_frame(cards_row, 450, 50, CARD_WIDTH, CARD_HEIGHT, "📊 Take Attendance", "UI_Image/attendance.png")
card3, content3 = create_card_frame(cards_row, 850, 50, CARD_WIDTH, CARD_HEIGHT, "📈 View Reports", "UI_Image/verifyy.png")
card4, content4 = create_card_frame(cards_row, 50, 380, CARD_WIDTH, CARD_HEIGHT, "📅 Past Reports", "UI_Image/verifyy.png")

# Add descriptions to cards with REDUCED SIZE for compact layout
desc1 = tk.Label(
    content1,
    text="Register new students by\ncapturing their facial features.\nSecure enrollment process.",
    bg=BG_CARD,
    fg=FG_SECONDARY,
    font=("Segoe UI", 9),
    justify=CENTER
)
desc1.pack(pady=8)

desc2 = tk.Label(
    content2,
    text="Automated attendance marking\nusing face recognition.\nReal-time processing.",
    bg=BG_CARD,
    fg=FG_SECONDARY,
    font=("Segoe UI", 9),
    justify=CENTER
)
desc2.pack(pady=8)

desc3 = tk.Label(
    content3,
    text="Comprehensive attendance\nreports and analytics.\nTrack participation trends.",
    bg=BG_CARD,
    fg=FG_SECONDARY,
    font=("Segoe UI", 9),
    justify=CENTER
)
desc3.pack(pady=8)

desc4 = tk.Label(
    content4,
    text="Access historical attendance\nrecords by date with\ncheckpoint details.",
    bg=BG_CARD,
    fg=FG_SECONDARY,
    font=("Segoe UI", 9),
    justify=CENTER
)
desc4.pack(pady=8)

# Background gradient already created above


def err_screen():
    # error message for name and no
    def del_sc1():
        sc1.destroy()

    sc1 = tk.Tk()
    sc1.geometry("400x110")
    sc1.iconbitmap("AMS.ico")
    sc1.title("Warning!!")
    sc1.configure(background=BG_DARK)
    sc1.resizable(0, 0)
    tk.Label(
        sc1,
        text="Enrollment & Name required!!!",
        fg=FG_PRIMARY,
        bg=BG_DARK,
        font=("Verdana", 16, "bold"),
    ).pack()
    ok_btn = tk.Button(
        sc1,
        text="OK",
        command=del_sc1,
        width=9,
        height=1,
        font=("Verdana", 16, "bold"),
    )
    style_button(ok_btn)
    ok_btn.place(x=110, y=50)


def testVal(inStr, acttyp):
    if acttyp == "1":  # insert
        if not inStr.isdigit():
            return False
    return True


def TakeImageUI():
    ImageUI = Tk()
    ImageUI.title("Student Registration - CLASS VISION")
    ImageUI.geometry("900x650")
    ImageUI.configure(background=BG_GRADIENT_START)
    ImageUI.resizable(0, 0)

    # Bring window to front and focus
    try:
        ImageUI.lift()
        ImageUI.attributes("-topmost", True)
        ImageUI.after(200, lambda: ImageUI.attributes("-topmost", False))
        ImageUI.focus_force()
    except Exception:
        pass
    
    # Create gradient background (pack first so other widgets appear on top)
    # Gradient disabled to avoid layering issues that can hide widgets
    # gradient_canvas = create_gradient_frame(ImageUI, 900, 650, BG_GRADIENT_START, BG_GRADIENT_END)
    # gradient_canvas.place(x=0, y=0, relwidth=1, relheight=1)
    
    try:
        ImageUI.iconbitmap("AMS.ico")
    except:
        pass

    # Modern header
    header_frame = tk.Frame(ImageUI, bg=BG_PANEL, height=80)
    header_frame.pack(fill=X, padx=20, pady=20)
    header_frame.pack_propagate(False)

    # Header content
    header_title = tk.Label(
        header_frame,
        text="👤 Student Registration Portal",
        bg=BG_PANEL,
        fg=FG_PRIMARY,
        font=("Segoe UI", 24, "bold")
    )
    header_title.pack(pady=20)

    # Main content frame
    main_frame = tk.Frame(ImageUI, bg=BG_GRADIENT_START)
    main_frame.pack(fill=BOTH, expand=True, padx=40, pady=20)

    # Background gradient already created above

    # Registration form card
    form_card = tk.Frame(main_frame, bg=BG_CARD, relief=FLAT, bd=0)
    # reduced outer padding so the form fits better on smaller screens
    form_card.pack(pady=10, padx=10, fill=BOTH, expand=True)

    # Form title
    form_title = tk.Label(
        form_card,
        text="Enter Student Details",
        bg=BG_CARD,
        fg=FG_ACCENT,
        font=("Segoe UI", 18, "bold")
    )
    form_title.pack(pady=20)

    # Form fields container
    fields_frame = tk.Frame(form_card, bg=BG_CARD)
    # reduced inner spacing for a more compact form
    fields_frame.pack(pady=10)

    # Enrollment field
    enrollment_frame = tk.Frame(fields_frame, bg=BG_CARD)
    enrollment_frame.pack(pady=8, padx=20, fill=X)

    lbl1 = tk.Label(
        enrollment_frame,
        text="📝 Enrollment Number:",
        bg=BG_CARD,
        fg=FG_SECONDARY,
        font=("Segoe UI", 14, "bold")
    )
    lbl1.pack(anchor=W, pady=(0, 5))

    txt1 = tk.Entry(
        enrollment_frame,
        bd=2,
        validate="key",
        bg=BG_PANEL,
        fg=FG_PRIMARY,
        relief=SOLID,
        font=("Segoe UI", 16),
        insertbackground=FG_PRIMARY,
        highlightthickness=1,
        highlightcolor=FG_PRIMARY
    )
    txt1.pack(fill=X, ipady=8)
    txt1["validatecommand"] = (txt1.register(testVal), "%P", "%d")

    # Name field
    name_frame = tk.Frame(fields_frame, bg=BG_CARD)
    name_frame.pack(pady=8, padx=20, fill=X)

    lbl2 = tk.Label(
        name_frame,
        text="👤 Student Name:",
        bg=BG_CARD,
        fg=FG_SECONDARY,
        font=("Segoe UI", 14, "bold")
    )
    lbl2.pack(anchor=W, pady=(0, 5))

    txt2 = tk.Entry(
        name_frame,
        bd=2,
        bg=BG_PANEL,
        fg=FG_PRIMARY,
        relief=SOLID,
        font=("Segoe UI", 16),
        insertbackground=FG_PRIMARY,
        highlightthickness=1,
        highlightcolor=FG_PRIMARY
    )
    txt2.pack(fill=X, ipady=8)


    # Status area
    message = tk.Label(
        form_card,
        text="Ready to take image",
        bg=BG_PANEL,
        fg=FG_ACCENT,
        relief=FLAT,
        font=("Segoe UI", 12, "bold"),
        padx=10,
        pady=10
    )
    message.pack(pady=10)

    # Actions
    def take_image():
        l1 = txt1.get()
        l2 = txt2.get()
        takeImage.TakeImage(
            l1,
            l2,
            haarcasecade_path,
            trainimage_path,
            message,
            err_screen,
            text_to_speech,
        )
        txt1.delete(0, "end")
        txt2.delete(0, "end")

    def train_image():
        trainImage.TrainImage(
            haarcasecade_path,
            trainimage_path,
            trainimagelabel_path,
            message,
            text_to_speech,
        )

    # Button frame below fields
    button_frame = tk.Frame(form_card, bg=BG_CARD)
    button_frame.pack(pady=10)

    takeImg = tk.Button(
        button_frame,
        text="📸 Capture Image",
        command=take_image,
        font=("Segoe UI", 14, "bold"),
        height=6,
        width=16,
    )
    style_button(takeImg, bg=BTN_SUCCESS, hover_bg=BTN_SUCCESS_HOVER)
    takeImg.pack(side=LEFT, padx=10)

    trainImg = tk.Button(
        button_frame,
        text="🧠 Train Model",
        command=train_image,
        font=("Segoe UI", 14, "bold"),
        height=6,
        width=16,
    )
    style_button(trainImg, bg=BTN_PRIMARY, hover_bg=BTN_PRIMARY_HOVER)
    trainImg.pack(side=LEFT, padx=10)

    # Instructions
    instructions = tk.Label(
        form_card,
        text="💡 Instructions: Enter enrollment number and name, then click 'Capture Image' to take photos.\nAfter capturing, click 'Train Model' to update the recognition system.",
        bg=BG_CARD,
        fg=FG_SECONDARY,
        font=("Segoe UI", 10, "italic"),
        justify=CENTER
    )
    instructions.pack(pady=20)

    # Keyboard shortcuts for this window
    ImageUI.bind_all("<Control-c>", lambda e: take_image())
    ImageUI.bind_all("<Control-t>", lambda e: train_image())

# Action buttons for cards
def register_student():
    animate_button_click(btn_register, BTN_SUCCESS, BTN_SUCCESS_HOVER)
    TakeImageUI()

def automatic_attedance():
    try:
        animate_button_click(btn_attend, BTN_PRIMARY, BTN_PRIMARY_HOVER)
        # New behavior: three scan instances with gaps.
        # A student is marked present (checkpoint ticked) only if
        # they are recognized in at least 2 out of 3 instances.
        try:
            # Ensure recognizer API is available
            if not hasattr(cv2, "face") or not hasattr(cv2.face, "LBPHFaceRecognizer_create"):
                messagebox.showerror(
                    "Recognizer Missing",
                    "Face recognizer (LBPH) not available. Install opencv-contrib-python to enable ID-based attendance."
                )
                return

            recognizer = cv2.face.LBPHFaceRecognizer_create()
            if os.path.exists(trainimagelabel_path):
                try:
                    recognizer.read(trainimagelabel_path)
                except Exception:
                    messagebox.showerror("Model Error", "Failed to load trained model. Please retrain.")
                    return
            else:
                messagebox.showerror("Model Missing", "No trained model found. Please train first.")
                return

            # Load Haarcascade and student mapping
            face_cascade = cv2.CascadeClassifier(haarcasecade_path)
            if face_cascade.empty():
                messagebox.showerror("Model Error", "Failed to load face cascade for detection.")
                return

            try:
                df_students = pd.read_csv(studentdetail_path, header=None, names=["Enrollment", "Name"], dtype=str)
                df_students["Enrollment"] = df_students["Enrollment"].astype(str).str.replace(r"\D+", "", regex=True)
                df_students["Enrollment"] = pd.to_numeric(df_students["Enrollment"], errors="coerce")
                df_students = df_students.dropna(subset=["Enrollment"])
                df_students["Enrollment"] = df_students["Enrollment"].astype(int)
                df_students = df_students.dropna(subset=["Name"]).drop_duplicates(subset=["Enrollment"], keep="last")
                id_to_name = dict(zip(df_students["Enrollment"].astype(int), df_students["Name"]))
            except Exception:
                id_to_name = {}

            # Open camera
            cam = None
            for src, api in [(0, cv2.CAP_DSHOW), (0, None), (1, cv2.CAP_DSHOW), (1, None)]:
                tmp = cv2.VideoCapture(src, api) if api is not None else cv2.VideoCapture(src)
                if tmp.isOpened():
                    cam = tmp
                    break
            if cam is None or not cam.isOpened():
                messagebox.showerror("Camera Error", "Unable to access camera. Please connect a camera.")
                return

            window_name = "Mark Attendance - Recognizing (3-instance mode, ESC to stop)"
            total_instances = 3
            scan_duration = 5   # seconds per scan
            gap_duration = 10   # seconds between scans
            early_exit = False

            # Track in how many instances each ID was seen
            instance_counts = {}   # enrollment_id -> count of instances where detected

            for instance in range(1, total_instances + 1):
                instance_end = datetime.datetime.now() + datetime.timedelta(seconds=scan_duration)
                recognized_in_this_instance = set()

                while datetime.datetime.now() < instance_end:
                    ret, frame = cam.read()
                    if not ret or frame is None:
                        continue

                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5)

                    for (x, y, w, h) in faces:
                        try:
                            Id, conf = recognizer.predict(gray[y:y + h, x:x + w])
                        except Exception:
                            Id, conf = (None, 999)

                        if conf < 45 and Id is not None:
                            name = id_to_name.get(int(Id), "Unknown")
                            label = f"{Id}-{name}"
                            recognized_in_this_instance.add(int(Id))
                            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                            cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
                        else:
                            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 25, 255), 2)
                            cv2.putText(frame, "Unknown", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 25, 255), 2)

                    # Overlay instance label
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

                    cv2.imshow(window_name, frame)
                    key = cv2.waitKey(30) & 0xFF
                    if key == 27:  # ESC
                        early_exit = True
                        break

                # Update counts for this instance
                for rid in recognized_in_this_instance:
                    instance_counts[rid] = instance_counts.get(rid, 0) + 1

                if early_exit:
                    break

                # Show gap countdown between instances
                if instance < total_instances:
                    for remaining in range(gap_duration, 0, -1):
                        ret, frame = cam.read()
                        if not ret or frame is None:
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
                            0.8,
                            (255, 255, 255),
                            2,
                            cv2.LINE_AA,
                        )

                        cv2.imshow(window_name, frame)
                        key = cv2.waitKey(1000) & 0xFF  # 1 second per step
                        if key == 27:  # ESC
                            early_exit = True
                            break

                    if early_exit:
                        break

            cam.release()
            cv2.destroyAllWindows()

            if early_exit and not instance_counts:
                messagebox.showinfo("Scanning Stopped", "Scanning stopped early by user (ESC). No attendance was marked.")
                return

            # Decide final attendance: IDs seen in at least 2 instances
            MIN_INSTANCES = 2
            final_present = {rid for rid, cnt in instance_counts.items() if cnt >= MIN_INSTANCES}

            if not final_present:
                if early_exit:
                    messagebox.showinfo("No Attendance Marked", "Scanning stopped early and no student met the 2-of-3 rule.")
                else:
                    messagebox.showinfo("No Attendance Marked", "No student was recognized in at least 2 of 3 instances.")
                return

            # Mark attendance via checkpoint system for final_present IDs
            try:
                date = datetime.datetime.now().strftime("%Y-%m-%d")

                # Build enrollment -> name mapping for present IDs
                unique_recognized = {}
                for rid in final_present:
                    name = id_to_name.get(int(rid), "Unknown")
                    unique_recognized[int(rid)] = name

                marked_count = 0
                for enrollment_id, student_name in unique_recognized.items():
                    try:
                        checkpoint_num = checkpoint_attendance.get_next_checkpoint(int(enrollment_id), date)
                        if checkpoint_num is not None:
                            checkpoint_attendance.add_student_checkpoint(
                                int(enrollment_id),
                                str(student_name),
                                checkpoint_num,
                                date
                            )
                            marked_count += 1
                    except Exception as e:
                        messagebox.showwarning(
                            "Error Marking Attendance",
                            f"Failed to mark attendance for {enrollment_id}-{student_name}: {str(e)}"
                        )

                # Optional: legacy report CSV with ticks for present students
                if marked_count > 0:
                    try:
                        reports_dir = os.path.join("Attendance", "Reports")
                        os.makedirs(reports_dir, exist_ok=True)
                        ts = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

                        if isinstance(df_students, pd.DataFrame) and not df_students.empty:
                            df_all = df_students[["Enrollment", "Name"]].drop_duplicates(subset=["Enrollment"]).copy()
                            df_all["Enrollment"] = df_all["Enrollment"].astype(int)
                            df_all[date] = ""
                            present_ids = set(unique_recognized.keys())
                            df_all.loc[df_all["Enrollment"].isin(present_ids), date] = 1
                            filename = os.path.join(reports_dir, f"Reports_{ts}.csv")
                            df_all.to_csv(filename, index=False)
                    except Exception:
                        pass

                messagebox.showinfo(
                    "Attendance Marked",
                    f"Marked attendance for {marked_count} student(s).\n"
                    f"Rule: present if recognized in at least 2 of 3 instances."
                )
            except Exception as ex_save:
                messagebox.showerror("Save Error", f"Failed to save attendance: {ex_save}")

        except Exception as ex:
            messagebox.showerror("Scanning Error", f"Error during scanning: {ex}")
            try:
                cam.release()
            except Exception:
                pass
            try:
                cv2.destroyAllWindows()
            except Exception:
                pass
    except Exception as e:
        messagebox.showerror("Attendance Error", f"Failed to mark attendance: {e}")

def view_attendance():
    try:
        animate_button_click(btn_view, BTN_WARNING, BTN_WARNING_HOVER)
        show_attendance.subjectchoose(text_to_speech)
    except Exception as e:
        messagebox.showerror("View Reports Error", f"Failed to view reports: {e}")

# Modern action buttons - REDUCED SIZE
btn_register = tk.Button(
    content1,
    text="🚀 Start Registration",
    command=register_student,
    font=("Segoe UI", 10, "bold"),
    height=1,
    width=18,
)
style_button(btn_register, bg=BTN_SUCCESS, hover_bg=BTN_SUCCESS_HOVER)
btn_register.pack(pady=5)

btn_attend = tk.Button(
    content2,
    text="📊 Mark Attendance",
    command=automatic_attedance,
    font=("Segoe UI", 10, "bold"),
    height=1,
    width=18,
)
style_button(btn_attend, bg=BTN_PRIMARY, hover_bg=BTN_PRIMARY_HOVER)
btn_attend.pack(pady=5)

btn_view = tk.Button(
    content3,
    text="📈 View Reports",
    command=view_attendance,
    font=("Segoe UI", 10, "bold"),
    height=1,
    width=18,
)
style_button(btn_view, bg=BTN_WARNING, hover_bg=BTN_WARNING_HOVER)
btn_view.pack(pady=5)

btn_past2 = tk.Button(
    content4,
    text="📅 Attendance Details",
    command=view_attendance,
    font=("Segoe UI", 10, "bold"),
    height=1,
    width=18,
)
style_button(btn_past2, bg=BTN_PRIMARY, hover_bg=BTN_PRIMARY_HOVER)
btn_past2.pack(pady=5)

# Bottom section with additional features (INSIDE SCROLLABLE CONTENT)
bottom_frame = tk.Frame(content_frame, bg=BG_GRADIENT_START, height=100)
bottom_frame.pack(side=BOTTOM, fill=X, padx=0, pady=20)

# Statistics or info panel
info_frame = tk.Frame(bottom_frame, bg=BG_PANEL, relief=FLAT, bd=0)
info_frame.pack(fill=X, pady=10)

info_label = tk.Label(
    info_frame,
    text="🔒 Secure • 🚀 Fast • 🎯 Accurate • 📊 Comprehensive Analytics",
    bg=BG_PANEL,
    fg=FG_ACCENT,
    font=("Segoe UI", 12, "bold")
)
info_label.pack(pady=15)

# Exit button frame
exit_frame = tk.Frame(bottom_frame, bg=BG_GRADIENT_START)
exit_frame.pack(pady=10)

def exit_application():
    animate_button_click(btn_exit, BTN_DANGER, BTN_DANGER_HOVER)
    window.after(200, quit)

btn_exit = tk.Button(
    exit_frame,
    text="🚪 Exit Application",
    command=exit_application,
    font=("Segoe UI", 12, "bold"),
    height=2,
    width=20,
)
style_button(btn_exit, bg=BTN_DANGER, hover_bg=BTN_DANGER_HOVER)
btn_exit.pack()


window.mainloop()
