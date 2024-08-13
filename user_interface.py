import tkinter as tk
from tkinter import messagebox, filedialog
from summarizer import summarize_youtube_video

def display_url():
    url = entry.get()
    #messagebox.showinfo("Entered URL", f"You entered: {url}")
    summarize_youtube_video(url, "outputs/")
    
def upload_file():
    file_path = filedialog.askopenfilename()
    if file_path:
        messagebox.showinfo("Selected File", f"You selected: {file_path}")

root = tk.Tk()
root.title("Video Summarizer")

root.geometry("400x350")

label = tk.Label(root, text="Please enter a URL or Upload a video")
label.pack(pady=10)

entry = tk.Entry(root, width=60)
entry.pack(pady=5)

button = tk.Button(root, text="Submit", command=display_url, cursor="hand2")
button.pack(pady=10)

upload_button = tk.Button(root, text="Upload File", command=upload_file, cursor="hand2")
upload_button.pack(pady=10)

upload_button.place(x=320,y=45)

root.mainloop()
