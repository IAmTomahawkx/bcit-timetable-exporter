# BCIT schedule exporter
This script exports your BCIT schedule from the website into your Apple Calendar using selenium and AppleScript.

#### To run:
- Before anything, open the Calendar app and create a calendar called "School". That's where this script will dump the contents.
- Download this repo by clicking the green `<> Code` button and pressing "Download ZIP".
- Install Python @ https://python.org
- copy `credentials.example.py` into `credentials.py` and fill out your BCIT username (usually your email), your BCIT student ID, and your password. 
    All 3 are needed since BCIT has two different login portals, one takes a student ID and the other takes a username. Which one it offers you depends on... well if you figure it out, do let me know.
- Open a console window
- Using python 3 (I used 3.12 when making this but it should work on any recent version), install the requirements (replace 3.12 with whatever version you're using):
    `python3.12 -m pip install -r requirements.txt`
- Once the requirements are installed, run the script (replace 3.12 if needed again):
    `python3.12 main.py`
- It will prompt you to pick chrome or firefox
- After that, you'll be prompted to either enter a date (it MUST be a monday, since that's how the BCIT timetable system works), or to enter nothing. Usually you should just press enter here, but if it crashes (due to antispam or something), you can enter the week to resume from, and then press enter.
- Assuming you didn't enter a date, it will load the current week. If class is not in session, it will ask you to skip to the next semester.
- Your computer will likely prompt you to allow the script to add events to the calendar.
- You will see a lot of notices in the console of events being added to the calendar. They're just there as info, they don't mean anything.
- ~~At the end of the semester, you'll see a notice in the console telling you so, and the script will exit. At this point the browser window will close, and the process should be done.~~ Just kidding right now it will go forever, so stop it once it finishes the semester


### Is this allowed by BCIT?
Absolutely not! Unfortunately they also have not provided this basic feature so here we are. Use at your own risk.