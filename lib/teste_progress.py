from threading import Thread
from time import sleep
import ttkbootstrap as ttk
import ttkbootstrap.constants as ttkconstants
import tkinter as tk


def expensive():
    print("Expensive work started")
    for i in range(10):
        print(i)
        progress_value.set(i*10)
        sleep(1)


def start_progress():
    Thread(target=expensive).start()


root = ttk.Window(themename='superhero')
root.title("Progress Bar in Tk")
root.geometry("300x200")
root.columnconfigure(1, weight=1)
# root.rowconfigure(1, weight=1)

label = ttk.Label(
    root,
    text="This is a progress bar",
    padding=10,
)
progress_value = tk.IntVar()
progressbar = ttk.Progressbar(
    root,
    orient=tk.HORIZONTAL,
    bootstyle=(ttkconstants.STRIPED, ttkconstants.SUCCESS),
    variable=progress_value,
)
button = ttk.Button(
    root,
    text="Start",
    command=start_progress,
)

label.grid(column=1, row=1, sticky=tk.W)
progressbar.grid(column=1, row=2, sticky=tk.EW)
button.grid(column=1, row=3, sticky=tk.EW, padx=10, pady=10)

root.mainloop()

Thread(target=expensive).start()
