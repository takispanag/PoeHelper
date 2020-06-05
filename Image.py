from time import sleep,time
from tkinter import Tk
import re
import pyautogui
import cv2
import win32gui
import pyperclip
import numpy as np
import keyboard
import os
import sys
import concurrent.futures
from pygtail import Pygtail


def main():
    global stash_currency
    global buyer_in_hideout
    global currency_for_sale
    buyer_in_hideout = []
    stash_currency = {}
    currency_for_sale = {}
    focus_poe()
    # open_stash()
    # in_stash_currency()

    #listen on client.log thread
    # with concurrent.futures.ThreadPoolExecutor(1) as ex:
    #     results = ex.map(read_file,"F:/Games/POE/logs/Client.txt")
    #     print(results)
    executor_log = concurrent.futures.ThreadPoolExecutor(1)
    file_being_read = executor_log.submit(read_file, "F:/Games/POE/logs/Client.txt")

    #kill proccess when X pressed thread
    executor_kill = concurrent.futures.ThreadPoolExecutor(1)
    process_to_be_killed = executor_kill.submit(kill_process) 

    # logfile = open("F:/Games/POE/logs/Client.txt","r")
    # loglines = follow(logfile)
    # for line in loglines:
    #     print (line)

    #open_stash()
    #print(stash_currency)

    do_trade()

def do_trade():
    global stash_currency
    window = get_trade_window()
    # img_rgb = window[0] #focus only on trade
    # img_rgb = np.array(img_rgb)
    # img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
    # template = cv2.imread("images/chaosOrig.png", 0)

    # center_x = pt[0] + w/2
    # center_y = pt[1] + h/2
    cell_distance=30
    # trade_button_clickable = False
    # while not trade_button_clickable:
    for i in range(12):
        for j in range(5):
            position=[window[1] + (i*cell_distance), window[2] + (j*cell_distance)]
            pyautogui.moveTo(position[0], position[1])

            result = clipboard_manage()
            if result: #string not empty
                #get total currency
                item_info = get_item_info(result)
                print(item_info)
                if item_info[0] is None:
                    break
                elif item_info[0] == "currency":
                    currency_name = item_info[1]
                    stash_currency[currency_name] += item_info[2]
                #sleep(0.5)
    #cv2.imwrite('res.png', img_rgb)
    
    #get the total currency number and name that was found in the trade
    in_trade_currency = {}
    for key, value in stash_currency.items():
        if value>0:
            in_trade_currency[key]=value
    print("Total  currencies found in trade: ",in_trade_currency)
   
    #testing function to accept trade if items found in trade are enough and then hit accept
    # for key,value in in_trade_currency.items():
    #     if(key == "Orb of Fusing" and value>1000):
    #         #click trade button if trade requirements are met
    #         found = False      
    #         #while trade button not clickable
    #         while not found:
    #             try:
    #                 tradeButton = pyautogui.center(pyautogui.locateOnScreen('images/tradeAccept.png'))
    #                 sleep(0.5)
    #                 pyautogui.click(pyautogui.moveTo(int(tradeButton[0]),int(tradeButton[1])+10))
    #                 found = True
    #             except:
    #                 pass
    #             #sleep between tries to accept trade
    #             sleep(1)

def get_item_info(string):
    #curr_list = all_currencies
    #item_name = print(re.search("\n(.*)\n-",string).group(1))#get item name
    item_name = string
    if any(word in item_name for word in curr_list): #if found currency is in my currency list find stack and the name
        category = "currency"
        curr_number = re.findall("\d+\/\d+", string)[0].split("/")[0] #find number of stack
        curr_name = re.search("\n(.*)\n-",string).group(1) #find currency name
    else: # if any other item or currency i don't want return other -1 not currency
        category = "other"
        curr_number = -1
        curr_name = "not currency"
    print("Item category: "+category+" currency name: "+curr_name+" number: ",(int(curr_number)))
    return [category,curr_name,int(curr_number)]

def get_trade_window():
    #Only trade window in image
    topLeft = pyautogui.locateOnScreen('images/topLeft.png')
    bottomRight = pyautogui.locateOnScreen('images/bottomRight.png')
    topLeftP = pyautogui.center(topLeft)
    bottomRightP = pyautogui.center(bottomRight)
    img = pyautogui.screenshot(region=(topLeftP[0], topLeftP[1]+20, (bottomRightP[0]-topLeftP[0])+10, (bottomRightP[1]-topLeftP[1])-20))
    img.save("trade_window.png")
    return [img, topLeftP[0]+20, topLeftP[1]+35] #image, first cell in trade window(x,y)

def log_regex_match(line):
    try:
        line_trade = re.search("(.*)@From (.*): Hi, I'd like to buy your (.*) for my (.*) in (.*)",line).groups()
        if line_trade is not None:
            #take all the needed arguments from the (.*)
            #get buyer_name from full username and guild. Example: <"UJ"> DoTMadness I only get DoTMadness
            buyer_name = get_name(line_trade[1])
            my_currency = line_trade[2]
            their_currency = line_trade[3]
            #if requirements met
            #trade_requirements(my_currency,their_currency)
            #send_invite(buyer_name,line)
            print("Buyer: "+buyer_name+" currency: "+their_currency+" for my: "+my_currency)
            trade_requirements(buyer_name,their_currency,my_currency)
    except:
        pass

    try:
        line_joined = re.search("^(?:[^ ]+ ){6}(\d+)\] : (.*?) has joined the area.*",line).groups()
        if line_joined is not None:
            print("Player: "+get_name(line_joined[1])+" has joined the area.")
            return ['joined']
    except:
        pass

    try:
        line_left = re.search("^(?:[^ ]+ ){6}(\d+)\] : (.*?) has left the area.*",line).groups()
        if line_left is not None:
            print("Player: "+get_name(line_left[1])+" has left the area.")
            return ['left']
    except:
        pass
    
# def trade_requirements(buyer,their_currency,my_currency):
#     if()

def get_name(full_name):
    name_tuple = full_name.split(' ')
    if len(name_tuple)<2: #user is not in a guild so first argument is the name
        name = name_tuple[0]
    else:                       #user is in a guild so first argument is the name
        name = name_tuple[1]
    return name

def open_stash():
    #open stash and click on first tab. It has to be the currency tab
    focus_poe()
    stash_opened = False
    while not stash_opened:
        try:
            stash_open = pyautogui.locateOnScreen("images/currency/stash_open.png", confidence=.9)
            if stash_open is not None:
                print("Stash is open")
                stash_arrow = pyautogui.center((pyautogui.locateOnScreen("images/currency/stash_left_arrow.png", confidence=.9)))
                if stash_arrow is not None:
                    #click on the first tab, search for the arrow next to it
                    pyautogui.click(pyautogui.moveTo(stash_arrow[0]+30, stash_arrow[1]))
                    print("Click on first Tab")
                stash_opened = True
            else:
                print("Stash not open, searching for stash")
                stash = pyautogui.locateOnScreen("images/currency/stash.png", confidence=.9)
                if stash is not None:
                    print("Stash found")
                    pyautogui.click(pyautogui.moveTo(pyautogui.center(stash)))
        except:
            pass
    
def trade_accepted(line):
    if "Trade accepted." in line:
        print("Trade accepted.")
        return True
    elif "Trade cancelled." in line:
        print("Trade cancelled.")
        return False
    
def send_trade(buyer,line):
    focus_poe()
    trade_command = ("/tradewith " +buyer)
    pyautogui.press("enter")
    pyautogui.typewrite(trade_command)
    pyautogui.press("enter")
    print("Sent trade request to: "+buyer)

def send_invite(buyer):
    focus_poe()
    invite_command = ("/invite "+buyer)
    pyautogui.press("enter")
    pyautogui.typewrite(invite_command)
    pyautogui.press("enter")
    print("Invite sent to : ",buyer)

def clipboard_manage():
    clipboard = pyperclip.copy('') # empty the string
    #ctrl c
    keyboard.press_and_release('ctrl+c')
    #get clipboard content
    try:
        clipboard = Tk().clipboard_get()
    except:
        clipboard = None
    return clipboard

def focus_poe():
    #focus poe
    try:
        hwnd = win32gui.FindWindow(None, 'Path of Exile')
        win32gui.SetForegroundWindow(hwnd)
        win32gui.ShowWindow(hwnd, 9)
        win32gui.MoveWindow(hwnd, -7, 0, 500, 500, True)
    except:
        print("Path of Exile not open! Please open it and run again.")
        sys.exit()

def read_file(filepath):
    #delete offset if exist from last run
    try:
        os.remove("log.offset")
    except OSError:
        pass

    while True:
        for line in Pygtail(filepath, every_n=1, read_from_end=True, full_lines=True, offset_file='log.offset'):
            print(line)
            log_regex_match(line)

def kill_process():
    #If i press X the proccess and the threads are killed
    while True:
        if keyboard.is_pressed('x'):
            os._exit(1)
            print("You pressed X process killed.")

def in_stash_currency():
    global stash_currency
    global currency_for_sale
    focus_poe()
    space = 32
    for i in range (0,3): 
        pyautogui.moveTo(35 + (i*space),155)
        clipboard = clipboard_manage()
        try:
            currency_name = re.search("\n(.*)\n-",clipboard).group(1)
            currency_number = re.findall("\d+\/\d+", clipboard)[0].split("/")[0]
            stash_currency[currency_name] = currency_number
            currency_price = re.search("~price (.*)",clipboard).group(1)
            currency_for_sale[currency_name] = currency_price 
            
        except:
            pass
    
    for i in range (0,5):
        pyautogui.moveTo(205 + (i*space),155)
        clipboard = clipboard_manage()
        try:
            currency_name = re.search("\n(.*)\n-",clipboard).group(1)
            currency_number = re.findall("\d+\/\d+", clipboard)[0].split("/")[0]
            stash_currency[currency_name] = currency_number
            currency_price = re.search("~price (.*)",clipboard).group(1)
            currency_for_sale[currency_name] = currency_price
        except:
            pass

    for i in range (0,2):
        for j in range (0,4):
            pyautogui.moveTo(35 + (j*space),195 + (i*space))
            clipboard = clipboard_manage()
            try:
                currency_name = re.search("\n(.*)\n-",clipboard).group(1)
                currency_number = re.findall("\d+\/\d+", clipboard)[0].split("/")[0]
                stash_currency[currency_name] = currency_number
                currency_price = re.search("~price (.*)",clipboard).group(1)
                currency_for_sale[currency_name] = currency_price
            except:
                pass
    
    for i in range (0,2):
        for j in range (0,2):
            pyautogui.moveTo(165 + (j*space),195 + (i*space))
            clipboard = clipboard_manage()
            try:
                currency_name = re.search("\n(.*)\n-",clipboard).group(1)
                currency_number = re.findall("\d+\/\d+", clipboard)[0].split("/")[0]
                stash_currency[currency_name] = currency_number
                currency_price = re.search("~price (.*)",clipboard).group(1)
                currency_for_sale[currency_name] = currency_price
            except:
                pass

    for i in range (0,2):
        for j in range (0,4):
            pyautogui.moveTo(240 + (j*space),195 + (i*space))
            clipboard = clipboard_manage()
            try:
                currency_name = re.search("\n(.*)\n-",clipboard).group(1)
                currency_number = re.findall("\d+\/\d+", clipboard)[0].split("/")[0]
                stash_currency[currency_name] = currency_number
                currency_price = re.search("~price (.*)",clipboard).group(1)
                currency_for_sale[currency_name] = currency_price
            except:
                pass
    
    for i in range (0,3): 
        pyautogui.moveTo(65 + (i*space), 265)
        clipboard = clipboard_manage()
        try:
            currency_name = re.search("\n(.*)\n-",clipboard).group(1)
            currency_number = re.findall("\d+\/\d+", clipboard)[0].split("/")[0]
            stash_currency[currency_name] = currency_number
            currency_price = re.search("~price (.*)",clipboard).group(1)
            currency_for_sale[currency_name] = currency_price
        except:
            pass

    for i in range (0,2): 
        pyautogui.moveTo(95 + (i*space), 295)
        clipboard = clipboard_manage()
        try:
            currency_name = re.search("\n(.*)\n-",clipboard).group(1)
            currency_number = re.findall("\d+\/\d+", clipboard)[0].split("/")[0]
            stash_currency[currency_name] = currency_number
            currency_price = re.search("~price (.*)",clipboard).group(1)
            currency_for_sale[currency_name] = currency_price
        except:
            pass

    for i in range (0,2):
        for j in range (0,4):
            pyautogui.moveTo(240 + (j*space),265 + (i*space))
            clipboard = clipboard_manage()
            try:
                currency_name = re.search("\n(.*)\n-",clipboard).group(1)
                currency_number = re.findall("\d+\/\d+", clipboard)[0].split("/")[0]
                stash_currency[currency_name] = currency_number
                currency_price = re.search("~price (.*)",clipboard).group(1)
                currency_for_sale[currency_name] = currency_price
            except:
                pass

    for i in range (0,2):
        for j in range (0,3):
            pyautogui.moveTo(65 + (j*space),340 + (i*space))
            clipboard = clipboard_manage()
            try:
                currency_name = re.search("\n(.*)\n-",clipboard).group(1)
                currency_number = re.findall("\d+\/\d+", clipboard)[0].split("/")[0]
                stash_currency[currency_name] = currency_number
                currency_price = re.search("~price (.*)",clipboard).group(1)
                currency_for_sale[currency_name] = currency_price
            except:
                pass

    #awakeners orb
    pyautogui.moveTo(185, 365)
    clipboard = clipboard_manage()
    try:
        currency_name = re.search("\n(.*)\n-",clipboard).group(1)
        currency_number = re.findall("\d+\/\d+", clipboard)[0].split("/")[0]
        stash_currency[currency_name] = currency_number
        currency_price = re.search("~price (.*)",clipboard).group(1)
        currency_for_sale[currency_name] = currency_price
    except:
        pass

    for i in range (0,2):
        for j in range (0,3):
            pyautogui.moveTo(240 + (j*space),335 + (i*space))
            clipboard = clipboard_manage()
            try:
                currency_name = re.search("\n(.*)\n-",clipboard).group(1)
                currency_number = re.findall("\d+\/\d+", clipboard)[0].split("/")[0]
                stash_currency[currency_name] = currency_number
                currency_price = re.search("~price (.*)",clipboard).group(1)
                currency_for_sale[currency_name] = currency_price
            except:
                pass

    for i in range (0,2):
        for j in range (0,7):
            pyautogui.moveTo(85 + (j*space),405 + (i*space))
            clipboard = clipboard_manage()
            try:
                currency_name = re.search("\n(.*)\n-",clipboard).group(1)
                currency_number = re.findall("\d+\/\d+", clipboard)[0].split("/")[0]
                stash_currency[currency_name] = currency_number
                currency_price = re.search("~price (.*)",clipboard).group(1)
                currency_for_sale[currency_name] = currency_price
            except:
                pass
    print(stash_currency)
    print(currency_for_sale)

if __name__ == "__main__":
    main()
