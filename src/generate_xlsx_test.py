import unittest

import openpyxl

from src.generate_xlsx import fill_workbook_with_data_time_format, get_holidays_from_xmlcalendar


class MyTestCase(unittest.TestCase):
    def test_generating(self):
        template_path = "template.xlsx"
        workbook = openpyxl.load_workbook(template_path)
        # Fill the workbook with adjusted data
        filled_workbook_adjusted = fill_workbook_with_data_time_format(workbook, 2023, 10,
                                                                       "Скипетров Алексей Сергеевич",
                                                                       get_holidays_from_xmlcalendar(2023),
                                                                       add_extra_minutes=True)

        # Save the filled workbook to a new file
        output_path_adjusted = "../generated/generated.xlsx"
        filled_workbook_adjusted.save(output_path_adjusted)


if __name__ == '__main__':
    unittest.main()
