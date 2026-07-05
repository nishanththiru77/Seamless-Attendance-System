"""
Checkpoint Attendance System: Tracks up to 7 attendance checkpoints per student per date.
Data is stored in CSV format: Enrollment, Name, Date_Session1, Date_Session2, ..., Date_Session7
For each checkpoint, value is 1 if marked, 0 or empty if not.
"""

import os
import pandas as pd
import datetime
from glob import glob

CHECKPOINT_DIR = "Attendance/Checkpoints"
CHECKPOINT_FILE_PATTERN = "checkpoint_*.csv"

def ensure_checkpoint_dir():
    """Create checkpoint directory if it doesn't exist."""
    os.makedirs(CHECKPOINT_DIR, exist_ok=True)

def get_checkpoint_file(date_str=None):
    """Get checkpoint file path for a given date (default: today)."""
    if date_str is None:
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    return os.path.join(CHECKPOINT_DIR, f"checkpoint_{date_str}.csv")

def get_checkpoint_df(date_str=None):
    """Load checkpoint CSV for a date, creating empty one if not exists."""
    ensure_checkpoint_dir()
    filepath = get_checkpoint_file(date_str)
    
    if os.path.exists(filepath):
        try:
            df = pd.read_csv(filepath)
            # Validate that required columns exist
            required_cols = ['Enrollment', 'Name'] + [f'Checkpoint_{i}' for i in range(1, 8)]
            if all(col in df.columns for col in required_cols):
                # Don't remove duplicates here - let cleanup_duplicate_checkpoints handle it
                return df
            else:
                # CSV exists but is malformed, recreate it
                pass
        except Exception:
            # CSV exists but can't be read, recreate it
            pass
    
    # Create empty DataFrame with structure
    df = pd.DataFrame(columns=['Enrollment', 'Name'] + [f'Checkpoint_{i}' for i in range(1, 8)])
    return df

def add_student_checkpoint(enrollment, name, checkpoint_num, date_str=None):
    """Mark a student present at a specific checkpoint on a date."""
    if checkpoint_num < 1 or checkpoint_num > 7:
        raise ValueError("Checkpoint must be between 1 and 7")
    
    df = get_checkpoint_df(date_str)
    filepath = get_checkpoint_file(date_str)
    
    col_name = f'Checkpoint_{checkpoint_num}'
    
    # Ensure the column exists
    if col_name not in df.columns:
        df[col_name] = 0
    
    # Find or create row for this student
    enrollment_str = str(enrollment).strip()
    
    # If dataframe doesn't have Enrollment column, ensure it has correct structure
    if 'Enrollment' not in df.columns:
        df = pd.DataFrame(columns=['Enrollment', 'Name'] + [f'Checkpoint_{i}' for i in range(1, 8)])
    
    # Remove duplicates first - keep the last occurrence for each enrollment
    if not df.empty and 'Enrollment' in df.columns:
        df = df.drop_duplicates(subset=['Enrollment'], keep='last')
    
    # Find or create row for this student
    if df.empty:
        # Dataframe is empty but has correct columns, add new row
        new_row = {'Enrollment': enrollment_str, 'Name': str(name).strip()}
        for i in range(1, 8):
            new_row[f'Checkpoint_{i}'] = 0
        new_row[col_name] = 1
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    else:
        try:
            mask = df['Enrollment'].astype(str).str.strip() == enrollment_str
            if mask.any():
                # Update existing row - get the first (and should be only) match
                idx = df[mask].index[0]
                df.at[idx, col_name] = 1
                # Also update name in case it changed
                df.at[idx, 'Name'] = str(name).strip()
            else:
                # Add new row
                new_row = {'Enrollment': enrollment_str, 'Name': str(name).strip()}
                for i in range(1, 8):
                    new_row[f'Checkpoint_{i}'] = 0
                new_row[col_name] = 1
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        except Exception as e:
            # If matching fails, add as new student
            new_row = {'Enrollment': enrollment_str, 'Name': str(name).strip()}
            for i in range(1, 8):
                new_row[f'Checkpoint_{i}'] = 0
            new_row[col_name] = 1
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    
    # Final cleanup - remove any remaining duplicates before saving
    df = df.drop_duplicates(subset=['Enrollment'], keep='last')
    
    # Save to CSV
    ensure_checkpoint_dir()
    df.to_csv(filepath, index=False)
    return df

def get_next_checkpoint(enrollment, date_str=None):
    """Get the next available checkpoint number (1-7) for a student on a date."""
    df = get_checkpoint_df(date_str)
    enrollment_str = str(enrollment).strip()
    
    # If dataframe is empty, return first checkpoint
    if df.empty or 'Enrollment' not in df.columns:
        return 1
    
    # Find student in dataframe
    try:
        mask = df['Enrollment'].astype(str).str.strip() == enrollment_str
        if not mask.any():
            return 1  # First checkpoint for this student
        
        row = df[mask].iloc[0]
        for i in range(1, 8):
            col = f'Checkpoint_{i}'
            if col in row.index:
                val = row[col]
                if val == 0 or pd.isna(val) or val == '':
                    return i
    except Exception:
        # If anything goes wrong, default to first checkpoint
        return 1
    
    return None  # All 7 checkpoints filled

def get_all_checkpoint_dates():
    """Get list of all dates with checkpoint records."""
    ensure_checkpoint_dir()
    files = glob(os.path.join(CHECKPOINT_DIR, CHECKPOINT_FILE_PATTERN))
    dates = []
    for f in sorted(files, reverse=True):
        basename = os.path.basename(f)
        date_str = basename.replace("checkpoint_", "").replace(".csv", "")
        dates.append(date_str)
    return dates

def get_checkpoint_attendance(date_str):
    """Get attendance data for a specific date."""
    return get_checkpoint_df(date_str)

def update_checkpoint(enrollment, checkpoint_num, value, date_str=None):
    """Update a checkpoint value (for editing)."""
    if checkpoint_num < 1 or checkpoint_num > 7:
        raise ValueError("Checkpoint must be between 1 and 7")
    
    df = get_checkpoint_df(date_str)
    filepath = get_checkpoint_file(date_str)
    enrollment_str = str(enrollment).strip()
    
    mask = df['Enrollment'].astype(str).str.strip() == enrollment_str
    if mask.any():
        idx = df[mask].index[0]
        col_name = f'Checkpoint_{checkpoint_num}'
        df.at[idx, col_name] = 1 if value else 0
        df.to_csv(filepath, index=False)
        return True
    return False

def cleanup_duplicate_checkpoints(date_str=None):
    """Clean up duplicate entries in checkpoint files by merging them."""
    df = get_checkpoint_df(date_str)
    filepath = get_checkpoint_file(date_str)
    
    if df.empty or 'Enrollment' not in df.columns:
        return df
    
    # Group by enrollment and merge checkpoint data
    cleaned_rows = []
    for enrollment in df['Enrollment'].unique():
        enrollment_str = str(enrollment).strip()
        student_rows = df[df['Enrollment'].astype(str).str.strip() == enrollment_str]
        
        if len(student_rows) == 1:
            # No duplicates for this student
            cleaned_rows.append(student_rows.iloc[0].to_dict())
        else:
            # Merge multiple rows for this student
            merged_row = {
                'Enrollment': enrollment_str,
                'Name': student_rows.iloc[-1]['Name']  # Use latest name
            }
            
            # For each checkpoint, use OR logic (if any row has 1, result is 1)
            for i in range(1, 8):
                col_name = f'Checkpoint_{i}'
                if col_name in student_rows.columns:
                    # Convert to numeric, treating NaN/empty as 0
                    values = pd.to_numeric(student_rows[col_name], errors='coerce').fillna(0)
                    merged_row[col_name] = 1 if (values == 1).any() else 0
                else:
                    merged_row[col_name] = 0
            
            cleaned_rows.append(merged_row)
    
    # Create new DataFrame from cleaned data
    cleaned_df = pd.DataFrame(cleaned_rows)
    
    # Ensure all checkpoint columns exist
    for i in range(1, 8):
        col_name = f'Checkpoint_{i}'
        if col_name not in cleaned_df.columns:
            cleaned_df[col_name] = 0
    
    # Reorder columns
    column_order = ['Enrollment', 'Name'] + [f'Checkpoint_{i}' for i in range(1, 8)]
    cleaned_df = cleaned_df[column_order]
    
    # Save cleaned data
    ensure_checkpoint_dir()
    cleaned_df.to_csv(filepath, index=False)
    
    return cleaned_df
