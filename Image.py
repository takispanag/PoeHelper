from time import sleep,time
from tkinter import Tk
import re
import pyautogui
import cv2
import win32gui
import pyperclip
import numpy as np
import keyboard
from currencies import *
import os
import sys
import concurrent.futures

def main():
    #focus poe
    try:
        hwnd = win32gui.FindWindow(None, 'Path of Exile')
        win32gui.SetForegroundWindow(hwnd)
        win32gui.ShowWindow(hwnd, 9)
        win32gui.MoveWindow(hwnd, -7, 0, 500, 500, True)
    except:
        print("Path of Exile not open! Please open it and run again.")
        sys.exit()
    
    #listen on client.log thread
    executor_log = concurrent.futures.ThreadPoolExecutor(1)
    #file_ret = read_file[0]
    future_file = executor_log.submit(read_file, "F:/Games/POE/logs/Client.txt")

    #kill proccess when X pressed thread
    executor_kill = concurrent.futures.ThreadPoolExecutor(1)
    process_to_be_killed = executor_kill.submit(kill_process) 

    # logfile = open("F:/Games/POE/logs/Client.txt","r")
    # loglines = follow(logfile)
    # for line in loglines:
    #     print (line)

    sleep(2)
    #do_trade()

def do_trade():
    window = get_trade_window()
    # img_rgb = window[0] #focus only on trade
    # img_rgb = np.array(img_rgb)
    # img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
    # template = cv2.imread("images/chaosOrig.png", 0)

    # center_x = pt[0] + w/2
    # center_y = pt[1] + h/2
    cell_distance=30
    for i in range(8):
        for j in range(5):
            position=[window[1] + (i*cell_distance), window[2] + (j*cell_distance)]

            result=pyperclip.copy('') # empty the string

            pyautogui.moveTo(position[0], position[1])
            #ctrl c
            #pyautogui.hotkey('ctrl', 'c')
            keyboard.press_and_release('ctrl+c')
            # pyautogui.keyDown('ctrl')
            # pyautogui.keyDown('c')
            # pyautogui.keyUp('c')
            # pyautogui.keyUp('ctrl')
            #get clipboard content
            try:
                result = Tk().clipboard_get()
            except:
                selection = None
            if result: #string not empty
                #get total currency
                item_info= get_info(result)
                print(item_info)
                if item_info[0] is None:
                    break
                elif item_info[0] == "currency":
                    currency_name = item_info[1]
                    currency_trading[currency_name] += item_info[2]
                #sleep(0.5)
    #cv2.imwrite('res.png', img_rgb)
    
    #get the total currency number and name that was found in the trade
    in_trade_currency = {}
    for key, value in currency_trading.items():
        if value>0:
            in_trade_currency[key]=value
    print("Total  currencies found in trade: ",in_trade_currency)
   
    #testing function to accept trade if items found in trade are enough and then hit accept
    for key,value in in_trade_currency.items():
        if(key == "Orb of Fusing" and value>1000):
            #click trade button if trade requirements are met
            found=False      
            #while trade button not clickable
            while not found:
                try:
                    tradeButton = pyautogui.center(pyautogui.locateOnScreen('images/tradeAccept.png'))
                    sleep(0.5)
                    pyautogui.click(pyautogui.moveTo(int(tradeButton[0]),int(tradeButton[1])+10))
                    found = True
                except:
                    pass
                #sleep between tries to accept trade
                sleep(1)

def get_info(string):
    curr_list = all_currencies
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
    print(category,curr_name,int(curr_number))
    return [category,curr_name,int(curr_number)]

def read_file(filepath):
    logfile = open(filepath)
    loglines = follow(logfile)
    for line in loglines:
        return [line,log_parser(line)] #i added log_parser(line) so normal function was return line

def get_trade_window():
    #Only trade window in image
    topLeft = pyautogui.locateOnScreen('images/topLeft.png')
    bottomRight = pyautogui.locateOnScreen('images/bottomRight.png')
    topLeftP = pyautogui.center(topLeft)
    bottomRightP = pyautogui.center(bottomRight)
    img = pyautogui.screenshot(region=(topLeftP[0], topLeftP[1]+20, (bottomRightP[0]-topLeftP[0])+10, (bottomRightP[1]-topLeftP[1])-20))
    img.save("trade_window.png")
    return [img, topLeftP[0]+20, topLeftP[1]+35] #image, first cell in trade window(x,y)

def follow(thefile):
    '''generator function that yields new lines in a file
    '''
    # seek the end of the file
    thefile.seek(0, 2)
    
    # start infinite loop
    while True:
        # read last line of file
        line = thefile.readline()        # sleep if file hasn't been updated
        if not line:
            sleep(0.1)
            continue

        yield line

def log_parser(sell_pm):
    pm = """2020/05/04 20:51:19 41618171 acf [INFO Client 7200] @From <"UJ"> DoTMadness: Hi, I'd like to buy your 56 Orb of Augmentation for my 10 Chaos Orb in Delirium.asdasdadssa"""
    #print("Whole line :",sell_pm)
    sell_pm=re.search("(.*)@From (.*): Hi, I'd like to buy your (.*) for my (.*) in (.*)",pm)
    options=[]
    #take all the needed arguments from the (.*)
    for i in sell_pm.groups():
        options.append(i)
    
    #get buyer_name from full username and guild. Example: <"UJ"> DoTMadness I only get DoTMadness
    buyer_full_name = options[1].split(' ')
    if len(buyer_full_name)<2: #user is not in a guild so first argument is the name
        buyer_name = buyer_full_name[0]
    else:                       #user is in a guild so first argument is the name
        buyer_name = buyer_full_name[1]
    my_currency = options[2]
    their_currency = options[3]
    return print("Log Parser: ",[buyer_name,my_currency,their_currency])

def kill_process():
    #If i press X the proccess and the threads are killed
    while True:
        if keyboard.is_pressed('x'):
            os._exit(1)
            print("You pressed X process killed.")

if __name__ == "__main__":
    main()
