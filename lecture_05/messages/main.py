import keyboard
import playsound
from time import sleep


def callback():
    playsound.playsound('alert.wav')


keyboard.add_hotkey('alt+shift+3', callback)

while True:
    sleep(10)


