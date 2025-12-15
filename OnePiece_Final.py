import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import requests
from bs4 import BeautifulSoup
import os
import sys
from PIL import Image, ImageTk
from io import BytesIO
import threading

# --- 🎨 COLORS & STYLING ---
COLOR_BG = "#1a1a1a"           # Dark Background
COLOR_POSTER = "#F4E4BC"       # "Wanted Poster" Paper (Beige)
COLOR_TEXT_DARK = "#281E15"    # Dark Brown Text
COLOR_ACCENT_RED = "#D32F2F"   # Luffy Red
COLOR_ACCENT_GOLD = "#FFD700"  # Straw Hat Yellow
FONT_WANTED = ("Times New Roman", 32, "bold") 
FONT_MAIN = ("Verdana", 10, "bold")
FONT_BTN = ("Comic Sans MS", 16, "bold") 
FONT_XLR8 = ("Impact", 20, "italic")

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class MangaDownloaderXLR8:
    def __init__(self, root):
        self.root = root
        self.root.title("One Piece Manga PDF Downloader - XLR8")
        self.root.geometry("650x800")
        self.root.configure(bg=COLOR_BG)
        
        # --- 1. WINDOW ICON (Straw_Hat.png) ---
        try:
            # We use resource_path to find the image inside the EXE
            icon_path = resource_path("Straw_Hat.png")
            self.icon_img = tk.PhotoImage(file=icon_path)
            self.root.iconphoto(False, self.icon_img)
        except Exception:
            pass 

        # --- 2. HEADER LOGO ---
        self.header_frame = tk.Frame(root, bg=COLOR_BG)
        self.header_frame.pack(pady=(15, 5))

        try:
            img_path = resource_path("Straw_Hat.png")
            img = Image.open(img_path)
            img = img.resize((140, 140), Image.Resampling.LANCZOS)
            self.hat_img = ImageTk.PhotoImage(img)
            tk.Label(self.header_frame, image=self.hat_img, bg=COLOR_BG).pack()
        except:
            tk.Label(self.header_frame, text="[Straw Hat Missing]", fg="red", bg=COLOR_BG).pack()

        tk.Label(root, text="ONE PIECE MANGA DOWNLOADER", font=("Impact", 22), fg="white", bg=COLOR_BG).pack()

        # --- 3. WANTED POSTER (Inputs + Jolly Roger) ---
        poster_frame = tk.Frame(root, bg=COLOR_POSTER, bd=8, relief="ridge")
        poster_frame.pack(pady=15, padx=25, fill="x")

        # Header Text
        tk.Label(poster_frame, text="WANTED", font=FONT_WANTED, fg=COLOR_TEXT_DARK, bg=COLOR_POSTER).pack(pady=(5,0))
        tk.Label(poster_frame, text="DEAD OR ALIVE", font=("Times New Roman", 12), fg=COLOR_TEXT_DARK, bg=COLOR_POSTER).pack(pady=(0,10))

        # Main Poster Content (Left: Inputs, Right: Jolly Roger)
        content_frame = tk.Frame(poster_frame, bg=COLOR_POSTER)
        content_frame.pack(fill="x", padx=10, pady=10)

        # -- Left Side: Inputs --
        input_area = tk.Frame(content_frame, bg=COLOR_POSTER)
        input_area.pack(side=tk.LEFT, fill="both", expand=True)

        tk.Label(input_area, text="START CHAPTER", font=FONT_MAIN, fg=COLOR_TEXT_DARK, bg=COLOR_POSTER).pack(anchor="w")
        self.entry_start = tk.Entry(input_area, font=("Arial", 14, "bold"), width=10, justify='center', bd=2, relief="solid")
        self.entry_start.insert(0, "1060")
        self.entry_start.pack(anchor="w", pady=(0, 15))

        tk.Label(input_area, text="END CHAPTER", font=FONT_MAIN, fg=COLOR_TEXT_DARK, bg=COLOR_POSTER).pack(anchor="w")
        self.entry_end = tk.Entry(input_area, font=("Arial", 14, "bold"), width=10, justify='center', bd=2, relief="solid")
        self.entry_end.insert(0, "1065")
        self.entry_end.pack(anchor="w", pady=(0, 5))

        # -- Right Side: Jolly Roger Image --
        try:
            jr_path = resource_path("Jolly_Rogers.png")
            jr_img = Image.open(jr_path)
            jr_img = jr_img.resize((150, 150), Image.Resampling.LANCZOS)
            self.jolly_img = ImageTk.PhotoImage(jr_img)
            
            # Use a frame to create a "Picture Border"
            photo_border = tk.Frame(content_frame, bg="#3e2723", bd=3)
            photo_border.pack(side=tk.RIGHT, padx=10)
            tk.Label(photo_border, image=self.jolly_img, bg="white").pack()
        except:
            tk.Label(content_frame, text="[Jolly Roger Missing]", bg=COLOR_POSTER).pack(side=tk.RIGHT)

        # -- Folder Selection (Bottom of Poster) --
        folder_frame = tk.Frame(poster_frame, bg=COLOR_POSTER)
        folder_frame.pack(fill="x", padx=10, pady=(0, 15))
        
        tk.Label(folder_frame, text="BOUNTY LOCATION:", font=("Arial", 9, "bold"), fg=COLOR_TEXT_DARK, bg=COLOR_POSTER).pack(anchor="w")
        
        self.folder_path = tk.StringVar()
        self.folder_path.set(os.path.join(os.path.expanduser("~"), "Desktop", "OnePiece"))
        
        f_entry = tk.Entry(folder_frame, textvariable=self.folder_path, bg="white", fg="black", relief="solid", bd=1)
        f_entry.pack(side=tk.LEFT, fill="x", expand=True, padx=(0, 5), ipady=4)
        
        btn_browse = tk.Button(folder_frame, text="🗺️ Map", bg="#5D4037", fg="white", font=("Arial", 9, "bold"), command=self.browse_folder)
        btn_browse.pack(side=tk.LEFT)

        # --- 4. ACTION BUTTON ---
        self.btn_download = tk.Button(root, 
                                      text="GOMU GOMU NO... DOWNLOAD!", 
                                      font=FONT_BTN, 
                                      bg=COLOR_ACCENT_RED, 
                                      fg=COLOR_ACCENT_GOLD, 
                                      activebackground="#B71C1C",
                                      activeforeground="white",
                                      relief="raised",
                                      bd=5,
                                      cursor="hand2",
                                      command=self.start_download_thread)
        self.btn_download.pack(pady=20, ipadx=20, ipady=8)

        # --- 5. LOG AREA ---
        self.log_area = scrolledtext.ScrolledText(root, width=65, height=8, bg="black", fg="#00FF00", font=("Consolas", 9), relief="solid", bd=2)
        self.log_area.pack(pady=5)
        self.log(">> Log: Waiting for captain's orders...")

        # --- 6. FOOTER XLR8 ---
        footer_frame = tk.Frame(root, bg=COLOR_BG)
        footer_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=15, pady=10)
        tk.Label(footer_frame, text="XLR8", font=FONT_XLR8, fg="#333", bg=COLOR_BG).pack(side=tk.RIGHT)

    def browse_folder(self):
        selected = filedialog.askdirectory()
        if selected: self.folder_path.set(selected)

    def log(self, msg):
        self.log_area.config(state='normal')
        self.log_area.insert(tk.END, ">> " + msg + "\n")
        self.log_area.see(tk.END)
        self.log_area.config(state='disabled')

    def start_download_thread(self):
        t = threading.Thread(target=self.run_downloader)
        t.start()

    def run_downloader(self):
        self.btn_download.config(state=tk.DISABLED, text="GEAR SECOND... (Working)")
        
        try:
            start_val = self.entry_start.get()
            end_val = self.entry_end.get()
            
            if not start_val.isdigit() or not end_val.isdigit():
                messagebox.showerror("Error", "Chapters must be numbers!")
                return

            start = int(start_val)
            end = int(end_val)
            save_folder = self.folder_path.get()
            base_url = "https://w061.1piecemanga.com/manga/one-piece-chapter-{}/"

            if not os.path.exists(save_folder):
                os.makedirs(save_folder)

            self.log(f"⚔️ Setting sail for chapters {start} to {end}...")

            for chapter in range(start, end + 1):
                self.log(f"⚓ Boarding Chapter {chapter}...")
                self.make_pdf(chapter, base_url, save_folder)
            
            self.log("👑 THE ONE PIECE IS REAL! (Download Complete)")
            messagebox.showinfo("XLR8", "Mission Complete!\nCheck your treasure folder.")

        except Exception as e:
            self.log(f"Error: {e}")
        finally:
            self.btn_download.config(state=tk.NORMAL, text="GOMU GOMU NO... DOWNLOAD!")

    def make_pdf(self, chapter_num, base_url, save_folder):
        url = base_url.format(chapter_num)
        try:
            resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
            if resp.status_code != 200: 
                self.log(f"❌ Chap {chapter_num} missing.")
                return

            soup = BeautifulSoup(resp.text, 'html.parser')
            images = []
            
            for img in soup.find_all('img'):
                link = img.get('data-src') or img.get('src')
                if link:
                    link = link.strip().replace(" ", "%20")
                    if not link.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')): continue
                    
                    try:
                        r = requests.get(link, stream=True, timeout=10)
                        if r.status_code == 200:
                            i = Image.open(BytesIO(r.content)).convert('RGB')
                            if i.width > 200: images.append(i)
                    except: pass
            
            if images:
                path = os.path.join(save_folder, f"Chapter_{chapter_num}.pdf")
                images[0].save(path, "PDF", resolution=100.0, save_all=True, append_images=images[1:])
                self.log(f"✅ Captured Chapter {chapter_num}")
            else:
                self.log(f"⚠️ Chapter {chapter_num} escaped (No images)")

        except Exception as e:
            self.log(f"❌ Defeated by error: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = MangaDownloaderXLR8(root)
    root.mainloop()