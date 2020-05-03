from time import sleep
from tkinter import Tk
import re
import pyautogui
import cv2
import win32gui
import pyperclip
import numpy as np
import keyboard

def main():
    #focus poe
    hwnd = win32gui.FindWindow(None, 'Path of Exile')
    win32gui.SetForegroundWindow(hwnd)
    win32gui.ShowWindow(hwnd, 9)
    win32gui.MoveWindow(hwnd, -7, 0, 500, 500, True)

    currency_trading ={
        "Chaos":0,
        "Exalted":0,
        "Alchemy":0,
        "Fusing":0
    }

    sleep(2)
    window = get_trade_window()
    img_rgb = window[0] #focus only on trade
    # img_rgb = np.array(img_rgb)
    # img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
    # template = cv2.imread("images/chaosOrig.png", 0)

    # center_x = pt[0] + w/2
    # center_y = pt[1] + h/2
    count = 0
    cell_distance=30
    for i in range(12):
        for j in range(5):
            position=[window[1] + (i*cell_distance), window[2] + (j*cell_distance)]
            next_position=[window[1] + (i+1*cell_distance), window[2] + (j+1*cell_distance)]

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
                if item_info[0] is None:
                    break
                elif item_info[0] == "currency":
                    currency_name= ''.join(item_info[2])
                    currency_trading[currency_name] += item_info[1]
                #sleep(0.5)
    #cv2.imwrite('res.png', img_rgb)
    print("Total  currencies found in trade: ",currency_trading)

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
    #category = "other"
    
    if "Currency" in string:
        category = "currency"
        curr_number = re.findall("\d+\/\d+", string)[0].split("/")[0] #find number of stack
        curr_name = re.findall("Alchemy|Chaos|Fusing|Exalted",string) #find currency name
    else:
        category = "other"
        curr_number = -1
        curr_name = "not currency"
    print(category,int(curr_number),curr_name)
    return [category,int(curr_number),curr_name]


def get_trade_window():
    topLeft = pyautogui.locateOnScreen('images/topLeft.png')
    bottomRight = pyautogui.locateOnScreen('images/bottomRight.png')
    topLeftP = pyautogui.center(topLeft)
    bottomRightP = pyautogui.center(bottomRight)
    img = pyautogui.screenshot(region=(topLeftP[0], topLeftP[1]+20, (bottomRightP[0]-topLeftP[0])+10, (bottomRightP[1]-topLeftP[1])-20))
    img.save("trade_window.png")
    return [img, topLeftP[0]+20, topLeftP[1]+35] #image, first cell (x,y)


if __name__ == "__main__":
    main()
