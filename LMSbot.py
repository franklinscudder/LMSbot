
"""

A script to automatically book Imperial LMS practise room slots.

Written for Python >= 3.8

Tom Findlay, 22/2/22.
www.github.com/franklinscudder

Released under MIT Software License.

"""



import requests as r
import datetime as dt
from time import sleep

def start():
    banner = r"""
    _______________________________________________________________________________
    
    
    88           88b           d88   ad88888ba   88                                
    88           888b         d888  d8"     "8b  88                         ,d     
    88           88`8b       d8'88  Y8,          88                         88     
    88           88 `8b     d8' 88  `Y8aaaaa,    88,dPPYba,    ,adPPYba,  MM88MMM  
    88           88  `8b   d8'  88    `""'""8b,  88P'    "8a  a8"     "8a   88     
    88           88   `8b d8'   88          `8b  88       d8  8b       d8   88     
    88           88    `888'    88  Y8a     a8P  88b,   ,a8"  "8a,   ,a8"   88,    
    88888888888  88     `8'     88   "Y88888P"   8Y"Ybbd8"'    `"YbbdP"'    "Y888
    
    
    by Tom Findlay 
    ______________________________________________________________________________
    """
    
    welcome = """    Welcome to LMSbot. 
    
    To find a slot ID, hover over a link in the calendar page and you'll see something like
    'https://www.union.ic.ac.uk/arts/jazzrock/bookings/slot/103-0' in the bottom left. 
    The slots on the calendar page are numbered in chronological order starting with 0. 
    The end of the URL you see is the slot ID with '-0' added on the end. 
    Count along to the desired slot from any bookable slot to calculate the target ID(s). 
    Enter these below, separated by commas and let the bot do it's thing.
    
    BEWARE - Slot IDs will change at the end of each week as the calendar rolls over.
    """

    print(banner)
    print(welcome)

def init():
    target_slots = [s.strip() for s in input("      Enter target slot ids e.g. '75, 76, 77': ").split(",")]
    
    lms_user = input("      Enter LMS username: ")
    lms_pass = input("      Enter LMS password: ")
    print()
    
    s = r.Session()
    res = s.post("https://www.union.ic.ac.uk/arts/jazzrock/user", data={"name":lms_user, "pass":lms_pass, "form_build_id":"form-Quz0idTacAYGlTH-BEUH5zHoCiqqVmfnuhcnR32LtdM", "form_id":"user_login", "op":"Log in"})
    print(f"INIT> Response code: {res.status_code} - {res.reason}")
    
    if len(s.cookies) == 0:
        print("FAIL> Log in unsuccessful!")
        s, target_slots = init()
    
    else:
        expiry = dt.datetime.fromtimestamp(next(x for x in s.cookies).expires)
        print(f"INIT> Session cookie obtained, will expire at {expiry}")
    
    return s, target_slots
    
def main(s, target_slots):

    book_url_base = "https://www.union.ic.ac.uk/arts/jazzrock/bookings/book/"
    slot_url_base = "https://www.union.ic.ac.uk/arts/jazzrock/bookings/slot/"
    
    now = dt.datetime.now()
    mins = now.minute
    print(f"INFO> Currently {mins} mins past, will attempt to book in ~{60-mins} mins.")
    
    while mins < 1 or mins > 59:
        for slot in target_slots:
            print(f"INFO> Trying to access slot {slot}...")
            
            res = s.get(slot_url_base + slot + "-0")
            slot_ID = res.url.split(r"/")[-1]
            
            if slot_ID == "0":
                print(f"INFO> Slot {slot} currently not bookable.")
            
            else:
                print(f"INFO> Mystical slot number is: {slot_ID}...")
                print(f"BOOK> Trying to book slot {slot}...")
            
            res = s.get(book_url_base + slot_ID)
            
            if "Room slot successfully booked." in res.text:
                target_slots.remove(slot)
                print(f"BOOK> Successfully booked slot {slot}!")
                if len(target_slots) == 0:
                    s.close()
                    return True
                    
            else:
                print(f"FAIL> Failed booking slot {slot}!")
    
        sleep(0.5)
        now = dt.datetime.now()
        mins = now.minute
        
    else:
        sleep(55)
  
    return False

if __name__ == "__main__":
    success = False
    start()
    s, target_slots = init()
    print("INIT> Bot initialised, running...")
    while not success:
        success = main(s, target_slots)
        sleep(1)
        
    print("SUCCESS! THANKS FOR USING LMSbot!")