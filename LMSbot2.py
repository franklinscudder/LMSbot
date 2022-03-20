
"""

A script to automatically book Imperial LMS practise room slots.

Version 2.1

Written for Python >= 3.8

Tom Findlay, 18/3/22.
www.github.com/franklinscudder

Released under MIT Software License.

"""



import requests as r
import datetime as dt
from time import sleep
from bs4 import BeautifulSoup as bs

def start():
    banner = r"""
    _______________________________________________________________________________
    
    V2 V2 V2 V2 V2 V2 V2 V2 V2 V2 V2 V2 V2 V2 V2 V2 V2 V2 V2 V2 V2 V2 V2 V2 V2 V2
    
    88           88b           d88   ad88888ba   88                                
    88           888b         d888  d8"     "8b  88                         ,d     
    88           88`8b       d8'88  Y8,          88                         88     
    88           88 `8b     d8' 88  `Y8aaaaa,    88,dPPYba,    ,adPPYba,  MM88MMM  
    88           88  `8b   d8'  88    `""'""8b,  88P'    "8a  a8"     "8a   88     
    88           88   `8b d8'   88          `8b  88       d8  8b       d8   88     
    88           88    `888'    88  Y8a     a8P  88b,   ,a8"  "8a,   ,a8"   88,    
    88888888888  88     `8'     88   "Y88888P"   8Y"Ybbd8"'    `"YbbdP"'    "Y888
    
    V2 V2 V2 V2 V2 V2 V2 V2 V2 V2 V2 V2 V2 V2 V2 V2 V2 V2 V2 V2 V2 V2 V2 V2 V2 V2 
    
    by Tom Findlay 
    ______________________________________________________________________________
    """
    
    welcome = """    Welcome to LMSbot. 
    
    Enter the date and start times you want as specified, the bot will wait until 
    exactly one week before the slot times and then spam the booking link. 
    
    You can make a file 'creds.py' defining strings USERNAME and PASSWORD in the
    script directory to avoid having to enter these each time (this is not secure
    but helpful if you use this tool a lot). There is a template for this file in 
    the GitHub repo.
    
    Good luck and happy sniping...  
    
    """

    print(banner)
    print(welcome)

def init():
    target_date = dt.datetime.strptime(input("      Enter the target date e.g. '15/3/22': ").strip(), "%d/%m/%y").date()
    raw_times = input("      Enter target slot start times e.g. '11, 12, 13': ").split(",")
    
    if any([int(x) > 22 or int(x) < 9 for x in raw_times]):
        print("FAIL> Slot times must be integers between 9 and 22 inclusive.")
        quit()
    
    target_times = [dt.datetime.strptime(t.strip(), "%H").time() for t in raw_times]
    
    try:
        from creds import USERNAME, PASSWORD
        print("\nINIT> Credentials imported successfully.")
    except ImportError:
        print("\n      No creds.py file found:")
        USERNAME, PASSWORD = False, False
        print()
    
    lms_user = USERNAME if USERNAME else input("      Enter LMS username: ")
    lms_pass = PASSWORD if PASSWORD else input("      Enter LMS password: ")
    
    
    s = r.Session()
    res = s.post("https://www.union.ic.ac.uk/arts/jazzrock/user", data={"name":lms_user, "pass":lms_pass, "form_build_id":"form-Quz0idTacAYGlTH-BEUH5zHoCiqqVmfnuhcnR32LtdM", "form_id":"user_login", "op":"Log in"})
    print(f"INIT> Response code: {res.status_code} - {res.reason}")
    
    if len(s.cookies) == 0:
        print("FAIL> Log in unsuccessful!")
        s, target_slots = init()
    
    else:
        expiry = dt.datetime.fromtimestamp(next(x for x in s.cookies).expires)
        print(f"INIT> Session cookie obtained, will expire at {expiry}")
    
    return s, target_date, target_times
    
def get_date_suffix(myDate):
    date_suffix = ["th", "st", "nd", "rd"]

    if myDate % 10 in [1, 2, 3] and myDate not in [11, 12, 13]:
        return date_suffix[myDate % 10]
    else:
        return date_suffix[0]

def handle_calendar(s, target_date, target_time):
    calendar_response = s.get(r"https://www.union.ic.ac.uk/arts/jazzrock//bookings/calendar/0")
    calendar = calendar_response.text
    print(f"INFO> Calendar page response code: {calendar_response.status_code} - {calendar_response.reason}")
    calendar_soup = bs(calendar, features="lxml")
    
    date_str = target_date.strftime("%b ") + target_date.strftime("%d").lstrip("0") + get_date_suffix(target_date.day)
    date_td = calendar_soup.find( lambda td: td.name=="td" and date_str in td.text )
    
    if date_td is None:
        print(f"FAIL> Cannot find a the date {target_date} in the calendar.")
        quit()
    
    time_str = target_time.strftime("%H:%M") + " -"
    slot_span = date_td.find( lambda span: span.name=="span" and time_str in span.text )
    
    if slot_span["class"] != ["room-slot"]:
        return slot_span["class"]
        
    return r"https://www.union.ic.ac.uk" + slot_span.a["href"]
    
def handle_booking(s, slot_url):
    booking_response = s.get(slot_url)
    print(f"INFO> Booking page response code: {booking_response.status_code} - {booking_response.reason}")
    booking_soup = bs(booking_response.text, features="lxml")
    print(f"BOOK> Slot page found at {slot_url}, attempting to book...")
    booking_a = booking_soup.find(lambda a: a.name=="a" and "bookings/book" in a["href"])
    booking_url = r"https://www.union.ic.ac.uk" + booking_a["href"]
    return s.get(booking_url)
    
def main():
    start()
    s, target_date, target_times = init()
    go_date = target_date - dt.timedelta(weeks=1)
    
    outcome_dict = {target_time : "Did not attempt booking." for target_time in target_times}
    
    print(f"INIT> Will try to book the following time slots on {target_date}:\n")
    for t in target_times:
        print(f"     - {t}")
    print()
    if dt.datetime.now() < dt.datetime.combine(go_date, min(target_times)):
        print(f"INFO> Waiting until {min(target_times)} on {go_date} to start trying to book.")
    
    while True:
        date_time = dt.datetime.now()
        date, time = date_time.date(), date_time.time()

        if date >= go_date: # or 1: 
        
            for target_time in target_times:
                time_to_slot = dt.datetime.combine(go_date, target_time) - date_time
                
                if time_to_slot < dt.timedelta(seconds=30) :# or 1:  
                    slot_url = handle_calendar(s, target_date, target_time)
                    
                    if type(slot_url) == list:
                        if "own" in slot_url:
                            print("FAIL> Cannot book, slot already owned by user.")
                            target_times.remove(target_time)
                            outcome_dict[target_time] = "Not booked, already owned by user."
                        elif "unbookable" in slot_url:
                            print("FAIL> Cannot book, slot marked as unbookable.")
                            target_times.remove(target_time)
                            outcome_dict[target_time] = "Not booked, unbookable."
                        elif "future" in slot_url:
                            print("FAIL> Cannot book, slot not available yet.")
                        elif "past" in slot_url:
                            print("FAIL> Cannot book, slot has passed.")
                            target_times.remove(target_time)
                            outcome_dict[target_time] = "Not booked, slot has passed."
                        elif "booked" in slot_url:
                            print("FAIL> Cannot book, slot has been booked by someone else.")
                            target_times.remove(target_time)
                            outcome_dict[target_time] = "Not booked, already taken."
                        else:   
                            print(f"FAIL> Cannot book, slot marked as: {slot_url}")
                            target_times.remove(target_time)
                            outcome_dict[target_time] = f"Not booked, {slot_url}."
                    
                    else:
                        final_response = handle_booking(s, slot_url)
                        
                        if "Room slot successfully booked." in final_response.text:
                            print(f"BOOK> Booked slot at {target_time} on {target_date}!")
                            target_times.remove(target_time)
                            outcome_dict[target_time] = "Successfully Booked."
                            print(f"INFO> Waiting until {min(target_times)} to book the next slot.")
                    
                    
            if len(target_times) == 0:
                print(f"DONE> Booking summary for slots on {target_date}:\n")
                for time in outcome_dict:
                    print(f"     - Slot at {time}: {outcome_dict[time]}")
                    
                return
                    
        
    
if __name__ == "__main__":
    main()
    print("\n>>>>> Booking complete <<<<<")