from openpyxl import Workbook
from openpyxl.worksheet.datavalidation import DataValidation

wb = Workbook()
ws = wb.active
ws.title = "AreaData"

ws['A1'] = "Chennai"
ws['B1'] = "Delhi"
ws['C1'] = "Mumbai"

ws['A2'] = "Tambaram"
ws['B2'] = "Connaught Place"
ws['C2'] = "Dadar"
ws['A3'] = "T. Nagar"
ws['B3'] = "Karol Bagh"
ws['C3'] = "Dadar West"
ws['A4'] = "Adyar"
ws['B4'] = "Janakpuri"
ws['C4'] = "Dadar East"

data_val = DataValidation(type="list", formula1="='AreaData'!$A$1:$C$1")  # References column A in the DataSource sheet

next_sheet = wb.create_sheet('Area')
next_sheet['A1'] = "Select the City"
# Add the data validation to the new sheet
next_sheet.add_data_validation(data_val)
data_val.add(next_sheet["B1"])

# Auto add the values based on the city selection
next_sheet['A2'] = "Areas in the City"

next_sheet['A3'] = "=index(AreaData!A2:AH,0,match(B1,AreaData!A1:C1,0))"


# Create xlsx file name from the python file name
import os
import sys
import re
filename = os.path.basename(sys.argv[0])
filename = re.sub(r'\.py$', '', filename)
wb.save(filename+'.xlsx')
