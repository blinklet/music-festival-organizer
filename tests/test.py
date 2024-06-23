import pandas as pd
import mfo.admin.services.spreadsheet_columns as sc

#responses = '/home/brian/Projects/Music Festival Program/Music Festival Reference Material/Spreadsheets and Reports/QCMF Online Entry Form (Responses).ods'
responses = '/home/brian/Projects/Music Festival Program/Music Festival Reference Material/Spreadsheets and Reports/test.ods'
df = pd.read_excel(responses, sheet_name='Form Responses 1', engine='odf')

lc = list(sc.names.keys())
lr = df.columns.values.tolist()
# .rename(columns=lambda x: x.lstrip())
for i in range(min(len(lc),len(lr))):
    if lc[i] != lr[i]:
        print(f"'{lc[i]}' , '{lr[i]}'")

if lc == lr:
    print("GOOD")
else:
    print("bad")