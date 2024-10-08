import tkinter as tk
from tkinter import messagebox, filedialog, font
from summarizer import summarize_youtube_video

def display_url():
    """Fetch the URL from the input field, summarize the corresponding YouTube video, 
    and print the long and short summaries to the console.

    This function handles any exceptions that may arise during the summarization process 
    and prints an error message if an exception occurs.
    """
    try:
        url = entry.get()
        long_summary, short_summary = summarize_youtube_video(url, "outputs/")
        print("This is long summary:\n", long_summary)
        print("This is short summary:\n", short_summary)
    except Exception as e: 
        print("An error occurred:", e)

def upload_file():
    """Open a file dialog for the user to select a video file. 
    Displays a message box showing the selected file path.
    
    Currently, this feature does not perform any actions on the selected file.
    """
    file_path = filedialog.askopenfilename()
    if file_path:
        messagebox.showinfo("Selected File", f"You selected: {file_path} - this feature is currently unavailable")

# Initialize the main application window
root = tk.Tk()
root.title("Video Summarizer")
root.geometry("500x400")
root.configure(bg="#f0f0f0")

# Define fonts for the interface
title_font = font.Font(family="Helvetica", size=16, weight="bold")
label_font = font.Font(family="Helvetica", size=12)
button_font = font.Font(family="Helvetica", size=10, weight="bold")

# Title label
title_label = tk.Label(root, text="Video Summarizer", font=title_font, bg="#f0f0f0", fg="#333333")
title_label.pack(pady=20)

# URL input label
label = tk.Label(root, text="Please enter a URL or Upload a video", font=label_font, bg="#f0f0f0", fg="#333333")
label.pack(pady=10)

# URL input field
entry = tk.Entry(root, width=50, font=label_font)
entry.pack(pady=5)

# Submit button to summarize the video
button = tk.Button(root, text="Submit", command=display_url, cursor="hand2", 
                   font=button_font, bg="#4CAF50", fg="white", 
                   activebackground="#45a049", activeforeground="white")
button.pack(pady=10)

# Upload button to select a video file
upload_button = tk.Button(root, text="Upload File", command=upload_file, cursor="hand2", 
                          font=button_font, bg="#008CBA", fg="white", 
                          activebackground="#007B9A", activeforeground="white")
upload_button.pack(pady=10)

# Center the window on the screen
root.update_idletasks()
width = root.winfo_width()
height = root.winfo_height()
x = (root.winfo_screenwidth() // 2) - (width // 2)
y = (root.winfo_screenheight() // 2) - (height // 2)
root.geometry('{}x{}+{}+{}'.format(width, height, x, y))

# Start the main application loop
root.mainloop()
