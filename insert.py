import pandas as pd

df = pd.read_excel('Data.xlsx')
df.sort_values(by='ExitDate', inplace = True)
df = df[df.ExitTime.notna()]

for index, row in df.iterrows():
	print(f"{row['VehicleNo']} {str(row['ExitDate'].date())} {row['ExitTime']}")
	break