import tkinter as tk
from tkinter import messagebox, filedialog, font
from summarizer import summarize_youtube_video

def display_url():
    url = entry.get()
    long_summary, short_summary = summarize_youtube_video(url, "outputs/")
    print("This is long summary:\n", long_summary)
    print("This is short summary:\n", short_summary)

def upload_file():
    file_path = filedialog.askopenfilename()
    if file_path:
        messagebox.showinfo("Selected File", f"You selected: {file_path}")

root = tk.Tk()
root.title("Video Summarizer")
root.geometry("500x400")
root.configure(bg="#f0f0f0")

title_font = font.Font(family="Helvetica", size=16, weight="bold")
label_font = font.Font(family="Helvetica", size=12)
button_font = font.Font(family="Helvetica", size=10, weight="bold")

title_label = tk.Label(root, text="Video Summarizer", font=title_font, bg="#f0f0f0", fg="#333333")
title_label.pack(pady=20)

# URL input
label = tk.Label(root, text="Please enter a URL or Upload a video", font=label_font, bg="#f0f0f0", fg="#333333")
label.pack(pady=10)

entry = tk.Entry(root, width=50, font=label_font)
entry.pack(pady=5)

button = tk.Button(root, text="Submit", command=display_url, cursor="hand2", 
                   font=button_font, bg="#4CAF50", fg="white", 
                   activebackground="#45a049", activeforeground="white")
button.pack(pady=10)

upload_button = tk.Button(root, text="Upload File", command=upload_file, cursor="hand2", 
                          font=button_font, bg="#008CBA", fg="white", 
                          activebackground="#007B9A", activeforeground="white")
upload_button.pack(pady=10)

root.update_idletasks()
width = root.winfo_width()
height = root.winfo_height()
x = (root.winfo_screenwidth() // 2) - (width // 2)
y = (root.winfo_screenheight() // 2) - (height // 2)
root.geometry('{}x{}+{}+{}'.format(width, height, x, y))

root.mainloop()