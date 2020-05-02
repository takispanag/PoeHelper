from time import sleep
import pyautogui
from imagesearch import *
import cv2
import win32gui
from tkinter import Tk
import re
import pyperclip
import pygame

def main():
    #focus poe
    hwnd = win32gui.FindWindow(None, 'Path of Exile')
    win32gui.SetForegroundWindow(hwnd)
    win32gui.ShowWindow(hwnd, 9)
    win32gui.MoveWindow(hwnd, -7, 0, 500, 500, True)

    sleep(2)
    window=get_trade_window()
    img_rgb=window[0]
    img_rgb = np.array(img_rgb)
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
    template = cv2.imread("chaosOrig.png", 0)

    w, h = template.shape[::-1]
    res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
    precision=0.86
    loc = np.where(res >= precision)
    count = 0
    total_currency=0
    for pt in zip(*loc[::-1]):  # Swap columns and rows
        cv2.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2) #// Uncomment to draw boxes around found occurrences
        center_x=pt[0]+w/2
        center_y=pt[1]+h/2
        count+=1
        pyautogui.moveTo(center_x+window[1],center_y+window[2])
        #ctrl c
        pyautogui.hotkey('ctrl','c')
        # pyautogui.keyDown('ctrl')
        # pyautogui.keyDown('c')
        # pyautogui.keyUp('c')
        # pyautogui.keyUp('ctrl')
        if clip_change():
        #get clipboard content
            clipb=Tk()
            result=clipb.selection_get(selection="CLIPBOARD")
            #get total currency
            total_currency+=get_currency_stack(result)
        #sleep(3)
        sleep(0.5)
    cv2.imwrite('res.png',img_rgb)
    print("Found",count,"Total currency: ",total_currency)


def get_currency_stack(string):
   stack_text=re.findall("\d+\/\d+",string)[0].split("/")[0]
   print(int(stack_text))
   return (int(stack_text))

def clip_change():
    recent_value = ""
    #pyautogui.hotkey('ctrl','c')
    while True:
        tmp_value = pyperclip.paste()
        if tmp_value != recent_value:
            recent_value = tmp_value
            return True

def get_trade_window():
    topLeft=pyautogui.locateOnScreen('topLeft.png')
    bottomRight=pyautogui.locateOnScreen('bottomRight.png')
    topLeftP=pyautogui.center(topLeft)
    bottomRightP=pyautogui.center(bottomRight)
    img=pyautogui.screenshot(region=(topLeftP[0],topLeftP[1]+20,(bottomRightP[0]-topLeftP[0])+10,(bottomRightP[1]-topLeftP[1])-20))
    img.save("trade_window.png")
    return [img,topLeftP[0],topLeftP[1]+20]

if __name__ == "__main__":
    main()