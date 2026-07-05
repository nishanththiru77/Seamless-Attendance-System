import pandas as pd
from glob import glob
import os
import tkinter
import csv
import tkinter as tk
from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
import checkpoint_attendance


def _normalize_enroll(value):
    """Normalize enrollment values to a canonical string without leading zeros
    and non-digit characters so lookups are consistent between student details
    and saved reports."""
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


def _is_marked(value):
    """Return True if a report cell should be considered marked/present.

    Handles numeric 1, string '1', 'true', 'yes' (case-insensitive), and
    boolean True. Treats empty strings, NaN, '0', 'false', 'no' as not marked.
    """
    try:
        # pandas NA handling
        if pd.isna(value):
            return False
    except Exception:
        pass
    try:
        s = str(value).strip()
    except Exception:
        return False
    if s == "":
        return False
    sl = s.lower()
    if sl in ("1", "true", "yes", "y", "t"):
        return True
    if sl in ("0", "false", "no", "n", "f"):
        return False
    # try numeric compare
    try:
        return float(s) == 1.0
    except Exception:
        return False

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


def show_student_history(enroll_display, name, enroll_norm):
    """Show full attendance history for a single student across all days."""
    import datetime

    # Get all dates that have checkpoint data
    dates = checkpoint_attendance.get_all_checkpoint_dates()
    if not dates:
        tk.messagebox.showinfo("No Data", "No attendance records found yet.")
        return

    dates = sorted(dates)  # oldest first

    history_rows = []

    for date_str in dates:
        try:
            df_day = checkpoint_attendance.get_checkpoint_attendance(date_str)
        except Exception:
            continue
        if df_day is None or df_day.empty or 'Enrollment' not in df_day.columns:
            continue

        # Find this student's row by normalized enrollment
        try:
            mask = df_day['Enrollment'].astype(str).apply(_normalize_enroll) == enroll_norm
        except Exception:
            continue

        if mask.any():
            row = df_day[mask].iloc[0]
            present_flags = []
            for i in range(1, 8):
                col_name = f'Checkpoint_{i}'
                val = row[col_name] if col_name in row.index else 0
                is_present = 1 if _is_marked(val) or val == 1 else 0
                present_flags.append(is_present)
        else:
            # Student not in file for this date → all absent
            present_flags = [0] * 7

        try:
            date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")
            weekday = date_obj.strftime("%A")
        except Exception:
            weekday = ""

        history_rows.append((date_str, weekday, present_flags))

    if not history_rows:
        tk.messagebox.showinfo("No Data", "No attendance rows found for this student.")
        return

    def compute_day_summary_from_rows(rows):
        """Compute day-based attendance using half-day logic.

        First 4 sessions = first half, next 3 = second half.
        A half-day is present only if all its sessions are present.
        """
        total_days_local = len(rows)
        total_halves = total_days_local * 2
        present_halves = 0

        for _, _, flags in rows:
            # Ensure flags has length 7
            pads = list(flags) + [0] * (7 - len(flags))
            first_half_present = all(pads[i] == 1 for i in range(4))       # sessions 1‑4
            second_half_present = all(pads[i] == 1 for i in range(4, 7))   # sessions 5‑7
            present_halves += int(first_half_present) + int(second_half_present)

        days_present_local = present_halves / 2.0 if total_halves > 0 else 0.0
        total_days_float = float(total_days_local)
        days_absent_local = total_days_float - days_present_local
        percentage_local = (days_present_local / total_days_float * 100.0) if total_days_float > 0 else 0.0
        return total_days_float, days_present_local, days_absent_local, percentage_local

    total_days, days_present, days_absent, percentage = compute_day_summary_from_rows(history_rows)

    # Build UI window
    win = tk.Toplevel()
    win.title(f"Attendance History - {name} ({enroll_display})")
    win.geometry("900x600")
    win.configure(background=BG_GRADIENT_START)

    try:
        win.iconbitmap("AMS.ico")
    except Exception:
        pass

    bg = create_gradient_frame(win, 900, 600, BG_GRADIENT_START, BG_GRADIENT_END)
    try:
        bg.place(x=0, y=0, relwidth=1, relheight=1)
        bg.lower()
    except Exception:
        pass

    header = tk.Frame(win, bg=BG_PANEL, height=80)
    header.pack(fill=X, padx=20, pady=20)
    header.pack_propagate(False)

    title_lbl = tk.Label(
        header,
        text=f"📊 Attendance Details - {name} ({enroll_display})",
        bg=BG_PANEL,
        fg=FG_PRIMARY,
        font=("Segoe UI", 18, "bold"),
        anchor="w",
    )
    title_lbl.pack(side=LEFT, padx=10)

    def format_summary_label(td, dp, da, pct):
        return f"Attendance: {pct:.1f}%  |  Present: {dp:.1f} / {td:.1f} days  |  Absent: {da:.1f} days"

    percent_lbl = tk.Label(
        header,
        text=format_summary_label(total_days, days_present, days_absent, percentage),
        bg=BG_PANEL,
        fg=FG_ACCENT,
        font=("Segoe UI", 14, "bold"),
        anchor="e",
    )
    percent_lbl.pack(side=RIGHT, padx=10)

    # Editable table area using labels (per‑student, with Edit/Save)
    main_frame = tk.Frame(win, bg=BG_CARD)
    main_frame.pack(fill=BOTH, expand=True, padx=20, pady=10)

    table_canvas = tk.Canvas(main_frame, bg=BG_CARD, highlightthickness=0)
    table_scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=table_canvas.yview)
    table_inner = tk.Frame(table_canvas, bg=BG_CARD)

    table_inner.bind(
        "<Configure>",
        lambda e: table_canvas.configure(scrollregion=table_canvas.bbox("all"))
    )

    table_canvas.create_window((0, 0), window=table_inner, anchor="nw")
    table_canvas.configure(yscrollcommand=table_scrollbar.set)

    table_canvas.pack(side=LEFT, fill=BOTH, expand=True)
    table_scrollbar.pack(side=RIGHT, fill="y")

    # Header row
    header_row = tk.Frame(table_inner, bg=BG_PANEL)
    header_row.pack(fill=X, padx=5, pady=5)

    tk.Label(header_row, text="Date", bg=BG_PANEL, fg=FG_ACCENT, font=("Segoe UI", 11, "bold"), width=12).grid(row=0, column=0, padx=4)
    tk.Label(header_row, text="Week day", bg=BG_PANEL, fg=FG_ACCENT, font=("Segoe UI", 11, "bold"), width=12).grid(row=0, column=1, padx=4)
    tk.Label(header_row, text="1st Half", bg=BG_PANEL, fg=FG_ACCENT, font=("Segoe UI", 11, "bold"), width=8).grid(row=0, column=2, padx=4)
    tk.Label(header_row, text="2nd Half", bg=BG_PANEL, fg=FG_ACCENT, font=("Segoe UI", 11, "bold"), width=8).grid(row=0, column=3, padx=4)
    for i in range(1, 8):
        tk.Label(header_row, text=str(i), bg=BG_PANEL, fg=FG_ACCENT, font=("Segoe UI", 10, "bold"), width=3).grid(row=0, column=3+i, padx=4)

    edit_mode = {"on": False}
    cell_vars = {}      # (row_idx, cp_num) -> IntVar
    half_labels = {}    # (row_idx, "FH"/"SH") -> Label

    def recompute_summary_from_vars():
        """Recompute day-based summary from current cell_vars."""
        # Build a temporary rows structure using current vars
        temp_rows = []
        for row_idx, (date_str, weekday, _) in enumerate(history_rows):
            flags = []
            for cp_num in range(1, 8):
                v = cell_vars.get((row_idx, cp_num))
                flags.append(int(v.get()) if v is not None else 0)
            temp_rows.append((date_str, weekday, flags))

        td, dp, da, pct = compute_day_summary_from_rows(temp_rows)
        try:
            percent_lbl.configure(text=format_summary_label(td, dp, da, pct))
        except Exception:
            pass

    def update_half_labels_for_row(row_idx):
        """Update first/second half labels for a given row based on cell_vars."""
        flags = []
        for cp_num in range(1, 8):
            v = cell_vars.get((row_idx, cp_num))
            flags.append(int(v.get()) if v is not None else 0)
        pads = flags + [0] * (7 - len(flags))
        first_half_present = all(pads[i] == 1 for i in range(4))
        second_half_present = all(pads[i] == 1 for i in range(4, 7))

        fh_lbl = half_labels.get((row_idx, "FH"))
        sh_lbl = half_labels.get((row_idx, "SH"))
        if fh_lbl is not None:
            fh_lbl.configure(
                text="P" if first_half_present else "A",
                fg="#38a169" if first_half_present else "#e53e3e",
            )
        if sh_lbl is not None:
            sh_lbl.configure(
                text="P" if second_half_present else "A",
                fg="#38a169" if second_half_present else "#e53e3e",
            )

    # Build data rows
    for row_idx, (date_str, weekday, flags) in enumerate(history_rows):
        row_bg = BG_CARD if row_idx % 2 == 0 else BG_DARK
        row_frame = tk.Frame(table_inner, bg=row_bg)
        row_frame.pack(fill=X, padx=5, pady=1)

        tk.Label(row_frame, text=date_str, bg=row_bg, fg=FG_SECONDARY, font=("Segoe UI", 10), width=12, anchor="center").grid(row=0, column=0, padx=4)
        tk.Label(row_frame, text=weekday, bg=row_bg, fg=FG_SECONDARY, font=("Segoe UI", 10), width=12, anchor="center").grid(row=0, column=1, padx=4)

        # Half‑day summary labels (P/A)
        fh_label = tk.Label(row_frame, text="", bg=row_bg, fg=FG_SECONDARY, font=("Segoe UI", 10, "bold"), width=8, anchor="center")
        fh_label.grid(row=0, column=2, padx=4)
        sh_label = tk.Label(row_frame, text="", bg=row_bg, fg=FG_SECONDARY, font=("Segoe UI", 10, "bold"), width=8, anchor="center")
        sh_label.grid(row=0, column=3, padx=4)
        half_labels[(row_idx, "FH")] = fh_label
        half_labels[(row_idx, "SH")] = sh_label

        for i in range(1, 8):
            present = flags[i-1] if i-1 < len(flags) else 0
            var = tk.IntVar(value=present)

            mark_text = "☑" if present else "☐"
            mark_color = "#38a169" if present else "#e53e3e"

            lbl = tk.Label(
                row_frame,
                text=mark_text,
                bg=row_bg,
                fg=mark_color,
                font=("Segoe UI", 12, "bold"),
                width=3,
                anchor="center",
            )
            lbl.grid(row=0, column=3+i, padx=4)

            def make_toggle(r_idx, cp_num):
                def toggle(event=None):
                    if not edit_mode["on"]:
                        return
                    v = cell_vars[(r_idx, cp_num)]
                    v.set(1 - v.get())
                    new_text = "☑" if v.get() == 1 else "☐"
                    new_color = "#38a169" if v.get() == 1 else "#e53e3e"
                    lbl_local = cell_labels[(r_idx, cp_num)]
                    lbl_local.configure(text=new_text, fg=new_color)

                    # Update half‑day labels and recompute day‑based summary
                    update_half_labels_for_row(r_idx)
                    recompute_summary_from_vars()
                return toggle

            lbl.bind("<Button-1>", make_toggle(row_idx, i))

            cell_vars[(row_idx, i)] = var
            # store label separately for easy update
            if 'cell_labels' not in locals():
                cell_labels = {}
            cell_labels[(row_idx, i)] = lbl

        # Initialize half‑day labels for this row
        update_half_labels_for_row(row_idx)

    # Footer with Edit / Save buttons
    footer = tk.Frame(win, bg=BG_PANEL, height=60)
    footer.pack(fill=X, padx=20, pady=10)
    footer.pack_propagate(False)

    info_lbl = tk.Label(
        footer,
        text="Click 'Edit' to modify attendance. Then click cells and press 'Save Changes'.",
        bg=BG_PANEL,
        fg=FG_SECONDARY,
        font=("Segoe UI", 10),
        anchor="w",
    )
    info_lbl.pack(side=LEFT, padx=10)

    def on_save():
        # Persist changes back to checkpoint CSVs per date
        try:
            for row_idx, (date_str, weekday, original_flags) in enumerate(history_rows):
                # Build flags for this date from current vars
                flags = []
                for cp_num in range(1, 8):
                    v = cell_vars.get((row_idx, cp_num))
                    flags.append(int(v.get()) if v is not None else 0)

                # Load or create dataframe for this date
                df_day = checkpoint_attendance.get_checkpoint_df(date_str)
                filepath = checkpoint_attendance.get_checkpoint_file(date_str)

                # Normalize enrollments for matching
                if not df_day.empty and 'Enrollment' in df_day.columns:
                    try:
                        norm_series = df_day['Enrollment'].astype(str).apply(_normalize_enroll)
                        mask = norm_series == enroll_norm
                    except Exception:
                        mask = pd.Series([False] * len(df_day))
                else:
                    mask = pd.Series([], dtype=bool)

                if mask.any():
                    idx = df_day[mask].index[0]
                else:
                    # Create new row for this student/day
                    new_row = {'Enrollment': enroll_display, 'Name': name}
                    for i in range(1, 8):
                        new_row[f'Checkpoint_{i}'] = 0
                    df_day = pd.concat([df_day, pd.DataFrame([new_row])], ignore_index=True)
                    idx = df_day.index[-1]

                # Update checkpoint columns
                for cp_num, val in enumerate(flags, start=1):
                    col_name = f'Checkpoint_{cp_num}'
                    if col_name not in df_day.columns:
                        df_day[col_name] = 0
                    df_day.at[idx, col_name] = int(val)

                # Save back to CSV
                checkpoint_attendance.ensure_checkpoint_dir()
                df_day.to_csv(filepath, index=False)

            # Recompute overall summary from saved vars
            recompute_summary_from_vars()
            tk.messagebox.showinfo("Saved", "Attendance changes saved.")
            edit_mode["on"] = False
        except Exception as e:
            tk.messagebox.showerror("Save Error", f"Failed to save attendance changes: {e}")

    def on_edit():
        # Enable inline editing without any popup
        edit_mode["on"] = True

    save_btn = tk.Button(footer, text="Save Changes", command=on_save)
    style_button(save_btn, bg=BTN_SUCCESS, hover_bg=BTN_SUCCESS_HOVER)
    save_btn.pack(side=RIGHT, padx=10)

    edit_btn = tk.Button(footer, text="Edit", command=on_edit)
    style_button(edit_btn, bg=BTN_WARNING, hover_bg=BTN_WARNING_HOVER)
    edit_btn.pack(side=RIGHT, padx=10)

def display_attendance(subject_name, csv_path):
    """Display attendance listing all registered students with editable checkboxes
    for the selected date (last date column in the report). Provides an Edit
    button (top-right) to enable editing, and a Submit button (bottom-right)
    that becomes "Save Changes" while editing. Saves changes back to CSV.
    """
    root = tkinter.Toplevel()
    root.title(f"📊 {subject_name} - Attendance Report")
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
    header_title.pack(side=LEFT, pady=20)

    # Load registered students. Keep both display and normalized enrollment
    # so we can show original formatting (e.g. leading zeros) but match
    # against report rows using a canonical normalized key.
    registered = []
    students_path = os.path.join("StudentDetails", "studentdetails.csv")
    try:
        with open(students_path, 'r', encoding='utf-8-sig', newline='') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                if ',' in line:
                    parts = [p.strip() for p in line.split(',') if p.strip()]
                    if len(parts) >= 2:
                        enroll_raw = parts[0]
                        name = parts[1]
                        enroll_norm = _normalize_enroll(enroll_raw)
                        registered.append((enroll_raw, name, enroll_norm))
                else:
                    # fallback: try split by whitespace
                    parts = line.split()
                    if len(parts) >= 2:
                        enroll_raw = parts[0]
                        name = ' '.join(parts[1:])
                        enroll_norm = _normalize_enroll(enroll_raw)
                        registered.append((enroll_raw, name, enroll_norm))
    except Exception:
        # If student details not found or malformed, fall back to report rows
        registered = []

    # Read report CSV into DataFrame
    try:
        df_report = pd.read_csv(csv_path, encoding='utf-8-sig')
    except Exception as e:
        tk.messagebox.showerror("Error", f"Failed to load report: {e}")
        root.destroy()
        return

    # Determine the target date column (use last column after Enrollment,Name)
    # If no date column exists, use today's date
    import datetime
    today_date = datetime.datetime.now().strftime("%Y-%m-%d")
    
    all_cols = list(df_report.columns)
    date_cols = all_cols[2:] if len(all_cols) > 2 else []
    if not date_cols:
        # Use today's date if no date column in CSV
        target_date = today_date
    else:
        # Use the last date column, but if it's not today, prefer today's date for current reports
        # (This allows viewing historical reports while defaulting to today for current view)
        last_csv_date = date_cols[-1]
        # Check if the CSV date looks like today (format YYYY-MM-DD)
        if last_csv_date == today_date:
            target_date = today_date
        else:
            # Use the CSV date (for historical reports)
            target_date = last_csv_date

    # If registered list is empty, create it from report enrollments. Store
    # both display and normalized values.
    if not registered:
        for _, row in df_report.iterrows():
            enroll_display = str(row.get('Enrollment', '')).strip()
            name = str(row.get('Name', '')).strip()
            enroll_norm = _normalize_enroll(enroll_display)
            registered.append((enroll_display, name, enroll_norm))

    # Also include any students found in TrainingImage folders (format: "<enroll>_<name>")
    # This ensures scanned/trained students appear in the UI even if not present
    # in StudentDetails.csv or the report CSV. We'll mark them present by default
    # if they don't already exist in the report mapping (below).
    training_enrolled = set()
    try:
        training_dir = os.path.join('TrainingImage')
        if os.path.isdir(training_dir):
            for entry in os.listdir(training_dir):
                path = os.path.join(training_dir, entry)
                if not os.path.isdir(path):
                    continue
                parts = entry.split('_', 1)
                enroll_raw = parts[0].strip()
                display_name = parts[1].replace('_', ' ').strip() if len(parts) > 1 else ''
                enroll_norm = _normalize_enroll(enroll_raw)
                if enroll_norm == '':
                    continue
                training_enrolled.add(enroll_norm)
                # add to registered list if not already present (by normalized key)
                if enroll_norm not in {r[2] for r in registered}:
                    registered.append((enroll_raw, display_name or entry, enroll_norm))
    except Exception:
        training_enrolled = set()

    # Load checkpoint attendance data for today's date
    current_session = None  # last session (S1..S7) that has any present students
    try:
        df_checkpoint = checkpoint_attendance.get_checkpoint_attendance(target_date)
        # Build report_map with checkpoint data
        report_map = {}
        for _, row in df_checkpoint.iterrows():
            enroll_norm = _normalize_enroll(row['Enrollment'])
            report_map[enroll_norm] = {}
            for cp_num in range(1, 8):
                col_name = f'Checkpoint_{cp_num}'
                val = row[col_name] if col_name in row.index else 0
                report_map[enroll_norm][col_name] = 1 if val == 1 else 0

        # Determine the latest session (checkpoint column) that has any 1s
        if not df_checkpoint.empty:
            for cp_num in range(1, 8):
                col_name = f'Checkpoint_{cp_num}'
                if col_name in df_checkpoint.columns:
                    try:
                        if (df_checkpoint[col_name] == 1).any():
                            current_session = cp_num
                    except Exception:
                        pass
    except Exception as e:
        # Fallback if checkpoint file doesn't exist
        report_map = {}
        for _, row in df_report.iterrows():
            enroll_norm = _normalize_enroll(row['Enrollment'])
            report_map[enroll_norm] = {}
            for cp_num in range(1, 8):
                report_map[enroll_norm][f'Checkpoint_{cp_num}'] = 0
        # Also initialize for training images
        try:
            for te in training_enrolled:
                if te and te not in report_map:
                    report_map[te] = {}
                    for cp_num in range(1, 8):
                        report_map[te][f'Checkpoint_{cp_num}'] = 0
        except:
            pass

    # Main content frame with scrollbar (no checkboxes here; only summary list)
    main_frame = tk.Frame(root, bg=BG_CARD)
    main_frame.pack(fill=BOTH, expand=True, padx=20, pady=10)

    canvas = tk.Canvas(main_frame, bg=BG_CARD, highlightthickness=0)
    scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg=BG_CARD)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    # Header row for the table with UNIFORM SIZING
    HEADER_HEIGHT = 40
    ROW_HEIGHT = 35
    COLUMN_PADDING = 5
    ENROLL_WIDTH = 12
    NAME_WIDTH = 25
    CHECKPOINT_WIDTH = 3
    
    header_row = tk.Frame(scrollable_frame, bg=BG_PANEL, relief=FLAT, bd=2, height=HEADER_HEIGHT)
    header_row.pack(fill=X, padx=10, pady=5)
    header_row.pack_propagate(False)
    
    tk.Label(header_row, text="Roll No", bg=BG_PANEL, fg=FG_ACCENT, font=("Segoe UI", 11, "bold"), width=ENROLL_WIDTH, height=1, anchor='w').grid(row=0, column=0, padx=COLUMN_PADDING, sticky='w')
    tk.Label(header_row, text="Name", bg=BG_PANEL, fg=FG_ACCENT, font=("Segoe UI", 11, "bold"), width=NAME_WIDTH, height=1, anchor='w').grid(row=0, column=1, padx=COLUMN_PADDING, sticky='w')
    tk.Label(header_row, text="Details", bg=BG_PANEL, fg=FG_ACCENT, font=("Segoe UI", 11, "bold"), width=NAME_WIDTH//2, height=1, anchor='center').grid(row=0, column=2, padx=COLUMN_PADDING, sticky='ew')

    # Show S1–S7 for the current day
    for i in range(1, 8):
        tk.Label(
            header_row,
            text=f"S{i}",
            bg=BG_PANEL,
            fg=FG_ACCENT,
            font=("Segoe UI", 10, "bold"),
            width=CHECKPOINT_WIDTH,
            height=1,
            anchor="center",
        ).grid(row=0, column=2 + i, padx=COLUMN_PADDING, sticky="ew")

    # Function to (re)build the student rows from `registered`.
    def refresh_rows():
        nonlocal current_session
        # remove existing data rows (keep header_row)
        for child in list(scrollable_frame.winfo_children()):
            if child is header_row:
                continue
            try:
                child.destroy()
            except Exception:
                pass

        for idx, (enroll_display, name, enroll_norm) in enumerate(registered):
            row_bg = BG_CARD if idx % 2 == 0 else BG_DARK
            row = tk.Frame(scrollable_frame, bg=row_bg, relief=FLAT, bd=1, height=ROW_HEIGHT)
            row.pack(fill=X, padx=10, pady=2)
            row.pack_propagate(False)

            lbl_enroll = tk.Label(row, text=enroll_display, bg=row_bg, fg=FG_SECONDARY, font=("Segoe UI", 10), width=ENROLL_WIDTH, anchor='w', height=1)
            lbl_enroll.grid(row=0, column=0, padx=COLUMN_PADDING, sticky='w')

            lbl_name = tk.Label(row, text=name, bg=row_bg, fg=FG_SECONDARY, font=("Segoe UI", 10), width=NAME_WIDTH, anchor='w', height=1)
            lbl_name.grid(row=0, column=1, padx=COLUMN_PADDING, sticky='w')

            # Clickable name in Details column to open full history
            detail_lbl = tk.Label(
                row,
                text=name,
                bg=row_bg,
                fg=FG_ACCENT,
                font=("Segoe UI", 10, "underline"),
                width=NAME_WIDTH//2,
                anchor='center',
                height=1,
                cursor="hand2",
            )
            detail_lbl.grid(row=0, column=2, padx=COLUMN_PADDING, sticky='ew')
            detail_lbl.bind(
                "<Button-1>",
                lambda e, ed=enroll_display, nm=name, en=enroll_norm: show_student_history(ed, nm, en),
            )

            # Current day's S1–S7 checkboxes (read‑only, reflect checkpoint_attendance)
            for cp_num in range(1, 8):
                col_name = f"Checkpoint_{cp_num}"
                is_marked = report_map.get(enroll_norm, {}).get(col_name, 0) == 1

                mark_text = "☑" if is_marked else "☐"
                # Highlight current_session's absences in black; others grey
                if is_marked:
                    mark_color = FG_ACCENT
                elif current_session is not None and cp_num == current_session:
                    mark_color = "black"
                else:
                    mark_color = FG_SECONDARY

                tk.Label(
                    row,
                    text=mark_text,
                    bg=row_bg,
                    fg=mark_color,
                    font=("Segoe UI", 12, "bold"),
                    width=CHECKPOINT_WIDTH,
                    anchor="center",
                ).grid(row=0, column=2 + cp_num, padx=COLUMN_PADDING, sticky="ew")

    # Refresh button reloads the checkpoint data and updates list
    def update_view():
        nonlocal target_date, report_map, current_session
        try:
            # Reload checkpoint data for today's date
            df_checkpoint = checkpoint_attendance.get_checkpoint_attendance(target_date)
            # Rebuild report_map with checkpoint data
            new_map = {}
            for _, row in df_checkpoint.iterrows():
                enroll_norm = _normalize_enroll(row['Enrollment'])
                new_map[enroll_norm] = {}
                for cp_num in range(1, 8):
                    col_name = f'Checkpoint_{cp_num}'
                    val = row[col_name] if col_name in row.index else 0
                    new_map[enroll_norm][col_name] = 1 if val == 1 else 0

            # Recompute current_session (latest checkpoint with any 1s)
            current_session = None
            if not df_checkpoint.empty:
                for cp_num in range(1, 8):
                    col_name = f'Checkpoint_{cp_num}'
                    if col_name in df_checkpoint.columns:
                        try:
                            if (df_checkpoint[col_name] == 1).any():
                                current_session = cp_num
                        except Exception:
                            pass
        except Exception as e:
            tk.messagebox.showerror("Reload Error", f"Failed to reload checkpoint data: {e}")
            return

        # Update reference
        report_map = new_map

        # Update header/date label
        try:
            header_title.configure(text=f"📊 {target_date} - Attendance Report")
        except Exception:
            pass

        # Rebuild rows so UI reflects latest checkpoint data
        try:
            refresh_rows()
        except Exception as e:
            tk.messagebox.showerror("Refresh Error", f"Error refreshing rows: {e}")

    refresh_btn = tk.Button(header_frame, text="Refresh", command=update_view)
    style_button(refresh_btn, bg=BTN_PRIMARY, hover_bg=BTN_PRIMARY_HOVER)
    refresh_btn.pack(side=RIGHT, padx=10)

    # Automatic refresh toggle: watches Attendance/Reports for new CSVs
    try:
        last_mtime = os.path.getmtime(csv_path)
    except Exception:
        last_mtime = 0

    auto_refresh_on = {'on': False}

    def set_auto_button_text():
        try:
            auto_btn.configure(text=('Auto: ON' if auto_refresh_on['on'] else 'Auto: OFF'))
        except Exception:
            pass

    def toggle_auto():
        auto_refresh_on['on'] = not auto_refresh_on['on']
        set_auto_button_text()
        if auto_refresh_on['on']:
            # start the poll loop
            root.after(1500, auto_check)

    def auto_check():
        nonlocal last_mtime, csv_path
        if not auto_refresh_on['on']:
            return
        reports_folder = os.path.join('Attendance', 'Reports')
        try:
            files = sorted(glob(os.path.join(reports_folder, "*.csv")), key=os.path.getmtime, reverse=True)
            if files:
                latest = files[0]
                try:
                    m = os.path.getmtime(latest)
                except Exception:
                    m = 0
                # If file changed or a new latest file exists, reload
                if latest != csv_path or m != last_mtime:
                    csv_path = latest
                    last_mtime = m
                    update_view()
        except Exception:
            pass
        # schedule next check
        try:
            root.after(3000, auto_check)
        except Exception:
            pass

    auto_btn = tk.Button(header_frame, text="Auto: OFF", command=toggle_auto)
    style_button(auto_btn, bg=BTN_SUCCESS, hover_bg=BTN_SUCCESS_HOVER)
    auto_btn.pack(side=RIGHT, padx=10)

    # Build initial rows
    refresh_rows()

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Footer info only (editing is done per-student history)
    footer_frame = tk.Frame(root, bg=BG_PANEL, height=70)
    footer_frame.pack(fill=X, padx=20, pady=10)
    footer_frame.pack_propagate(False)

    info_label = tk.Label(footer_frame, text=f"Click a student name in 'Details' to see and edit full attendance history.", bg=BG_PANEL, fg=FG_ACCENT, font=("Segoe UI", 10, "italic"))
    info_label.pack(side=LEFT, padx=10, pady=10)

    # No submit/save button here; edits happen inside per-student history window


def subjectchoose(text_to_speech):
    # View current date's attendance using checkpoint system
    import datetime
    today_date = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # Check if checkpoint file exists for today
    checkpoint_file = checkpoint_attendance.get_checkpoint_file(today_date)
    if not os.path.exists(checkpoint_file):
        # If no checkpoint file exists, create a dummy CSV for display purposes
        # This allows the UI to show all registered students even if no attendance taken yet
        reports_folder = os.path.join("Attendance", "Reports")
        os.makedirs(reports_folder, exist_ok=True)
        csv_path = os.path.join(reports_folder, f"Reports_{today_date}.csv")
        # Create empty CSV with date column if it doesn't exist
        if not os.path.exists(csv_path):
            try:
                # Try to load registered students to create initial report
                students_path = os.path.join("StudentDetails", "studentdetails.csv")
                if os.path.exists(students_path):
                    df_init = pd.read_csv(students_path, header=None, names=["Enrollment", "Name"], dtype=str)
                    df_init[today_date] = ""
                    df_init.to_csv(csv_path, index=False)
                else:
                    # Create empty CSV with just headers
                    df_empty = pd.DataFrame(columns=["Enrollment", "Name", today_date])
                    df_empty.to_csv(csv_path, index=False)
            except Exception:
                # Create minimal CSV if all else fails
                df_empty = pd.DataFrame(columns=["Enrollment", "Name", today_date])
                df_empty.to_csv(csv_path, index=False)
    else:
        # Use checkpoint file location for the report path (display_attendance will load checkpoint data)
        reports_folder = os.path.join("Attendance", "Reports")
        os.makedirs(reports_folder, exist_ok=True)
        csv_path = os.path.join(reports_folder, f"Reports_{today_date}.csv")
        # Create/update the CSV with today's date column so display_attendance can use it
        if not os.path.exists(csv_path):
            try:
                # Load registered students
                students_path = os.path.join("StudentDetails", "studentdetails.csv")
                if os.path.exists(students_path):
                    df_init = pd.read_csv(students_path, header=None, names=["Enrollment", "Name"], dtype=str)
                    df_init[today_date] = ""
                    df_init.to_csv(csv_path, index=False)
                else:
                    df_empty = pd.DataFrame(columns=["Enrollment", "Name", today_date])
                    df_empty.to_csv(csv_path, index=False)
            except Exception:
                df_empty = pd.DataFrame(columns=["Enrollment", "Name", today_date])
                df_empty.to_csv(csv_path, index=False)
    
    subject_display = f"Attendance Report - {today_date}"
    display_attendance(subject_display, csv_path)
