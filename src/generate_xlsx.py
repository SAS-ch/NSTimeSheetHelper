import random
from datetime import time, datetime, date, timedelta

import openpyxl.styles.colors
import requests
from openpyxl.styles import PatternFill, NamedStyle, Color, Border, Side, borders, Font, Alignment

border = Border(
    left=Side(border_style=borders.BORDER_THIN, color='FF000000'),
    right=Side(border_style=borders.BORDER_THIN, color='FF000000'),
    top=Side(border_style=borders.BORDER_THIN, color='FF000000'),
    bottom=Side(border_style=borders.BORDER_THIN, color='FF000000')
)
bold_italic_font = Font(bold=True, italic=True, name='Arial')
center_alignment = Alignment(horizontal='center', vertical='center')

time_style = NamedStyle(
    name='time_style',
    number_format='hh:mm',
    border=border
)
just_border_style = NamedStyle(
    name='just_border_style',
    border=border
)
name_style = NamedStyle(
    name='sdf',
    font=bold_italic_font,
    alignment=center_alignment
)
MONTHS_RU = {
    1: "январь",
    2: "февраль",
    3: "март",
    4: "апрель",
    5: "май",
    6: "июнь",
    7: "июль",
    8: "август",
    9: "сентябрь",
    10: "октябрь",
    11: "ноябрь",
    12: "декабрь"
}

grey_fill = PatternFill(start_color="00D3D3D3", end_color="00D3D3D3", fill_type='solid')


def fill_workbook_with_data_time_format(workbook, year, month, employee_name, holidays_data, add_extra_minutes=False):
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

    # Get non-working days, reduced working days, and holidays for the given month
    non_working_days = holidays_data.get(month, {}).get("non_working_days", [])
    reduced_days = holidays_data.get(month, {}).get("holidays", [])

    sheet["A2"] = f"Табель учета рабочего времени за {MONTHS_RU[month]} {year} г."
    sheet["A2"].style = name_style
    # Fill the employee name

    sheet["D3"] = employee_name
    sheet["D3"].style = name_style

    from calendar import monthrange
    _, num_days = monthrange(year, month)

    # Define the working hours as datetime.time objects
    base_work_start = time(8, 30)
    base_lunch_start = time(12, 0)
    base_lunch_end = time(13, 0)
    base_work_end = time(17, 30)
    base_work_end_reduced = time(16, 30)  # For days with 1-hour reduction

    # ... [оставляем все как было]

    # Fill the days and working hours
    for day in range(1, num_days + 1):
        work_start = base_work_start
        lunch_start = base_lunch_start
        lunch_end = base_lunch_end
        work_end = base_work_end
        work_end_reduced = base_work_end_reduced

        if add_extra_minutes:
            extra_minutes = random.choice([5, 10, 15])
            work_start = (datetime.combine(date.today(), work_start) + timedelta(minutes=extra_minutes)).time()
            lunch_start = (datetime.combine(date.today(), lunch_start) + timedelta(minutes=extra_minutes)).time()
            lunch_end = (datetime.combine(date.today(), lunch_end) - timedelta(minutes=extra_minutes)).time()
            work_end = (datetime.combine(date.today(), work_end) - timedelta(minutes=extra_minutes)).time()
            work_end_reduced = (
                    datetime.combine(date.today(), work_end_reduced) - timedelta(minutes=extra_minutes)).time()

        row = day + 7  # Because the data starts from row 8
        sheet[f"A{row}"] = day
        sheet[f"A{row}"].style = just_border_style

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
            sheet[f"G{row}"].style = just_border_style
        else:
            # If it's a non-working day, color the row grey
            for col in ["B", "C", "D", "E", "F", "G"]:
                sheet[f"{col}{row}"].style = time_style
                sheet[f"{col}{row}"].fill = grey_fill

    # Clear remaining rows if month has less than 31 days
    for day in range(num_days + 1, 32):
        row = day + 7
        for col in ["A", "B", "C", "D", "E", "F"]:
            sheet[f"{col}{row}"] = ""
            sheet.row_dimensions[row].height = 0

    sheet["F39"].style = just_border_style  # lib bug
    sheet["G39"].style = just_border_style

    last_filled_row = 7 + num_days
    sheet["F39"].value = f"=SUM(F8:F{last_filled_row})*24"

    if num_days < 31:
        start_row_to_delete = 8 + num_days
        rows_to_delete = 31 - num_days
        sheet.delete_rows(start_row_to_delete, rows_to_delete)

    return workbook


def get_holidays_from_xmlcalendar(year):
    URL = f"https://xmlcalendar.ru/data/ru/{year}/calendar.json"
    response = requests.get(URL)
    data = response.json()

    holidays = {}
    for month_data in data["months"]:
        month = month_data["month"]
        days = month_data["days"].split(',')

        # Extracting the reduced days (days with *)
        reduced_days = [int(day.replace('*', '')) for day in days if '*' in day]
        # Extracting all non-working days (days without * and with +)
        non_working_days = [int(day.replace('+', '')) for day in days if '*' not in day]

        holidays[month] = {
            "non_working_days": non_working_days,
            "holidays": reduced_days  # Теперь "holidays" правильно указывает на сокращенные дни
        }

    return holidays
