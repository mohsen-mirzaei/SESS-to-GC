import csv
from unidecode import unidecode
import calendar
from selenium import webdriver
from selenium.webdriver.common.by import By
import datetime


driver = webdriver.Chrome()

# Open Sess
driver.get('https://sess.shirazu.ac.ir')

input("log in, navigate to your sess home page and then press enter...")

ed_list = driver.find_element(By.XPATH, '//*[@id="edList"]')
num_of_classes = len(ed_list.find_elements(By.XPATH, "*"))
classes = []
for i in range(1, num_of_classes + 1):
    class_name = driver.find_element(By.XPATH, f'//*[@id="edList"]/tr[{i}]/td[3]').text
    class_time = driver.find_element(By.XPATH, f'//*[@id="edList"]/tr[{i}]/td[8]').text.split(" و ")
    class_time_clean = []
    for item in class_time:
        hour_day = item.split(" - ")
        hour = []
        for i in hour_day[1].split(" "):
            i = unidecode(i)
            if i != "ly":
                hour.append(i)
        time_dic = {
            "day": hour_day[0],
            "hour": hour
        }
        class_time_clean.append(time_dic)
    classes.append({
        "class_name": class_name,
        "class_time": class_time_clean
    })

persian_weekdays = ['دو شنبه', 'سه شنبه', 'چهار شنبه', 'پنجشنبه', 'جمعه', 'شنبه', 'يک شنبه']
persian_weekdays_sorted = ['شنبه', 'يک شنبه', 'دو شنبه', 'سه شنبه', 'چهار شنبه', 'پنج ‌شنبه', 'جمعه']
english_weekdays = list(calendar.day_name)
persian_to_english = dict(zip(persian_weekdays, english_weekdays))


def next_weekday(d, weekday):
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0: # Target day already happened this week
        days_ahead += 7
    return d + datetime.timedelta(days_ahead)


week_events = []
for item in classes:
    class_name = item.get("class_name")
    for item2 in item.get("class_time"):
        date = next_weekday(datetime.datetime.today(), persian_weekdays.index(item2.get("day")))
        event = {"Subject": class_name,
                 "Start Date": date,
                 "Start Time": datetime.datetime.strptime(item2.get("hour")[0], "%H:%M").strftime("%I:%M %p"),
                 "End Date": date,
                 "End Time": datetime.datetime.strptime(item2.get("hour")[1], "%H:%M").strftime("%I:%M %p")
                 }
        week_events.append(event)


semester_events = []
for event in week_events:
    while event.get("Start Date") < datetime.datetime.today() + datetime.timedelta(days=200):
        cr_event = event.copy()
        cr_event["Start Date"] = cr_event["Start Date"].strftime("%m/%d/%Y")
        cr_event["End Date"] = cr_event["End Date"].strftime("%m/%d/%Y")
        semester_events.append(cr_event)
        event["Start Date"] = event.get("Start Date") + datetime.timedelta(weeks=1)
        event["End Date"] = event.get("End Date") + datetime.timedelta(weeks=1)

with open("sch.csv", 'w', encoding="utf-8") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=['End Date', 'End Time', 'Start Date', 'Start Time', 'Subject'])
    writer.writeheader()
    writer.writerows(semester_events)


with open("schedule.txt", "w", encoding="utf-8") as file:
    for weekday in persian_weekdays_sorted:
        weekday_classes = []
        file.write(weekday + "\n")
        for item in classes:
            for combo in item.get("class_time"):
                item_day = combo.get("day")
                if item_day == weekday:
                    line_data = item.get("class_name") + " * " + combo.get("hour")[0] + "-" + combo.get("hour")[1] + "\n"
                    class_start_time = int(combo.get("hour")[0].split(":")[0])
                    weekday_classes.append({
                        "class_start_time": class_start_time,
                        "line_data": line_data
                    })
        weekday_classes = sorted(weekday_classes, key=lambda x: x['class_start_time'])
        for weekday_class in weekday_classes:
            file.write(weekday_class.get("line_data"))


# Close the browser window
driver.quit()
