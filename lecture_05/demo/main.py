import keyboard
from time import sleep

events_list = []


def callback(event):
    events_list.append(event)


keyboard.on_press(callback)

while True:
    sleep(10)
    print("saving data")
    file = open('out.txt', 'a')

    for e in events_list:
        print(e.time, e.name, file=file)
    events_list = []

    file.close()
