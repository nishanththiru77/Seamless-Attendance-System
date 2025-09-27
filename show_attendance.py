import pandas as pd
from glob import glob
import os
import tkinter
import csv
import tkinter as tk
from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk

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
    """Create a gradient background canvas. Caller should place() and lower() it."""
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

def subjectchoose(text_to_speech):
    def calculate_attendance():
        Subject = tx.get()
        if Subject=="":
            t='Please enter the subject name.'
            text_to_speech(t)
            return

        csv_path = f"Attendance\\{Subject}\\attendance.csv"
        if os.path.exists(csv_path):
            # Display stored attendance report
            display_attendance(Subject, csv_path)
            return

        folder = os.path.join("Attendance", Subject)
        filenames = sorted(glob(os.path.join(folder, "*.csv")))
        # Exclude aggregated report itself
        filenames = [f for f in filenames if os.path.basename(f).lower() != "attendance.csv"]
        if not filenames:
            t = "No attendance files found for this subject yet."
            text_to_speech(t)
            return

        # Load each session, enforce consistent dtypes
        df = []
        for f in filenames:
            dfi = pd.read_csv(f)
            if "Enrollment" in dfi.columns:
                dfi["Enrollment"] = pd.to_numeric(dfi["Enrollment"], errors="coerce").astype("Int64")
            if "Name" in dfi.columns:
                dfi["Name"] = dfi["Name"].astype(str)
            df.append(dfi)
        newdf = df[0]
        for i in range(1, len(df)):
            # Merge strictly on Enrollment and Name to avoid using date columns as keys
            newdf = newdf.merge(df[i], how="outer", on=["Enrollment", "Name"])
        newdf.fillna(0, inplace=True)

        # Ensure numeric for all session columns before computing averages
        if newdf.shape[1] > 2:
            for col in newdf.columns[2:]:
                newdf[col] = pd.to_numeric(newdf[col], errors="coerce").fillna(0)

        if newdf.shape[1] <= 2:
            newdf["Attendance"] = "0%"
        else:
            avg = (newdf.iloc[:, 2:].mean(axis=1) * 100).round().astype(int).astype(str) + '%'
            newdf["Attendance"] = avg
        newdf.to_csv(csv_path, index=False)

        # Modern attendance display window
        display_attendance(Subject, csv_path)

    def display_attendance(subject_name, csv_path):
        """Display attendance in a modern, attractive format"""
        root = tkinter.Toplevel()
        root.title(f"📊 Attendance Report - {subject_name}")
        root.geometry("1000x600")
        root.configure(background=BG_GRADIENT_START)
        
        try:
            root.iconbitmap("AMS.ico")
        except:
            pass

        # Create gradient background behind content
        bg = create_gradient_frame(root, 1000, 600, BG_GRADIENT_START, BG_GRADIENT_END)
        try:
            bg.place(x=0, y=0, relwidth=1, relheight=1)
            bg.lower()
        except Exception:
            pass

        # Header
        header_frame = tk.Frame(root, bg=BG_PANEL, height=80)
        header_frame.pack(fill=X, padx=20, pady=20)
        header_frame.pack_propagate(False)

        header_title = tk.Label(
            header_frame,
            text=f"📊 {subject_name} - Attendance Report",
            bg=BG_PANEL,
            fg=FG_PRIMARY,
            font=("Segoe UI", 20, "bold")
        )
        header_title.pack(pady=20)

        # Main content frame with scrollbar
        main_frame = tk.Frame(root, bg="transparent")
        main_frame.pack(fill=BOTH, expand=True, padx=20, pady=10)

        # Create scrollable frame
        canvas = tk.Canvas(main_frame, bg=BG_CARD, highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=BG_CARD)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Read and display CSV data
        try:
            with open(csv_path, 'r') as file:
                reader = csv.reader(file)
                data = list(reader)
                
                if data:
                    # Header row with modern styling
                    header_row = tk.Frame(scrollable_frame, bg=BG_PANEL, relief=FLAT, bd=2)
                    header_row.pack(fill=X, padx=10, pady=5)
                    
                    for col_idx, header in enumerate(data[0]):
                        header_label = tk.Label(
                            header_row,
                            text=header,
                            bg=BG_PANEL,
                            fg=FG_ACCENT,
                            font=("Segoe UI", 12, "bold"),
                            width=15,
                            height=2,
                            relief=FLAT,
                            bd=1
                        )
                        header_label.grid(row=0, column=col_idx, padx=2, pady=2, sticky="ew")
                    
                    # Data rows with alternating colors
                    for row_idx, row_data in enumerate(data[1:], 1):
                        row_bg = BG_CARD if row_idx % 2 == 0 else BG_DARK
                        data_row = tk.Frame(scrollable_frame, bg=row_bg, relief=FLAT, bd=1)
                        data_row.pack(fill=X, padx=10, pady=2)
                        
                        for col_idx, cell_data in enumerate(row_data):
                            # Color code attendance percentages
                            cell_fg = FG_SECONDARY
                            if col_idx == len(row_data) - 1 and '%' in str(cell_data):  # Attendance column
                                try:
                                    percentage = int(cell_data.replace('%', ''))
                                    if percentage >= 75:
                                        cell_fg = "#4ade80"  # Green
                                    elif percentage >= 50:
                                        cell_fg = "#fbbf24"  # Yellow
                                    else:
                                        cell_fg = "#f87171"  # Red
                                except:
                                    pass
                            
                            cell_label = tk.Label(
                                data_row,
                                text=cell_data,
                                bg=row_bg,
                                fg=cell_fg,
                                font=("Segoe UI", 11),
                                width=15,
                                height=1,
                                relief=FLAT
                            )
                            cell_label.grid(row=0, column=col_idx, padx=2, pady=2, sticky="ew")

        except Exception as e:
            error_label = tk.Label(
                scrollable_frame,
                text=f"Error loading attendance data: {str(e)}",
                bg=BG_CARD,
                fg="#f87171",
                font=("Segoe UI", 12),
                pady=20
            )
            error_label.pack()

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Footer with statistics
        footer_frame = tk.Frame(root, bg=BG_PANEL, height=60)
        footer_frame.pack(fill=X, padx=20, pady=10)
        footer_frame.pack_propagate(False)

        footer_text = tk.Label(
            footer_frame,
            text="💡 Green: ≥75% | Yellow: 50-74% | Red: <50% attendance",
            bg=BG_PANEL,
            fg=FG_ACCENT,
            font=("Segoe UI", 10, "italic")
        )
        footer_text.pack(pady=15)

    # Modern subject selection window
    subject = Toplevel()
    subject.title("📈 Attendance Reports - CLASS VISION")
    subject.geometry("700x450")
    subject.resizable(0, 0)
    subject.configure(background=BG_GRADIENT_START)
    
    try:
        subject.iconbitmap("AMS.ico")
    except:
        pass

    # Create gradient background behind content
    bg = create_gradient_frame(subject, 700, 450, BG_GRADIENT_START, BG_GRADIENT_END)
    try:
        bg.place(x=0, y=0, relwidth=1, relheight=1)
        bg.lower()
    except Exception:
        pass

    # Header
    header_frame = tk.Frame(subject, bg=BG_PANEL, height=80)
    header_frame.pack(fill=X, padx=20, pady=20)
    header_frame.pack_propagate(False)

    header_title = tk.Label(
        header_frame,
        text="📈 Attendance Reports",
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
        text="Enter the subject name to view attendance reports and analytics",
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

    # Enable Enter key to trigger report fetch and focus the input
    tx.focus_set()
    tx.bind('<Return>', lambda e: calculate_attendance())

    # Buttons frame
    buttons_frame = tk.Frame(content_card, bg=BG_CARD)
    buttons_frame.pack(pady=40)

    def open_folder():
        sub = tx.get()
        if sub == "":
            t="Please enter the subject name!!!"
            text_to_speech(t)
        else:
            try:
                os.startfile(f"Attendance\\{sub}")
            except:
                t = f"Folder for {sub} not found!"
                text_to_speech(t)

    # View Reports button
    view_btn = tk.Button(
        buttons_frame,
        text="📊 View Reports",
        command=calculate_attendance,
        font=("Segoe UI", 14, "bold"),
        height=2,
        width=15,
    )
    style_button(view_btn, bg=BTN_SUCCESS, hover_bg=BTN_SUCCESS_HOVER)
    view_btn.pack(side=LEFT, padx=15)

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

    # Tips section
    tips_frame = tk.Frame(content_card, bg=BG_PANEL, relief=FLAT, bd=2)
    tips_frame.pack(fill=X, padx=20, pady=20)

    tips_label = tk.Label(
        tips_frame,
        text="💡 Tips: Make sure attendance has been taken for the subject before viewing reports.\nReports show attendance percentage and detailed analytics.",
        bg=BG_PANEL,
        fg=FG_SECONDARY,
        font=("Segoe UI", 10, "italic"),
        justify=CENTER
    )
    tips_label.pack(pady=15)

    subject.mainloop()
