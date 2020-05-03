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

    currency ={
        "chaos":0,
        "exalted":0,
        "alchemy":0,
        "fusing":0
    }

    sleep(2)
    window = get_trade_window()
    img_rgb = window[0] #focus only on trade
    img_rgb = np.array(img_rgb)
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
    template = cv2.imread("images/chaosOrig.png", 0)

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
                last_currency= get_info(result)
                currency["chaos"] += last_currency
                #sleep(0.5)
    cv2.imwrite('res.png', img_rgb)
    print("Found", count, "Total currency: ", currency["chaos"])

def get_info(string):
    stack_text = re.findall("\d+\/\d+", string)[0].split("/")[0]
    print("Found :",int(stack_text))
    print(re.search("(.*)\n-+",text).group(1))
    return (int(stack_text))

def get_trade_window():
    topLeft = pyautogui.locateOnScreen('images/topLeft.png')
    bottomRight = pyautogui.locateOnScreen('images/bottomRight.png')
    topLeftP = pyautogui.center(topLeft)
    bottomRightP = pyautogui.center(bottomRight)
    img = pyautogui.screenshot(region=(topLeftP[0], topLeftP[1]+20, (bottomRightP[0]-topLeftP[0])+10, (bottomRightP[1]-topLeftP[1])-20))
    img.save("trade_window.png")
    return [img, topLeftP[0]+20, topLeftP[1]+35] #image, first cell (x,y)

# def currency_update(currency):


if __name__ == "__main__":
    main()
