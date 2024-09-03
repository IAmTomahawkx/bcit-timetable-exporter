import time
import datetime
import random
import subprocess
from selenium.webdriver import Chrome, Firefox
from selenium.webdriver.common.by import By
import credentials

which = input("[~] Chrome (c) or firefox (f): ").lower()
if which.startswith("f"):
    driver = Firefox()

    if credentials.extensions:
        for x in credentials.extensions:
            driver.install_addon(x)
else:
    driver = Chrome()

ICS_PATH = "./calendar.ics"

with open("add_calendar_item.applescript") as f:
    SCRIPT = f.read()

def get_random_sleep():
    # so that bcit doesnt autoban us
    time.sleep(random.randint(3,6))

def _parse_one_time(t: str) -> tuple[int, int]:
    if len(t) == 3:
        # bcit is annoying in that when it's early morning, it doesn't include the leading 0
        # ie 0830 becomes 830
        # why? To fuck with you I guess
        hour = t[0]
        mins = t[1:]
    else:
        hour = t[:2]
        mins = t[2:]
    
    return int(hour), int(mins)

def parse_time(day: datetime.datetime, t: str) -> tuple[datetime.datetime, datetime.datetime]:
    start, end = t.split("-")
    start = _parse_one_time(start)
    end = _parse_one_time(end)

    start_dt = day.replace(hour=start[0], minute=start[1])
    end_dt = day.replace(hour=end[0], minute=end[1])
    return start_dt, end_dt
    

def login(start_url: str) -> bool:
    print("[!] We have been logged out. Attempting to log in.")

    try: # logged out path
        driver.find_element(
            By.XPATH,
            "/html/body/div/div[1]/table/tbody/tr/td[1]/table/tbody/tr[2]/td/p/a"
        ).click()
        get_random_sleep()

        username_field = driver.find_element(By.CLASS_NAME, "credentials_input_text")
        password_field = driver.find_element(By.CLASS_NAME, "credentials_input_password")

        username_field.send_keys(credentials.USERNAME)
        password_field.send_keys(credentials.PASSWORD)

        driver.find_element(By.CLASS_NAME, "credentials_input_submit").click()
        get_random_sleep()

    except: # templated sign-in path
        driver.find_element(By.ID, "userid").send_keys(credentials.USERID)
        driver.find_element(By.ID, "pwd").send_keys(credentials.PASSWORD)

        driver.find_element(By.ID, "button_sign-in").click()

        time.sleep(2)


    driver.get(start_url)
    time.sleep(2)

    if driver.current_url != start_url: # wtf?
        print(f"[!] BCIT refused to let us in. We are currently at {driver.current_url}")
        return False
    
    return True

def scrape_once(monday: datetime.datetime):
    print(driver.find_element(By.XPATH, "/html/body/div[3]/table[1]/tbody/tr/td[3]/span[1]").text)

    table = driver.find_element(By.CLASS_NAME, "datadisplaytable").find_element(By.XPATH, "tbody")

    for row_idx, row in enumerate(table.find_elements(By.XPATH, "*")):
        if row_idx == 0:
            continue # day labels
        
        row_cols = row.find_elements(By.XPATH, "*")

        row_has_header = row_cols[0].get_attribute("class") == "ddlabel" and row_cols[0].text.isnumeric()
        row_offset = int(row_has_header) * -1
        # the rows with time markers at the start get an extra element that the other rows dont... so we have to account for that
        # in our iterating

        for day, class_ in enumerate(row_cols):
            _txt = class_.text.strip()
            if not _txt or _txt.isnumeric(): # empty or time label
                continue

            date = monday + datetime.timedelta(day + row_offset)
            content = class_.text
            try:
                class_name, title, note, class_time, location = content.split("\n")
            except:
                print("[!] Could not parse the following text:")
                print(content)
            else:
                print(f"[-] Adding class {title} on {date.date()}")
                start, end = parse_time(date, class_time)
                template = SCRIPT.format(
                    _description=note,
                    _title=f"{class_name} | {title}",
                    _location=f"BCIT {location}",
                    _start=start.strftime("%m-%d-%Y %H:%M:00"), # damn yanks
                    _end=end.strftime("%m-%d-%Y %H:%M:00")
                )
                subprocess.run(["osascript", "-e", template])

def is_current_table_empty() -> bool:
    try:
        elem = driver.find_element(By.CLASS_NAME, "datadisplaytable")
    except: # BCIT stopped us for spam
        print("[!] BCIT logged us out. If it says there was an issue with your connection, you've been flagged for spam and should try again later.")
        raise SystemExit(-1)

    return elem.text == "No courses with assigned times this week."

def is_logged_out() -> bool:
    if driver.current_url == "https://id.bcit.ca/my.logout.php3":
        return True
    
    try:
        driver.find_element(By.ID, 'userid')
        driver.find_element(By.ID, "pwd")
        return True
    except:
        return False

def main():
    url_template = "https://bss.bcit.ca/owa_prod/bwskfshd.P_CrseSchd?start_date_in={0.month}/{0.day}/{0.year}"
    # americans and their awful date format strike again
    
    start = input(f"[~] If you want to skip to a specific week, enter it now (mm/dd/yyyy), otherwise enter nothing: ")
    if start.strip():
        _month, _day, _year = start.strip().split("/")
        this_monday = datetime.datetime(int(_year), int(_month), int(_day))
    else:
        now = datetime.datetime.now()
        this_monday = now - datetime.timedelta(days = now.weekday())

    url = url_template.format(this_monday)

    driver.get(url)

    get_random_sleep()

    if is_logged_out(): # logged out
        if not login(url):
            return
    
    if is_current_table_empty(): # current week is empty
        print("[!] This week is empty. Do you want to skip to the next semester? (enter y/n)")

        inp = input()
        if not inp or inp.lower().startswith("n"):
            print("[!] Exiting")
            return
        
        if 12 > this_monday.month > 6: # go to september
            this_monday = datetime.datetime(this_monday.year, 9, 7)
        elif this_monday.month == 12: # we're in december, get january
            this_monday = datetime.datetime(this_monday.year+1, 1, 7)
        else: # iunno, just grab january
            this_monday = datetime.datetime(this_monday.year, 1, 7)

        this_monday = this_monday + datetime.timedelta(-this_monday.weekday()) # first monday of the month
        print(f"[!] Navigating to {this_monday.date()}")
        driver.get(url_template.format(this_monday))
        get_random_sleep()
    
    monday = this_monday
    while not is_current_table_empty():
        scrape_once(monday)
        monday += datetime.timedelta(days=7)

        last_url = url
        url = url_template.format(monday)
        driver.get(url)
        if driver.current_url == last_url: # end of semester reached
            print("[~] Reached end of semester. Exiting")
            break
        
        get_random_sleep()

if __name__ == "__main__":
    main()