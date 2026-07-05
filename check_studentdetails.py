import pandas as pd
studentdetail_path = 'StudentDetails/studentdetails.csv'
try:
    df_raw = pd.read_csv(studentdetail_path, header=None, names=["Enrollment", "Name"], dtype=str, skip_blank_lines=True)
except Exception as e:
    print('Error reading file:', e)
    raise

# Clean
df_raw["Enrollment"] = df_raw["Enrollment"].astype(str).str.strip()
df_raw["Enrollment"] = df_raw["Enrollment"].str.replace(r"\D+", "", regex=True)
df_raw["Enrollment"] = pd.to_numeric(df_raw["Enrollment"], errors="coerce")
df_raw = df_raw.dropna(subset=["Enrollment"]) 
if df_raw.empty:
    print('No valid student records found after cleaning')
else:
    df_raw["Enrollment"] = df_raw["Enrollment"].astype(int)
    df = df_raw.drop_duplicates(subset=["Enrollment"], keep="last")
    print('Total valid students:', len(df))
    print(df.head(20).to_string(index=False))
