"""
Past Reports Viewer: Display historical checkpoint attendance by date.
"""

import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import os
import checkpoint_attendance
import pandas as pd

# Color scheme (matching main app)
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

def show_past_reports(text_to_speech):
    """Display past attendance reports by date."""
    root = tk.Tk()
    root.title("📅 Past Attendance Reports")
    root.geometry("1000x700")
    root.configure(background=BG_GRADIENT_START)
    
    try:
        root.iconbitmap("AMS.ico")
    except:
        pass

    # Header
    header_frame = tk.Frame(root, bg=BG_PANEL, height=80)
    header_frame.pack(fill=X, padx=20, pady=20)
    header_frame.pack_propagate(False)

    header_title = tk.Label(
        header_frame,
        text="📅 Past Attendance Reports",
        bg=BG_PANEL,
        fg=FG_PRIMARY,
        font=("Segoe UI", 24, "bold")
    )
    header_title.pack(pady=20)

    # Main content
    content_frame = tk.Frame(root, bg=BG_GRADIENT_START)
    content_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)

    # Left panel: Date list
    dates_frame = tk.Frame(content_frame, bg=BG_CARD, relief=FLAT, bd=0)
    dates_frame.pack(side=LEFT, fill=BOTH, expand=False, padx=10, pady=10)
    dates_frame.configure(width=200)

    dates_title = tk.Label(
        dates_frame,
        text="Select Date:",
        bg=BG_CARD,
        fg=FG_ACCENT,
        font=("Segoe UI", 14, "bold")
    )
    dates_title.pack(pady=10)

    # Get all available dates
    dates_list = checkpoint_attendance.get_all_checkpoint_dates()

    selected_date = {'value': None}

    def on_date_select(date_str):
        """Load attendance data for selected date."""
        selected_date['value'] = date_str
        show_attendance_for_date(date_str)

    # Create date buttons
    dates_scroll_frame = tk.Frame(dates_frame, bg=BG_CARD)
    dates_scroll_frame.pack(fill=BOTH, expand=True, padx=5, pady=5)

    if not dates_list:
        no_dates_label = tk.Label(
            dates_scroll_frame,
            text="No checkpoint records yet.\nMark attendance to create records.",
            bg=BG_CARD,
            fg=FG_SECONDARY,
            font=("Segoe UI", 11),
            justify=CENTER
        )
        no_dates_label.pack(pady=20)
    else:
        for date in dates_list:
            btn = tk.Button(
                dates_scroll_frame,
                text=date,
                command=lambda d=date: on_date_select(d),
                bg=BG_PANEL,
                fg=FG_PRIMARY,
                font=("Segoe UI", 11),
                relief=FLAT,
                padx=10,
                pady=8
            )
            btn.pack(fill=X, padx=5, pady=3)

    # Right panel: Attendance details
    detail_frame = tk.Frame(content_frame, bg=BG_CARD, relief=FLAT, bd=0)
    detail_frame.pack(side=RIGHT, fill=BOTH, expand=True, padx=10, pady=10)

    # Header frame for detail title and Edit button
    detail_header = tk.Frame(detail_frame, bg=BG_CARD)
    detail_header.pack(fill=X, padx=10, pady=5)
    
    detail_title = tk.Label(
        detail_header,
        text="Attendance Details",
        bg=BG_CARD,
        fg=FG_ACCENT,
        font=("Segoe UI", 14, "bold")
    )
    detail_title.pack(side=LEFT, pady=5)

    # Scrollable details area with canvas for scrolling
    detail_scroll_container = tk.Frame(detail_frame, bg=BG_CARD)
    detail_scroll_container.pack(fill=BOTH, expand=True, padx=10, pady=10)
    
    canvas = tk.Canvas(detail_scroll_container, bg=BG_CARD, highlightthickness=0)
    scrollbar = ttk.Scrollbar(detail_scroll_container, orient="vertical", command=canvas.yview)
    details_inner = tk.Frame(canvas, bg=BG_CARD)
    
    details_inner.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas_window = canvas.create_window((0, 0), window=details_inner, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    # Configure canvas to resize with window
    def configure_canvas_width(event):
        canvas_width = event.width
        canvas.itemconfig(canvas_window, width=canvas_width)
    
    canvas.bind('<Configure>', configure_canvas_width)
    
    canvas.pack(side=LEFT, fill=BOTH, expand=True)
    scrollbar.pack(side=RIGHT, fill="y")

    # Store check_vars and edit_mode for the current date view
    check_vars = {}
    edit_mode = {"on": False}
    current_edit_date = {"value": None}
    
    # Helper function to normalize enrollment (matching show_attendance.py)
    def _normalize_enroll(value):
        try:
            s = str(value).strip()
        except Exception:
            return ""
        digits = ''.join(ch for ch in s if ch.isdigit())
        if digits == "":
            return s
        try:
            return str(int(digits))
        except Exception:
            return digits
    
    def style_button(btn, bg=BTN_PRIMARY, hover_bg=BTN_PRIMARY_HOVER, fg=FG_SECONDARY):
        """Style button with hover effects"""
        btn.configure(
            bg=bg,
            fg=fg,
            activebackground=hover_bg,
            activeforeground=fg,
            bd=0,
            relief=FLAT,
            highlightthickness=0,
            cursor="hand2",
            font=("Segoe UI", 11, "bold"),
            padx=15,
            pady=8
        )
        def on_enter(event):
            btn.configure(bg=hover_bg, relief=RAISED, bd=2)
        def on_leave(event):
            btn.configure(bg=bg, relief=FLAT, bd=0)
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
    
    def enable_edit_mode():
        """Enable editing of checkboxes"""
        edit_mode["on"] = True
        edit_btn.configure(text="Save Changes")
        # Enable clicking on checkpoint labels to toggle
        for enroll_norm, item in check_vars.items():
            for cp_num, cp_item in item['checkpoints'].items():
                label = cp_item['label']
                def make_toggle(enroll_key, cp_num_val):
                    def toggle(event=None):
                        cp_data = check_vars[enroll_key]['checkpoints'][cp_num_val]
                        cp_data['var'].set(1 - cp_data['var'].get())
                        mark_text = "✓" if cp_data['var'].get() == 1 else "☐"
                        mark_color = FG_ACCENT if cp_data['var'].get() == 1 else FG_SECONDARY
                        cp_data['label'].configure(text=mark_text, fg=mark_color, cursor="hand2")
                    return toggle
                label.bind("<Button-1>", make_toggle(enroll_norm, cp_num))
                label.configure(cursor="hand2")
    
    def save_changes():
        """Save edited changes back to checkpoint system"""
        if not edit_mode["on"]:
            return
        
        if current_edit_date["value"] is None:
            tk.messagebox.showerror("Error", "No date selected for editing.")
            return
        
        date_str = current_edit_date["value"]
        
        try:
            # Get current checkpoint dataframe
            df_checkpoint = checkpoint_attendance.get_checkpoint_attendance(date_str)
            
            # Update checkpoint values from check_vars
            for enroll_norm, item in check_vars.items():
                enrollment = item['display']
                name = item['name']
                
                # Find or create row
                enrollment_str = str(enrollment).strip()
                mask = df_checkpoint['Enrollment'].astype(str).str.strip() == enrollment_str
                
                if mask.any():
                    idx = df_checkpoint[mask].index[0]
                else:
                    # Add new row
                    new_row = {'Enrollment': enrollment, 'Name': name}
                    for i in range(1, 8):
                        new_row[f'Checkpoint_{i}'] = 0
                    df_checkpoint = pd.concat([df_checkpoint, pd.DataFrame([new_row])], ignore_index=True)
                    idx = len(df_checkpoint) - 1
                
                # Update each checkpoint
                for cp_num in range(1, 8):
                    col_name = f'Checkpoint_{cp_num}'
                    value = item['checkpoints'][cp_num]['var'].get()
                    df_checkpoint.at[idx, col_name] = value
                    # Also update name in case it changed
                    df_checkpoint.at[idx, 'Name'] = name
            
            # Save back to checkpoint file
            checkpoint_file = checkpoint_attendance.get_checkpoint_file(date_str)
            checkpoint_attendance.ensure_checkpoint_dir()
            df_checkpoint.to_csv(checkpoint_file, index=False)
            
            tk.messagebox.showinfo("Saved", f"Changes saved successfully for {date_str}.")
            
            # Exit edit mode and refresh view
            edit_mode["on"] = False
            edit_btn.configure(text="Edit")
            show_attendance_for_date(date_str)
            
        except Exception as e:
            tk.messagebox.showerror("Save Error", f"Failed to save changes: {str(e)}")
    
    def on_edit_click():
        """Handle Edit/Save button click"""
        if edit_mode["on"]:
            save_changes()
        else:
            enable_edit_mode()
    
    # Edit button (will be positioned in header)
    edit_btn = tk.Button(
        detail_header,
        text="Edit",
        command=on_edit_click,
        bg=BTN_WARNING,
        fg=FG_SECONDARY,
        font=("Segoe UI", 11, "bold"),
        padx=15,
        pady=8
    )
    style_button(edit_btn, bg=BTN_WARNING, hover_bg=BTN_WARNING_HOVER)
    edit_btn.pack(side=RIGHT, padx=10)
    
    def show_attendance_for_date(date_str):
        """Display attendance data for a specific date."""
        # Clear previous content
        for widget in details_inner.winfo_children():
            try:
                widget.destroy()
            except:
                pass
        
        # Reset edit mode for new date
        edit_mode["on"] = False
        edit_btn.configure(text="Edit")
        current_edit_date["value"] = date_str
        check_vars.clear()

        try:
            # Load checkpoint data for the date
            df_checkpoint = checkpoint_attendance.get_checkpoint_attendance(date_str)
            
            # Load all registered students using pandas (more robust)
            registered = []
            students_path = os.path.join("StudentDetails", "studentdetails.csv")
            try:
                # Try absolute path first, then relative
                if not os.path.exists(students_path):
                    # Try with current working directory
                    cwd = os.getcwd()
                    alt_path = os.path.join(cwd, students_path)
                    if os.path.exists(alt_path):
                        students_path = alt_path
                
                if os.path.exists(students_path):
                    # Use pandas to read CSV (handles empty lines better)
                    try:
                        df_students = pd.read_csv(students_path, header=None, names=["Enrollment", "Name"], dtype=str, skip_blank_lines=True)
                        # Clean and filter valid entries
                        df_students = df_students.dropna(subset=["Enrollment", "Name"])
                        df_students = df_students[df_students["Enrollment"].astype(str).str.strip() != ""]
                        df_students = df_students[df_students["Name"].astype(str).str.strip() != ""]
                        
                        for _, row in df_students.iterrows():
                            enroll_raw = str(row["Enrollment"]).strip()
                            name = str(row["Name"]).strip()
                            if enroll_raw and name:
                                enroll_norm = _normalize_enroll(enroll_raw)
                                registered.append((enroll_raw, name, enroll_norm))
                        print(f"DEBUG: Loaded {len(registered)} students from CSV using pandas")
                    except Exception as pd_error:
                        # Fallback to manual parsing
                        print(f"DEBUG: Pandas read failed, using manual parsing: {pd_error}")
                        with open(students_path, 'r', encoding='utf-8-sig', newline='') as f:
                            for line_num, line in enumerate(f, 1):
                                line = line.strip()
                                if not line:
                                    continue
                                if ',' in line:
                                    parts = [p.strip() for p in line.split(',')]
                                    parts = [p for p in parts if p]
                                    if len(parts) >= 2:
                                        enroll_raw = parts[0]
                                        name = parts[1]
                                        if enroll_raw and name:
                                            enroll_norm = _normalize_enroll(enroll_raw)
                                            registered.append((enroll_raw, name, enroll_norm))
                        print(f"DEBUG: Loaded {len(registered)} students from CSV using manual parsing")
                else:
                    print(f"DEBUG: Students file not found at: {students_path}")
            except Exception as e:
                import traceback
                print(f"Error loading students: {e}")
                print(traceback.format_exc())
            
            # If no registered students found, use checkpoint data
            if not registered and not df_checkpoint.empty:
                for _, row in df_checkpoint.iterrows():
                    enroll_raw = str(row.get('Enrollment', '')).strip()
                    name = str(row.get('Name', '')).strip()
                    enroll_norm = _normalize_enroll(enroll_raw)
                    registered.append((enroll_raw, name, enroll_norm))
            
            # If still no data, show message with helpful info
            if not registered:
                debug_info = f"Students path tried: {students_path}\nCheckpoint file exists: {os.path.exists(checkpoint_attendance.get_checkpoint_file(date_str))}"
                print(f"DEBUG: No registered students found. {debug_info}")
                no_data = tk.Label(
                    details_inner,
                    text=f"No registered students found for {date_str}.\nPlease register students first.",
                    bg=BG_CARD,
                    fg=FG_SECONDARY,
                    font=("Segoe UI", 12),
                    justify=CENTER
                )
                no_data.pack(pady=20)
                canvas.update_idletasks()
                canvas.configure(scrollregion=canvas.bbox("all"))
                return

            # Build a map of checkpoint data by normalized enrollment
            checkpoint_map = {}
            if not df_checkpoint.empty:
                for _, row in df_checkpoint.iterrows():
                    enroll_raw = str(row.get('Enrollment', '')).strip()
                    enroll_norm = _normalize_enroll(enroll_raw)
                    checkpoint_map[enroll_norm] = {}
                    for cp_num in range(1, 8):
                        col_name = f'Checkpoint_{cp_num}'
                        val = row.get(col_name, 0)
                        checkpoint_map[enroll_norm][col_name] = 1 if (val == 1 or val == "1" or str(val).strip() == "1") else 0

            # Header row - Only Name and 7 checkpoints (NO Roll No) with UNIFORM SIZING
            HEADER_HEIGHT = 40
            ROW_HEIGHT = 35
            COLUMN_PADDING = 5
            NAME_WIDTH = 30
            CHECKPOINT_WIDTH = 3
            
            header = tk.Frame(details_inner, bg=BG_PANEL, height=HEADER_HEIGHT)
            header.pack(fill=X, padx=5, pady=5)
            header.pack_propagate(False)

            name_header = tk.Label(header, text="Name", bg=BG_PANEL, fg=FG_ACCENT, font=("Segoe UI", 11, "bold"), width=NAME_WIDTH, anchor='w', height=1)
            name_header.pack(side=LEFT, padx=COLUMN_PADDING, pady=5)
            
            for i in range(1, 8):
                cp_header = tk.Label(header, text=f"S{i}", bg=BG_PANEL, fg=FG_ACCENT, font=("Segoe UI", 10, "bold"), width=CHECKPOINT_WIDTH, anchor='center', height=1)
                cp_header.pack(side=LEFT, padx=COLUMN_PADDING, pady=5)
            
            print(f"DEBUG: Displaying {len(registered)} registered students for date {date_str}")

            # Data rows - Show all registered students with their checkpoint data
            for idx, (enroll_raw, name, enroll_norm) in enumerate(registered):
                row_bg = BG_CARD if idx % 2 == 0 else BG_DARK
                row_frame = tk.Frame(details_inner, bg=row_bg, height=ROW_HEIGHT)
                row_frame.pack(fill=X, padx=5, pady=2)
                row_frame.pack_propagate(False)

                # Name label
                name_label = tk.Label(row_frame, text=name, bg=row_bg, fg=FG_SECONDARY, font=("Segoe UI", 10), width=NAME_WIDTH, anchor='w', height=1)
                name_label.pack(side=LEFT, padx=COLUMN_PADDING, pady=5)

                # Initialize check_vars for this student
                check_vars[enroll_norm] = {'checkpoints': {}, 'name': name, 'display': enroll_raw}

                # Show checkmarks for each checkpoint (use checkpoint_map if available)
                for i in range(1, 8):
                    col_name = f'Checkpoint_{i}'
                    # Get value from checkpoint_map if available, otherwise 0
                    if enroll_norm in checkpoint_map and col_name in checkpoint_map[enroll_norm]:
                        is_marked = checkpoint_map[enroll_norm][col_name]
                    else:
                        is_marked = 0
                    
                    mark_text = "✓" if is_marked else "☐"
                    mark_color = FG_ACCENT if is_marked else FG_SECONDARY
                    
                    var = tk.IntVar(value=is_marked)
                    mark_label = tk.Label(row_frame, text=mark_text, bg=row_bg, fg=mark_color, font=("Segoe UI", 14, "bold"), width=CHECKPOINT_WIDTH, anchor='center', height=1)
                    mark_label.pack(side=LEFT, padx=COLUMN_PADDING, pady=5)
                    
                    check_vars[enroll_norm]['checkpoints'][i] = {
                        'var': var,
                        'widget': mark_label,
                        'label': mark_label
                    }
            
            # Force update of canvas and scroll region
            details_inner.update_idletasks()
            canvas.update_idletasks()
            bbox = canvas.bbox("all")
            if bbox:
                canvas.configure(scrollregion=bbox)
            else:
                # If bbox is None, set a default scroll region
                canvas.configure(scrollregion=(0, 0, 1000, 600))
            
            print(f"DEBUG: Created {len(registered)} rows, canvas bbox: {bbox}")

        except Exception as e:
            import traceback
            error_msg = f"Error loading data: {str(e)}\n{traceback.format_exc()}"
            print(f"PAST REPORTS ERROR: {error_msg}")  # Print full error to console for debugging
            error_label = tk.Label(
                details_inner,
                text=f"Error loading data: {str(e)}\nCheck console for details.",
                bg=BG_CARD,
                fg="#ff6b6b",
                font=("Segoe UI", 12),
                justify=CENTER
            )
            error_label.pack(pady=20)
            canvas.update_idletasks()
            canvas.configure(scrollregion=canvas.bbox("all"))

    root.mainloop()
