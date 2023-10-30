from datetime import time

import requests
from openpyxl.styles import PatternFill, NamedStyle

time_style = NamedStyle(
    name='time_style',
    number_format='hh:mm'
)


# Todo пропадает табличка
# Todo выходной день не закрашивается серым

def fill_workbook_with_data_time_format(workbook, year, month, employee_name, holidays_data):
    """
    Fill the Excel workbook with the provided data and format cells as Time.

    Parameters:
    - workbook: the Excel workbook to fill
    - year: the year for the timetable
    - month: the month for the timetable
    - employee_name: the name of the employee
    - holidays_data: the data of holidays and non-working days

    Returns:
    - Modified workbook.
    """
    # Get the active sheet (assuming the template has only one sheet)
    sheet = workbook.active

    # Fill the employee name
    sheet["D3"] = employee_name

    # Define the working hours as datetime.time objects
    work_start = time(8, 0)
    lunch_start = time(12, 0)
    lunch_end = time(13, 0)
    work_end = time(17, 0)
    work_end_reduced = time(16, 0)  # For days with 1-hour reduction

    # Get the number of days in the month
    from calendar import monthrange
    _, num_days = monthrange(year, month)

    # Get non-working days, reduced working days, and holidays for the given month
    non_working_days = holidays_data.get(month, {}).get("non_working_days", [])
    reduced_days = holidays_data.get(month, {}).get("holidays", [])

    # Define the grey fill for non-working days
    grey_fill = PatternFill(start_color="D3D3D3", end_color="D3D3D3", fill_type="solid")

    # Fill the days and working hours
    for day in range(1, num_days + 1):
        row = day + 7  # Because the data starts from row 8
        sheet[f"A{row}"] = day

        if day not in non_working_days:
            sheet[f"B{row}"] = work_start
            sheet[f"B{row}"].style = time_style
            sheet[f"C{row}"] = lunch_start
            sheet[f"C{row}"].style = time_style
            sheet[f"D{row}"] = lunch_end
            sheet[f"D{row}"].style = time_style
            if day in reduced_days:
                sheet[f"E{row}"] = work_end_reduced
            else:
                sheet[f"E{row}"] = work_end
            sheet[f"E{row}"].style = time_style
            sheet[f"F{row}"].style = time_style
        else:
            # If it's a non-working day, color the row grey
            for col in ["A", "B", "C", "D", "E"]:
                sheet[f"{col}{row}"].fill = grey_fill

    # Clear remaining rows if month has less than 31 days
    for day in range(num_days + 1, 32):
        row = day + 7
        for col in ["A", "B", "C", "D", "E", "F"]:
            sheet[f"{col}{row}"] = None
            sheet[f"{col}{row}"] = PatternFill(fill_type=None)  # Clear any fills

    return workbook


def get_holidays_from_xmlcalendar(year):
    URL = f"https://xmlcalendar.ru/data/ru/{year}/calendar.json"
    response = requests.get(URL)
    data = response.json()

    holidays = {}
    for month_data in data["months"]:
        month = month_data["month"]
        days = month_data["days"].split(',')

        # Extracting only the holidays (days with *)
        holiday_days = [int(day.replace('*', '')) for day in days if '*' in day]
        # Extracting all non-working days (including holidays)
        non_working_days = [int(day.replace('*', '').replace('+', '')) for day in days]

        holidays[month] = {
            "non_working_days": non_working_days,
            "holidays": holiday_days
        }

    return holidays
