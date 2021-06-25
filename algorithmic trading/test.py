import tkinter as tk

import pyttsx3
engine = pyttsx3.init()
engine.say("Good Morning Karthik")
engine.runAndWait()

root = tk.Tk()



canvas1 = tk.Canvas(root, width=300, height=300)
canvas1.pack()

label1 = tk.Label(root, text='Hello World!')
canvas1.create_window(150, 150, window=label1)

root.mainloop()