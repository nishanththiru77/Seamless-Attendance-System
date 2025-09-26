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
import tkinter.font as font
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


# Theme constants
BG_DARK = "#1c1c1c"
BG_PANEL = "#2b2b2b"
FG_PRIMARY = "#ffde59"  # warm yellow
BTN_BG = "#2e86de"
BTN_BG_HOVER = "#1b4f72"
BTN_FG = "#ffffff"


def style_button(btn, bg=BTN_BG, hover_bg=BTN_BG_HOVER, fg=BTN_FG):
    btn.configure(
        bg=bg,
        fg=fg,
        activebackground=hover_bg,
        activeforeground=fg,
        bd=0,
        relief=RIDGE,
        highlightthickness=0,
        cursor="hand2",
    )

    def on_enter(_):
        btn.configure(bg=hover_bg)

    def on_leave(_):
        btn.configure(bg=bg)

    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)


haarcasecade_path = "haarcascade_frontalface_default.xml"
trainimagelabel_path = (
    "./TrainingImageLabel/Trainner.yml"
)
# FIX: Use relative project path (previously was "/TrainingImage" pointing to drive root)
trainimage_path = "./TrainingImage"
os.makedirs(trainimage_path, exist_ok=True)

studentdetail_path = (
    "./StudentDetails/studentdetails.csv"
)
attendance_path = "Attendance"

window = Tk()
window.title("Face Recognizer")
window.geometry("1280x720")
dialog_title = "QUIT"
dialog_text = "Are you sure want to close?"
window.configure(background=BG_DARK)
window.resizable(True, True)

# Header bar
logo = Image.open("UI_Image/0001.png")
logo = logo.resize((50, 47), Image.LANCZOS)
logo1 = ImageTk.PhotoImage(logo)

titl = tk.Label(window, bg=BG_DARK, relief=RIDGE, bd=10, font=("Verdana", 30, "bold"))
titl.pack(fill=X)

l1 = tk.Label(window, image=logo1, bg=BG_DARK)
l1.place(x=470, y=10)

header = tk.Label(
    window, text="CLASS VISION", bg=BG_DARK, fg=FG_PRIMARY, font=("Verdana", 27, "bold"),
)
header.place(x=525, y=12)

welcome = tk.Label(
    window,
    text="Welcome to CLASS VISION",
    bg=BG_DARK,
    fg=FG_PRIMARY,
    bd=10,
    font=("Verdana", 35, "bold"),
)
welcome.pack()

# Illustrations
ri = Image.open("UI_Image/register.png")
r = ImageTk.PhotoImage(ri)
label1 = Label(window, image=r, bg=BG_DARK)
label1.image = r
label1.place(x=100, y=270)

ai = Image.open("UI_Image/attendance.png")
a = ImageTk.PhotoImage(ai)
label2 = Label(window, image=a, bg=BG_DARK)
label2.image = a
label2.place(x=980, y=270)

vi = Image.open("UI_Image/verifyy.png")
v = ImageTk.PhotoImage(vi)
label3 = Label(window, image=v, bg=BG_DARK)
label3.image = v
label3.place(x=600, y=270)


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
    ImageUI.title("Take Student Image..")
    ImageUI.geometry("780x520")
    ImageUI.configure(background=BG_DARK)
    ImageUI.resizable(0, 0)

    titl = tk.Label(ImageUI, bg=BG_DARK, relief=RIDGE, bd=10, font=("Verdana", 30, "bold"))
    titl.pack(fill=X)

    # Title
    heading = tk.Label(
        ImageUI, text="Register Your Face", bg=BG_DARK, fg="#6be675", font=("Verdana", 30, "bold"),
    )
    heading.place(x=230, y=12)

    # Subheading
    sub = tk.Label(
        ImageUI,
        text="Enter the details",
        bg=BG_DARK,
        fg=FG_PRIMARY,
        bd=10,
        font=("Verdana", 24, "bold"),
    )
    sub.place(x=260, y=75)

    # Enrollment
    lbl1 = tk.Label(
        ImageUI,
        text="Enrollment No",
        width=12,
        height=2,
        bg=BG_DARK,
        fg=FG_PRIMARY,
        bd=5,
        relief=RIDGE,
        font=("Verdana", 14),
    )
    lbl1.place(x=80, y=140)
    txt1 = tk.Entry(
        ImageUI,
        width=20,
        bd=0,
        validate="key",
        bg=BG_PANEL,
        fg=FG_PRIMARY,
        relief=FLAT,
        font=("Verdana", 18, "bold"),
        insertbackground=FG_PRIMARY,
    )
    txt1.place(x=250, y=145, height=40)
    txt1["validatecommand"] = (txt1.register(testVal), "%P", "%d")

    # Name
    lbl2 = tk.Label(
        ImageUI,
        text="Name",
        width=12,
        height=2,
        bg=BG_DARK,
        fg=FG_PRIMARY,
        bd=5,
        relief=RIDGE,
        font=("Verdana", 14),
    )
    lbl2.place(x=80, y=200)
    txt2 = tk.Entry(
        ImageUI,
        width=20,
        bd=0,
        bg=BG_PANEL,
        fg=FG_PRIMARY,
        relief=FLAT,
        font=("Verdana", 18, "bold"),
        insertbackground=FG_PRIMARY,
    )
    txt2.place(x=250, y=205, height=40)

    lbl3 = tk.Label(
        ImageUI,
        text="Notification",
        width=12,
        height=2,
        bg=BG_DARK,
        fg=FG_PRIMARY,
        bd=5,
        relief=RIDGE,
        font=("Verdana", 14),
    )
    lbl3.place(x=80, y=260)

    message = tk.Label(
        ImageUI,
        text="",
        width=34,
        height=2,
        bd=0,
        bg=BG_PANEL,
        fg=FG_PRIMARY,
        relief=FLAT,
        font=("Verdana", 14, "bold"),
    )
    message.place(x=250, y=260)

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

    takeImg = tk.Button(
        ImageUI,
        text="Take Image",
        command=take_image,
        font=("Verdana", 18, "bold"),
        height=2,
        width=14,
    )
    style_button(takeImg, bg="#27ae60", hover_bg="#1e8449")
    takeImg.place(x=100, y=350)

    def train_image():
        trainImage.TrainImage(
            haarcasecade_path,
            trainimage_path,
            trainimagelabel_path,
            message,
            text_to_speech,
        )

    trainImg = tk.Button(
        ImageUI,
        text="Train Image",
        command=train_image,
        font=("Verdana", 18, "bold"),
        height=2,
        width=14,
    )
    style_button(trainImg)
    trainImg.place(x=390, y=350)


# Main actions
btn_register = tk.Button(
    window,
    text="Register a new student",
    command=TakeImageUI,
    font=("Verdana", 16, "bold"),
    height=2,
    width=20,
)
style_button(btn_register)
btn_register.place(x=100, y=520)


def automatic_attedance():
    automaticAttedance.subjectChoose(text_to_speech)


btn_attend = tk.Button(
    window,
    text="Take Attendance",
    command=automatic_attedance,
    font=("Verdana", 16, "bold"),
    height=2,
    width=20,
)
style_button(btn_attend)
btn_attend.place(x=600, y=520)


def view_attendance():
    show_attendance.subjectchoose(text_to_speech)


btn_view = tk.Button(
    window,
    text="View Attendance",
    command=view_attendance,
    font=("Verdana", 16, "bold"),
    height=2,
    width=20,
)
style_button(btn_view)
btn_view.place(x=1000, y=520)

btn_exit = tk.Button(
    window,
    text="EXIT",
    command=quit,
    font=("Verdana", 16, "bold"),
    height=2,
    width=20,
)
style_button(btn_exit, bg="#e74c3c", hover_bg="#922b21")
btn_exit.place(x=600, y=660)


window.mainloop()
