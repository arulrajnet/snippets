from openpyxl import Workbook
from openpyxl.worksheet.datavalidation import DataValidation

wb = Workbook()
ws = wb.active
ws.title = "DataSource"

for number in range(1,100): #Generates 99 "ip" address in the Column A;
    ws['A{}'.format(number)].value= "192.168.1.{}".format(number)

data_val = DataValidation(type="list", formula1="='DataSource'!$A:$A")  # References column A in the DataSource sheet

next_sheet = wb.create_sheet('Dropdown')
next_sheet['A1'] = "Select IP Address"
# Add the data validation to the new sheet
next_sheet.add_data_validation(data_val)
data_val.add(next_sheet["B1"])

wb.save('Test.xlsx')
