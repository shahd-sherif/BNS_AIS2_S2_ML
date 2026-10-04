import pandas as pd
import numpy as np

# 1. Load Data
df = pd.read_csv(r'C:\Users\MOBI LAP\BNS_AIS2_S2_ML\python\fordgobike-tripdataFor201902.csv')

# 2. Handle Missing Values
# Fill unknown categorical values; drop rows missing critical station IDs
df['member_gender'] = df['member_gender'].fillna('Unknown')
df['member_birth_year'] = df['member_birth_year'].fillna(df['member_birth_year'].median())
df.dropna(subset=['start_station_name', 'end_station_name'], inplace=True)

# 3. Feature Engineering
# Trip duration in minutes
df['duration_min'] = df['duration_sec'] / 60.0

# Calculate Age (Dataset reference year = 2019)
df['age'] = 2019 - df['member_birth_year'].astype(int)

# Age Group categorization
def categorize_age(age):
    if age < 30:
        return 'Young'
    elif age <= 50:
        return 'Adult'
    else:
        return 'Senior'

df['age_group'] = df['age'].apply(categorize_age)

# Parse Dates (defaulting 2019-02 for timestamp snippets)
df['start_time_dt'] = pd.to_datetime('2019-02-01 ' + df['start_time'].astype(str), errors='coerce')
df['start_date'] = df['start_time_dt'].dt.date
df['day_of_week'] = df['start_time_dt'].dt.day_name()
df['hour'] = df['start_time_dt'].dt.hour
df['is_weekend'] = df['day_of_week'].isin(['Saturday', 'Sunday']).astype(int)

# 4. Outlier Removal (keep duration <= 90 mins, age <= 85)
df = df[(df['duration_min'] > 1) & (df['duration_min'] <= 90)]
df = df[(df['age'] >= 18) & (df['age'] <= 85)]

# 5. Create Route column
df['route'] = df['start_station_name'] + " -> " + df['end_station_name']

# Export Cleaned Data
df.to_csv('cleaned_bikeshare.csv', index=False)
print(f"Preprocessing complete. Cleaned rows: {len(df)}")