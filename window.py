import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext, messagebox
from tkinter import filedialog
import requests
from bs4 import BeautifulSoup
from PIL import Image, ImageTk
import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import pyperclip

class MyApp():
    def __init__(self, root):
        self.root = root
        self.root.title("Web Scraping Example")
        self.root.geometry("800x900")
        self.text_files = []
        self.current_directory = ""

        notebook = ttk.Notebook(root)
        notebook.pack()

        self.frame1 = tk.Frame(root)
        notebook.add(self.frame1, text="search")

        self.frame2 = tk.Frame(root)
        notebook.add(self.frame2, text="texts are here!")

        ## Frame 1

        # URL 입력 위젯 (Entry)
        url_label = tk.Label(self.frame1, text="긁어올 URL:")
        url_label.pack(pady=5)
        self.url_entry = tk.Entry(self.frame1, width=40)
        self.url_entry.pack(pady=5)

        # 크롤링 버튼
        crawl_button = tk.Button(self.frame1, text="긁어오기", command=self.crawl_url)
        crawl_button.pack(pady=10)

        # 크롤링 결과를 표시할 스크롤 가능한 텍스트 위젯 (ScrolledText)
        self.output_text = scrolledtext.ScrolledText(self.frame1, wrap=tk.WORD, width=80, height=20)
        self.output_text.pack(expand=True, fill="both", pady=10)

        save_button = tk.Button(self.frame1, text="파일로 저장하기", command=self.save_to_file)
        save_button.pack(pady=5)

        ## Frame 2

        # Contents 입력 위젯
        self.output_text2 = scrolledtext.ScrolledText(self.frame2, wrap=tk.WORD, width=80, height=20)
        self.output_text2.pack(expand=True, fill="both", pady=10)

        self.paste_button = tk.Button(self.frame2, text="복사하기", command=self.copy_to_clipboard)
        self.paste_button.pack(expand=True, fill="both", pady=10)

        # frame 2 init
        self.updateCurrentDirectory()
        self.updateTextFiles()

        frame2_button_label = tk.Label(self.frame2, text="현재 폴더 파일목록: ", background="lightblue", foreground="black")
        frame2_button_label.pack(pady=10)

        self.makeButtons()
        
        self.setup_watchdog()

    def copy_to_clipboard(self):
        # 클립보드에 텍스트 복사
        pyperclip.copy(self.output_text2.get("1.0", tk.END))
        print("텍스트가 클립보드에 복사되었습니다.")

        return
    def crawl_url(self):
        url = self.url_entry.get()  # Get URL from the Entry widget
        try:
            response = requests.get(url)
            response.raise_for_status()  # Check if the request was successful
            content = response.text

            # Parsing the HTML content with BeautifulSoup
            soup = BeautifulSoup(content, 'html.parser')
            text_content = soup.get_text()

            # Remove empty lines
            text_content = "\n\n".join(line.strip() for line in text_content.splitlines() if line.strip())

            # Displaying the crawled content in the ScrolledText widget
            self.output_text.delete(1.0, tk.END)  # Clear previous content
            self.output_text.insert(tk.END, text_content)
        except requests.exceptions.RequestException as e:
            self.output_text.delete(1.0, tk.END)  # Clear previous content
            self.output_text.insert(tk.END, f"Error: {e}")

    def save_to_file(self):
        content_to_save = self.output_text.get("1.0", tk.END)
        try:
            file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
            if file_path:
                with open(file_path, 'w', encoding="utf-8") as file:
                    file.write(content_to_save)
                messagebox.showinfo("저장 성공", "내용이 성공적으로 저장되었습니다.")
        except Exception as e:
            messagebox.showerror("Error", f"Error saving file: {e}")


    def updateTextFiles(self):
        self.text_files = [f for f in os.listdir() if os.path.isfile(f) and f.endswith(".txt")]

    def updateCurrentDirectory(self):
        self.current_directory = os.path.dirname(os.path.realpath(__file__))
    
    def removeFrame2Buttons(self):
        for child in self.frame2.winfo_children():
            if isinstance(child, tk.Button):
                child.destroy()
    
    def create_button(self, file):
        text_button = tk.Button(self.frame2, text=f"{file}", command=lambda f=file : self.display_text_file_content(f))
        text_button.pack(side=tk.LEFT)

    def makeButtons(self):
        for file in self.text_files:
            self.create_button(file)
    
    def display_text_file_content(self, file):
        try:
            file_path = os.path.join(self.current_directory, file)
            if file_path:
                with open(file_path, 'r', encoding="utf-8") as file:
                    file_content = file.read()
                    self.output_text2.delete(1.0, tk.END)  # Clear previous content
                    self.output_text2.insert(tk.END, file_content)
        except Exception as e:
            messagebox.showerror("Error", f"Error reading file: {e}")

    def setup_watchdog(self):
        path_to_watch = "."  # 감시할 폴더의 경로 (현재 폴더)

        self.event_handler = MyHandler(self)
        self.observer = Observer()
        self.observer.schedule(self.event_handler, path=path_to_watch, recursive=False)

        print("Observer Started")

        self.observer.start()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def on_closing(self):
        self.observer.stop()
        self.root.destroy()

class MyHandler(FileSystemEventHandler):
    def __init__(self, app):
        super().__init__()
        self.app = app

    def on_any_event(self, event):
        print(event.event_type)
        if event.is_directory:
            return  # 폴더에 대한 이벤트는 무시
        elif event.event_type in ['deleted', 'created'] and event.src_path.endswith(".txt"):
            self.app.updateTextFiles()
            self.app.removeFrame2Buttons()
            self.app.makeButtons()

            file_name = os.path.basename(event.src_path)
            print(f'파일이 삭제/생성 되었습니다: {file_name}')

if __name__ == "__main__":
    # Tkinter 윈도우 생성
    root = tk.Tk()
    app = MyApp(root)
    root.mainloop()