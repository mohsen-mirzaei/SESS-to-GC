from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from unidecode import unidecode
from pprint import pprint
import os
import calendar

USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")

# Replace the path with the path to your Chrome driver executable
driver = webdriver.Chrome()

# Open Sess
driver.get('https://sess.shirazu.ac.ir')
time.sleep(3)
uname = driver.find_element(By.XPATH, '//*[@id="edId"]')
uname.send_keys(USERNAME)
password = driver.find_element(By.XPATH, '//*[@id="edPass"]')
password.send_keys(PASSWORD)
submit_button = driver.find_element(By.XPATH, '//*[@id="edEnter"]')
submit_button.click()
time.sleep(3)
ed_list = driver.find_element(By.XPATH, '//*[@id="edList"]')
num_of_classes = len(ed_list.find_elements(By.XPATH, "*"))
classes = []
for i in range(1, num_of_classes + 1):
    class_name = driver.find_element(By.XPATH, f'//*[@id="edList"]/tr[{i}]/td[3]').text
    class_time = driver.find_element(By.XPATH, f'//*[@id="edList"]/tr[{i}]/td[8]').text.split(" و ")
    print("class_time:")
    pprint(class_time)
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
pprint(classes)

persian_weekdays = ['دو شنبه', 'سه شنبه', 'چهار شنبه', 'پنجشنبه', 'جمعه', 'شنبه', 'یک شنبه']
persian_weekdays_sorted = ['شنبه', 'يک شنبه', 'دو شنبه', 'سه شنبه', 'چهار شنبه', 'پنج ‌شنبه', 'جمعه']
english_weekdays = list(calendar.day_name)
print(calendar.day_name)
persian_to_english = dict(zip(persian_weekdays, english_weekdays))


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
                    print("sort by" + str(class_start_time) + "|" + line_data)
        weekday_classes = sorted(weekday_classes, key=lambda x: x['class_start_time'])
        for weekday_class in weekday_classes:
            file.write(weekday_class.get("line_data"))


# Close the browser window
driver.quit()
