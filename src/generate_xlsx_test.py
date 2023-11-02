import unittest
from datetime import time

import openpyxl

from src.generate_pdf import convert_to_pdf
from src.generate_xlsx import fill_workbook_with_data_time_format, get_holidays_from_xmlcalendar


class MyTestCase(unittest.TestCase):
    def test_generating(self):
        template_path = "template.xlsx"
        workbook = openpyxl.load_workbook(template_path)
        # Fill the workbook with adjusted data
        weekly_schedule = {
            0: {'work_start': time(9, 00), 'lunch_start': time(12, 0), 'lunch_end': time(13, 0),
                'work_end': time(18, 00)},  # Понедельник
            1: {'work_start': time(8, 30), 'lunch_start': time(12, 0), 'lunch_end': time(13, 0),
                'work_end': time(17, 30)},  # Monday
            2: {'work_start': time(9, 00), 'lunch_start': time(12, 0), 'lunch_end': time(13, 0),
                'work_end': time(18, 00)},  # Sunday
            3: {'work_start': time(8, 30), 'lunch_start': time(12, 0), 'lunch_end': time(13, 0),
                'work_end': time(17, 30)},  # Monday
            4: {'work_start': time(9, 00), 'lunch_start': time(12, 0), 'lunch_end': time(13, 0),
                'work_end': time(18, 00)},  # Sunday
            5: {'work_start': time(8, 30), 'lunch_start': time(12, 0), 'lunch_end': time(13, 0),
                'work_end': time(17, 30)},  # Monday
            6: {'work_start': time(8, 30), 'lunch_start': time(12, 0), 'lunch_end': time(13, 0),
                'work_end': time(17, 30)},  # Monday

        }

        filled_workbook_adjusted = fill_workbook_with_data_time_format(workbook, 2023, 6,
                                                                       "Скипетров Алексей Сергеевич",
                                                                       "разработки программного обеспечения",
                                                                       get_holidays_from_xmlcalendar(2023),
                                                                       weekly_schedule,
                                                                       add_extra_minutes=True)

        # Save the filled workbook to a new file
        output_path_adjusted = "../generated/generated.xlsx"
        output_path_pdf = "../generated"
        filled_workbook_adjusted.save(output_path_adjusted)
        convert_to_pdf(output_path_adjusted, output_path_pdf, "C:\Program Files\LibreOffice\program\scalc.exe")


if __name__ == '__main__':
    unittest.main()
