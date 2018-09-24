import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
import lxml

HEBREW_ENCODING = "utf8"
SHNATON_URL = "http://shnaton.huji.ac.il/index.php"
SHNATON_HEADER_ANCHOR_TEXT = "מועדים מיוחדים"
SHNATON_HEADER_HOUR_TEXT = " שעה "
SHNATON_HEADER_TYPE_TEXT = "סוג שיעור"
SHNATON_HEADER_DATE_TEXT = "מועדים מיוחדים"
ICS_SUFFIX = ".ics"
FIXED_FILE_SUFFIX = "_fixed"


class ScheduleClass:
    def __init__(self, date, start_hour, type):
        self.date = date
        self.start_hour = start_hour
        self.type = type

    def is_possible_match(self, date, start_hour):
        if self.date:
            return self.start_hour == start_hour and self.date == date
        else:
            return self.start_hour == start_hour


def get_element_recursively_by_tag(anchor_element, tag_name):
    parent = anchor_element
    while not parent.name == tag_name:
        parent = parent.parent
    return parent


def get_working_date_from_shnaton_date(shnaton_date):
    try:
        return datetime.strptime(shnaton_date, "%d/%m/%y").date()
    except ValueError:
        return None


def get_course_page_as_soup(course_number,year):
    shnaton_requests_params = {"peula": "Simple", "year": year, "course": course_number}
    response = requests.post(SHNATON_URL, data=shnaton_requests_params)
    data = response.text
    return BeautifulSoup(data, "lxml")


def get_classes_for_course(course_number, year):
    soup = get_course_page_as_soup(course_number, year)
    table = get_element_recursively_by_tag(soup.find("th", text=SHNATON_HEADER_ANCHOR_TEXT), "table")
    header_row = table.find("tr")
    headers = header_row.find_all("th")

    hour_index = headers.index(header_row.find("th", text= SHNATON_HEADER_HOUR_TEXT))
    date_index = headers.index(header_row.find("th", text= SHNATON_HEADER_DATE_TEXT))
    type_index = headers.index(header_row.find("th", text= SHNATON_HEADER_TYPE_TEXT))

    classes_for_course = []

    for row in table.find_all("tr")[1:]:
        entries = row.find_all("td")
        if len(entries) > 1:
            class_type = entries[type_index].text
            class_times = entries[hour_index]
            for br in class_times.find_all("br"):
                br.replace_with("  ")
            class_start_times = [class_time[6:8] for class_time in class_times.text.split()]
            class_dates = entries[date_index].text.split()
            for i in range(len(class_start_times) - len(class_dates)):
                class_dates.append("")
            for i, class_start_time in enumerate(class_start_times):
                classes_for_course.append(
                    ScheduleClass(get_working_date_from_shnaton_date(class_dates[i]), class_start_time, class_type))
    return classes_for_course


def get_course_name_in_hebrew(course_number, year):
    soup = get_course_page_as_soup(course_number, year)
    table = get_element_recursively_by_tag(soup.find("td", class_= "courseTD textEng"), "table")
    td = table.find_all("td")[1]
    possible_b = td.find("b")
    if possible_b:
        return possible_b.string
    else:
        return td.text


def fix(file_contents, year, hadassah_start_times):
    classes_by_course_number = {}
    course_names_in_hebrew = {}
    content = [line.decode(HEBREW_ENCODING).strip('\n') for line in file_contents]
    for i in range(2, len(content) - 1, 6):
        course_number = content[i + 3].split(":")[1]
        course_start_time = content[i + 1].split(":")[1].split("T")[1][0:2]
        course_date = datetime.strptime(content[i + 1].split(":")[1].split("T")[0], "%Y%m%d").date()
        try:
            if not course_number in classes_by_course_number:
                classes_by_course_number[course_number] = get_classes_for_course(course_number, year)
            if not course_number in course_names_in_hebrew:
                course_names_in_hebrew[course_number] = get_course_name_in_hebrew(course_number, year)
            for possible_class in classes_by_course_number[course_number]:
                if possible_class.is_possible_match(course_date, course_start_time):
                    content[i + 3] = content[i + 3].split(":")[0] + ":" + possible_class.type + " - " + \
                                     course_names_in_hebrew[course_number]
                    if hadassah_start_times:
                        content[i+1] = (content[i+1])[:-4] + "15" + (content[i+1])[-2:]
                    break
        except AttributeError:
            pass
    return content

# file_name = input("Please enter the FULL path to the ORIGINAL ics file: ")
# year = input("Please enter the school year (E.g., for the school year 2018-19, enter 2019): ")
#     # "schedule.ics"
# updated_content = get_updated_file_content(file_name, year)
# fixed_file_path = os.path.abspath(file_name).split(ICS_SUFFIX)[0] + FIXED_FILE_SUFFIX + ICS_SUFFIX
# with open(fixed_file_path, "w+", encoding=HEBREW_ENCODING) as fixed_file:
#     fixed_file.write("\n".join(updated_content))
# print("Done. Updated file can be found at: "+fixed_file_path)
# input("Press enter to exit")