import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import yt_dlp
import os


def get_available_formats(url):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'ignoreerrors': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        formats = info.get('formats', [])
        quality_options = []
        for f in formats:
            format_note = f.get('format_note', '')
            format_id = f.get('format_id', '')
            ext = f.get('ext', '')
            resolution = f.get('resolution', 'N/A')
            fps = f.get('fps', '')
            filesize = f.get('filesize', 0)
            filesize_mb = round(filesize / (1024 * 1024), 2) if filesize else 'N/A'

            if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                quality = f"Video: {format_note} - {resolution} - {fps}fps - {filesize_mb}MB ({format_id}.{ext})"
            elif f.get('vcodec') != 'none':
                quality = f"Video Only: {format_note} - {resolution} - {fps}fps - {filesize_mb}MB ({format_id}.{ext})"
            elif f.get('acodec') != 'none':
                quality = f"Audio Only: {format_note} - {filesize_mb}MB ({format_id}.{ext})"
            else:
                continue

            quality_options.append(quality)

    return list(dict.fromkeys(quality_options))  # Remove duplicates


def update_quality_options():
    url = url_entry.get()
    if url:
        qualities = get_available_formats(url)
        quality_combobox['values'] = qualities
        if qualities:
            quality_combobox.set(qualities[0])
    else:
        quality_combobox['values'] = []
        quality_combobox.set('')


def download_video():
    url = url_entry.get()
    output_path = output_path_entry.get()
    selected_quality = quality_combobox.get()
    format_id = selected_quality.split('(')[-1].split(')')[0].split('.')[0]

    ydl_opts = {
        'format': f'{format_id}[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
        'no_warnings': True,
        'ignoreerrors': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
        messagebox.showinfo("Success", f"Downloaded: {os.path.basename(filename)}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")


def download_playlist():
    url = url_entry.get()
    output_path = output_path_entry.get()
    selected_quality = quality_combobox.get()
    format_id = selected_quality.split('(')[-1].split(')')[0].split('.')[0]

    ydl_opts = {
        'format': f'{format_id}[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': os.path.join(output_path, '%(playlist_title)s', '%(title)s.%(ext)s'),
        'no_warnings': True,
        'ignoreerrors': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if 'entries' in info:
                total_videos = len(info['entries'])
                for index, entry in enumerate(info['entries']):
                    try:
                        ydl.download([entry['webpage_url']])
                    except Exception as e:
                        print(f"Error downloading video {index + 1}: {str(e)}")
                    progress = (index + 1) / total_videos * 100
                    progress_var.set(progress)
                    root.update_idletasks()
        messagebox.showinfo("Success", "Playlist download completed")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")


def browse_output_path():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        output_path_entry.delete(0, tk.END)
        output_path_entry.insert(0, folder_selected)


# Create the main window
root = tk.Tk()
root.title("YouTube Downloader")
root.geometry("700x400")
root.configure(bg="#2B2D42")

# Create and place widgets
style = ttk.Style()
style.configure('TLabel', background="#2B2D42", foreground="#EDF2F4", font=("Arial", 12))
style.configure('TButton', background="#8D99AE", foreground="#2B2D42", font=("Arial", 10, "bold"), padding=5)

ttk.Label(root, text="YouTube URL:").pack(pady=5)
url_entry = ttk.Entry(root, width=80)
url_entry.pack(pady=5)

ttk.Button(root, text="Get Quality Options", command=update_quality_options).pack(pady=5)

ttk.Label(root, text="Select Quality:").pack(pady=5)
quality_combobox = ttk.Combobox(root, width=80, state="readonly")
quality_combobox.pack(pady=5)

ttk.Label(root, text="Output Path:").pack(pady=5)
output_path_frame = ttk.Frame(root)
output_path_frame.pack(fill=tk.X, padx=5)

output_path_entry = ttk.Entry(output_path_frame, width=70)
output_path_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
output_path_entry.insert(0, os.path.join(os.path.expanduser("~"), "Downloads"))

browse_button = ttk.Button(output_path_frame, text="Browse", command=browse_output_path)
browse_button.pack(side=tk.RIGHT)

ttk.Button(root, text="Download Video", command=download_video).pack(pady=10)
ttk.Button(root, text="Download Playlist", command=download_playlist).pack(pady=10)

progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=100)
progress_bar.pack(pady=10, fill=tk.X, padx=20)

root.mainloop()