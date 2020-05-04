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
    
    hwnd = win32gui.FindWindow(None, 'Path of Exile')
    win32gui.SetForegroundWindow(hwnd)
    win32gui.ShowWindow(hwnd, 9)
    win32gui.MoveWindow(hwnd, -7, 0, 500, 500, True)
    
    #listen on client.log
    executor_log = concurrent.futures.ThreadPoolExecutor(1)
    future_file = executor_log.submit(read_file, "F:/Games/POE/logs/Client.txt")

    #if x entered kill proccess
    executor_kill = concurrent.futures.ThreadPoolExecutor(1)
    process_to_be_killed = executor_kill.submit(kill_process) 

    # logfile = open("F:/Games/POE/logs/Client.txt","r")
    # loglines = follow(logfile)
    # for line in loglines:
    #     print (line)



    sleep(2)
    do_trade()
    #trade accepted
    #currency_trading=dict.fromkeys(currency_trading)

def do_trade():
    window = get_trade_window()
    # img_rgb = window[0] #focus only on trade
    # img_rgb = np.array(img_rgb)
    # img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
    # template = cv2.imread("images/chaosOrig.png", 0)

    # center_x = pt[0] + w/2
    # center_y = pt[1] + h/2
    cell_distance=30
    for i in range(4):
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
    in_trade_currency = {}
    for key, value in currency_trading.items():
        if value>0:
            in_trade_currency[key]=value
    print("Total  currencies found in trade: ",in_trade_currency)
    #if trade button is clickable
    found=False      
    while not found:
        try:
            tradeButton = pyautogui.center(pyautogui.locateOnScreen('images/tradeAccept.png'))
            sleep(0.5)
            pyautogui.click(pyautogui.moveTo(int(tradeButton[0]),int(tradeButton[1])+10))
            found = True
        except:
            pass
def get_info(string):
    curr_list = all_currencies
    #item_name = print(re.search("\n(.*)\n-",string).group(1))#get item name
    item_name = string
    if any(word in item_name for word in curr_list):
        category = "currency"
        curr_number = re.findall("\d+\/\d+", string)[0].split("/")[0] #find number of stack
        curr_name = re.search("\n(.*)\n-",string).group(1) #find currency name
    else:
        category = "other"
        curr_number = -1
        curr_name = "not currency"
    print(category,curr_name,int(curr_number))
    return [category,curr_name,int(curr_number)]


def read_file(filepath):
        logfile = open(filepath)
        loglines = follow(logfile)
        for line in loglines:
            return print(log_parser(line))

def get_trade_window():
    topLeft = pyautogui.locateOnScreen('images/topLeft.png')
    bottomRight = pyautogui.locateOnScreen('images/bottomRight.png')
    topLeftP = pyautogui.center(topLeft)
    bottomRightP = pyautogui.center(bottomRight)
    img = pyautogui.screenshot(region=(topLeftP[0], topLeftP[1]+20, (bottomRightP[0]-topLeftP[0])+10, (bottomRightP[1]-topLeftP[1])-20))
    img.save("trade_window.png")
    return [img, topLeftP[0]+20, topLeftP[1]+35] #image, first cell (x,y)

    

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
    sell_pm=re.search("(.*)Hi, I'd like to buy your (.*) for my (.*) in (.*)",sell_pm)
    options=[]
    for i in sell_pm.groups():
        options.append(i)
    print(options)
    buyer = options[0]
    my_currency = options[1]
    their_currency = options[2]
    print(buyer,my_currency,their_currency)

def kill_process():
    while True:
        if keyboard.is_pressed('x'):
            os._exit(1)
            print("You pressed X procces killed.")

if __name__ == "__main__":
    main()
