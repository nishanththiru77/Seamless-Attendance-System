def automatic_attendance():
    animate_button_click(btn_attend, BTN_PRIMARY, BTN_PRIMARY_HOVER)
    automaticAttedance.subjectChoose(text_to_speech)
def exit_application():
    animate_button_click(btn_exit, BTN_DANGER, BTN_DANGER_HOVER)
    window.after(200, window.quit)
import tkinter as tk
from tkinter import *
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
import takeImage
import trainImage
import automaticAttedance


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
    container.pack(side=LEFT, padx=20, pady=10)

    # Main card frame
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
window.geometry("1400x800")
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
window.bind_all("<Escape>", lambda e: exit_application())

# Modern Header Section
header_frame = tk.Frame(window, bg=BG_GRADIENT_START, height=120)
header_frame.pack(fill=X, pady=20)

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
welcome_frame.pack(pady=20)

welcome_label = tk.Label(
    welcome_frame,
    text="🎓 Revolutionizing Attendance with AI-Powered Face Recognition 🎓",
    bg=BG_GRADIENT_START,
    fg=FG_SECONDARY,
    font=("Segoe UI", 18, "bold")
)
welcome_label.pack()

# Main content area with cards
content_frame = tk.Frame(window, bg=BG_GRADIENT_START)
content_frame.pack(fill=BOTH, expand=True, padx=40, pady=20)

# Create modern cards for each function
card1, content1 = create_card_frame(content_frame, 50, 50, 350, 300, "👤 Student Registration", "UI_Image/register.png")
card2, content2 = create_card_frame(content_frame, 450, 50, 350, 300, "📊 Take Attendance", "UI_Image/attendance.png")
card3, content3 = create_card_frame(content_frame, 850, 50, 350, 300, "📈 View Reports", "UI_Image/verifyy.png")

# Add descriptions to cards
desc1 = tk.Label(
    content1,
    text="Register new students by capturing\ntheir facial features for recognition.\nSecure and efficient enrollment process.",
    bg=BG_CARD,
    fg=FG_SECONDARY,
    font=("Segoe UI", 11),
    justify=CENTER
)
desc1.pack(pady=20)

desc2 = tk.Label(
    content2,
    text="Automated attendance marking using\nadvanced face recognition technology.\nReal-time processing and accuracy.",
    bg=BG_CARD,
    fg=FG_SECONDARY,
    font=("Segoe UI", 11),
    justify=CENTER
)
desc2.pack(pady=20)

desc3 = tk.Label(
    content3,
    text="Comprehensive attendance reports\nand analytics for better insights.\nTrack student participation trends.",
    bg=BG_CARD,
    fg=FG_SECONDARY,
    font=("Segoe UI", 11),
    justify=CENTER
)
desc3.pack(pady=20)

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
    form_card.pack(pady=20, padx=20, fill=BOTH, expand=True)

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
    fields_frame.pack(pady=20)

    # Enrollment field
    enrollment_frame = tk.Frame(fields_frame, bg=BG_CARD)
    enrollment_frame.pack(pady=15, padx=40, fill=X)

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
    name_frame.pack(pady=15, padx=40, fill=X)

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

    # Add Mark Attendance button
    def mark_attendance():
        automaticAttedance.subjectChoose(text_to_speech)

    markAttendBtn = tk.Button(
        button_frame,
        text="✅ Mark Attendance",
        command=mark_attendance,
        font=("Segoe UI", 14, "bold"),
        height=6,
        width=16,
    )
    style_button(markAttendBtn, bg=BTN_WARNING, hover_bg=BTN_WARNING_HOVER)
    markAttendBtn.pack(side=LEFT, padx=10)

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
        automaticAttedance.subjectChoose(text_to_speech)
    except Exception as e:
        messagebox.showerror("Attendance Error", f"Failed to mark attendance: {e}")

def view_attendance():
    try:
        animate_button_click(btn_view, BTN_WARNING, BTN_WARNING_HOVER)
        show_attendance.subjectchoose(text_to_speech)
    except Exception as e:
        messagebox.showerror("View Reports Error", f"Failed to view reports: {e}")

# Modern action buttons
btn_register = tk.Button(
    content1,
    text="🚀 Start Registration",
    command=register_student,
    font=("Segoe UI", 12, "bold"),
    height=2,
    width=20,
)
style_button(btn_register, bg=BTN_SUCCESS, hover_bg=BTN_SUCCESS_HOVER)
btn_register.pack(pady=10)

btn_attend = tk.Button(
    content2,
    text="📊 Mark Attendance",
    command=automatic_attedance,
    font=("Segoe UI", 12, "bold"),
    height=2,
    width=20,
)
style_button(btn_attend, bg=BTN_PRIMARY, hover_bg=BTN_PRIMARY_HOVER)
btn_attend.pack(pady=10)

btn_view = tk.Button(
    content3,
    text="📈 View Reports",
    command=view_attendance,
    font=("Segoe UI", 12, "bold"),
    height=2,
    width=20,
)
style_button(btn_view, bg=BTN_WARNING, hover_bg=BTN_WARNING_HOVER)
btn_view.pack(pady=10)

# Redundant but reliable action bar to ensure buttons are always visible
action_bar = tk.Frame(window, bg=BG_PANEL)
action_bar.pack(fill=X, padx=40, pady=10)

btn_register_top = tk.Button(
    action_bar,
    text="👤 Register",
    command=register_student,
    font=("Segoe UI", 12, "bold"),
    height=2,
    width=16,
)
style_button(btn_register_top, bg=BTN_SUCCESS, hover_bg=BTN_SUCCESS_HOVER)
btn_register_top.pack(side=LEFT, padx=10, pady=10)

btn_attend_top = tk.Button(
    action_bar,
    text="📊 Attendance",
    command=automatic_attedance,
    font=("Segoe UI", 12, "bold"),
    height=2,
    width=16,
)
style_button(btn_attend_top, bg=BTN_PRIMARY, hover_bg=BTN_PRIMARY_HOVER)
btn_attend_top.pack(side=LEFT, padx=10, pady=10)

btn_view_top = tk.Button(
    action_bar,
    text="📈 Reports",
    command=view_attendance,
    font=("Segoe UI", 12, "bold"),
    height=2,
    width=16,
)
style_button(btn_view_top, bg=BTN_WARNING, hover_bg=BTN_WARNING_HOVER)
btn_view_top.pack(side=LEFT, padx=10, pady=10)

# Bottom section with additional features
bottom_frame = tk.Frame(window, bg=BG_GRADIENT_START, height=100)
bottom_frame.pack(side=BOTTOM, fill=X, padx=40, pady=20)

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

# Exit button
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
