import os
import sys
from glob import glob
import pandas as pd
# ensure project root is on path so show_attendance can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import show_attendance as sa

reports_folder = os.path.join("Attendance", "Reports")
files = sorted(glob(os.path.join(reports_folder, "*.csv")), key=os.path.getmtime, reverse=True)
if not files:
    print('No report files found in', reports_folder)
    exit(1)

csv_path = files[0]
print('Using report:', csv_path)

df_report = pd.read_csv(csv_path, encoding='utf-8-sig')
print('\nReport columns:', df_report.columns.tolist())

# Load students
students_path = os.path.join('StudentDetails', 'studentdetails.csv')
regs = []
if os.path.exists(students_path):
    with open(students_path, 'r', encoding='utf-8-sig') as f:
        for line in f:
            line=line.strip()
            if not line: continue
            if ',' in line:
                parts=[p.strip() for p in line.split(',') if p.strip()]
                if len(parts)>=2:
                    enroll_raw=parts[0]
                    name=parts[1]
                    regs.append((enroll_raw, name, sa._normalize_enroll(enroll_raw)))
            else:
                parts=line.split()
                if len(parts)>=2:
                    enroll_raw=parts[0]
                    name=' '.join(parts[1:])
                    regs.append((enroll_raw, name, sa._normalize_enroll(enroll_raw)))

print('\nLoaded students (display, name, norm):')
for r in regs:
    print(r)

if not regs:
    print('\nNo studentdetails.csv entries found — falling back to report rows')
    for _, row in df_report.iterrows():
        enroll_display = str(row.get('Enrollment', '')).strip()
        name = str(row.get('Name', '')).strip()
        regs.append((enroll_display, name, sa._normalize_enroll(enroll_display)))
    for r in regs:
        print(r)

# Build report_map
report_map = {}
cols = list(df_report.columns)
if len(cols)>2:
    target = cols[-1]
else:
    target = None

for r, v in zip(df_report['Enrollment'].astype(str), df_report[target] if target else []):
    key = sa._normalize_enroll(r)
    val = 1 if (not pd.isna(v) and str(v).strip()!='') else 0
    report_map[key]=val

print('\nReport map (norm_enroll -> val):')
for k,v in report_map.items():
    print(k, '->', v)

print('\nFinal check values for students:')
for enroll_raw, name, enroll_norm in regs:
    val = report_map.get(enroll_norm, 0)
    print(enroll_raw, '(',enroll_norm,')', name, '->', val)
