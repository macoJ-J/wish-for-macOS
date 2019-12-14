import pyautogui
from time import sleep

def chat(text):
	sleep(2)
	pyautogui.typewrite(text)