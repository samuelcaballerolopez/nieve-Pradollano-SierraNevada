import cv2
import numpy as np
import time

import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk


webcam = 'https://recursos.sierranevada.es/_extras/fotos_camaras/pradollano/snap_c1.jpg?timestamp=638669215345290000&IPIGNORE=TRUE'

def capture(webcam):
    cap = cv2.VideoCapture(webcam)
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        yield frame
    cap.release()


def detect_snow(frame):
    height = frame.shape[0]
    cropped_frame = frame[int(height * 0.40):, :]

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    white_lower = np.array([0, 0, 200], dtype=np.uint8)
    white_upper = np.array([185, 25, 255], dtype=np.uint8)
    
    mask = cv2.inRange(hsv, white_lower, white_upper)
    white_pixels = cv2.countNonZero(mask)

    total_pixels = frame.shape[0] * frame.shape[1]

    return white_pixels, total_pixels   



def assign_message(white_pixels, total_pixels):
    prop_white_pixels = white_pixels/total_pixels
    if prop_white_pixels < 0.01:
        return 'No hay nieve'
    elif 0.01 < prop_white_pixels < 0.1:
        return 'Hay un poco de nieve y/o hay alguna nube'
    elif 0.1 < prop_white_pixels < 0.5:
        return 'Hay algo de nieve y/o hay nubes'    
    else:
        return "Hay mucha nieve"

def show_message():
    for frame in capture(webcam):
        white_pixels, total_pixels = detect_snow(frame)
        message = assign_message(white_pixels, total_pixels)
        message_label.config(text=message)
        root.update_idletasks()
        break


def open_stream():
    try:
        message_label.destroy()
        for frame in capture(webcam):
            white_pixels, total_pixels = detect_snow(frame)
            message = assign_message(white_pixels, total_pixels)
            prop_white_pixels = white_pixels / total_pixels
            print(f'Message: {message}, White pixel percentage: {prop_white_pixels:.2%}')
        
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img)
            img = ImageTk.PhotoImage(image=img)
        
            panel.img = img
            panel.config(image=img)
            root.update_idletasks()
            time.sleep(0.01)
        
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        cv2.destroyAllWindows()

root = tk.Tk()
root.title("Snow in Pradollano")

root.state('zoomed')

panel = tk.Label(root)
panel.pack(expand=True)

message_label = tk.Label(root, text="", font=("Helvetica", 35, 'bold'), bg="darkblue", fg="white")
message_label.place(relx=0.5, rely=0.4, anchor="center")
show_message()

btn = tk.Button(root, text="VER PRADOLLANO", command=open_stream,
                font=("Helvetica", 16), bg="#800000", fg="white", padx=40, pady=20)
btn.place(relx=0.5, rely=0.5, anchor="center")
btn.pack()

root.mainloop()

