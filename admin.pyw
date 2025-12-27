import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
import shutil
import time

# --- KONFIGURASI ---
FILE_DATA = 'data.js'
FOLDER_IMG = 'img'

class MangaAdminApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Admin Manga Project (Python Version)")
        self.root.geometry("600x750")
        
        # Pastikan folder img ada
        if not os.path.exists(FOLDER_IMG):
            os.makedirs(FOLDER_IMG)

        # Style
        style = ttk.Style()
        style.configure('TLabel', font=('Segoe UI', 10))
        style.configure('TButton', font=('Segoe UI', 10))
        
        # --- UI ELEMENTS ---
        main_frame = ttk.Frame(root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Judul
        ttk.Label(main_frame, text="Judul Manga").pack(anchor=tk.W)
        self.entry_title = ttk.Entry(main_frame, width=50)
        self.entry_title.pack(fill=tk.X, pady=(0, 10))

        # Status
        ttk.Label(main_frame, text="Status").pack(anchor=tk.W)
        self.combo_status = ttk.Combobox(main_frame, values=["Ongoing", "Completed"], state="readonly")
        self.combo_status.current(0)
        self.combo_status.pack(fill=tk.X, pady=(0, 10))

        # Gambar (Browse)
        ttk.Label(main_frame, text="Cover Image").pack(anchor=tk.W)
        img_frame = ttk.Frame(main_frame)
        img_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.entry_image = ttk.Entry(img_frame)
        self.entry_image.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        btn_browse = ttk.Button(img_frame, text="Pilih Gambar...", command=self.browse_image)
        btn_browse.pack(side=tk.RIGHT, padx=(5, 0))

        # Genre
        ttk.Label(main_frame, text="Genre (Pisahkan dengan koma)").pack(anchor=tk.W)
        self.entry_genres = ttk.Entry(main_frame)
        self.entry_genres.pack(fill=tk.X, pady=(0, 10))

        # Chapter
        ttk.Label(main_frame, text="Chapter Terakhir (Misal: Vol.1 Ch.10)").pack(anchor=tk.W)
        self.entry_chapter = ttk.Entry(main_frame)
        self.entry_chapter.pack(fill=tk.X, pady=(0, 10))

        # Link
        ttk.Label(main_frame, text="Link Mangadex").pack(anchor=tk.W)
        self.entry_link = ttk.Entry(main_frame)
        self.entry_link.pack(fill=tk.X, pady=(0, 10))

        # Sinopsis
        ttk.Label(main_frame, text="Sinopsis").pack(anchor=tk.W)
        self.text_synopsis = tk.Text(main_frame, height=5, font=('Segoe UI', 10))
        self.text_synopsis.pack(fill=tk.X, pady=(0, 20))

        # Tombol Simpan
        btn_save = tk.Button(main_frame, text="SIMPAN PERUBAHAN", bg="#00b894", fg="white", font=('Segoe UI', 12, 'bold'), command=self.save_data)
        btn_save.pack(fill=tk.X, ipady=10)

        # Status Bar
        self.lbl_status = ttk.Label(main_frame, text="Siap.", foreground="gray")
        self.lbl_status.pack(pady=10)

        # Variabel untuk menyimpan path gambar asli
        self.source_image_path = ""

    def browse_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Images", "*.jpg;*.jpeg;*.png;*.webp")])
        if file_path:
            self.source_image_path = file_path
            filename = os.path.basename(file_path)
            self.entry_image.delete(0, tk.END)
            self.entry_image.insert(0, filename) # Tampilkan nama file saja

    def load_existing_data(self):
        # PERBAIKAN: Cek apakah file ada dan TIDAK KOSONG
        if not os.path.exists(FILE_DATA) or os.stat(FILE_DATA).st_size == 0:
            return []
        
        try:
            with open(FILE_DATA, 'r', encoding='utf-8') as f:
                content = f.read()
                # Jika file hanya berisi spasi/enter, anggap kosong
                if not content.strip(): 
                    return []
                    
                # Hapus bagian "const mangaList = " dan ";" agar jadi JSON valid
                json_str = content.replace("const mangaList = ", "").replace(";", "")
                return json.loads(json_str)
        except json.JSONDecodeError:
            # Jika format rusak, kita reset jadi array kosong agar tidak error
            print("Database rusak atau kosong, memulai dari awal.")
            return []
        except Exception as e:
            messagebox.showerror("Error", f"Gagal membaca database: {e}")
            return []

    def save_data(self):
        # 1. Ambil Data dari Form
        title = self.entry_title.get()
        status = self.combo_status.get()
        genres = [g.strip() for g in self.entry_genres.get().split(',')]
        chapter = self.entry_chapter.get()
        link = self.entry_link.get()
        synopsis = self.text_synopsis.get("1.0", tk.END).strip()
        img_filename = self.entry_image.get()

        if not title or not img_filename:
            messagebox.showwarning("Peringatan", "Judul dan Gambar wajib diisi!")
            return

        # 2. Proses Copy Gambar (Auto Copy ke folder img)
        final_image_path = f"img/{img_filename}"
        
        if self.source_image_path:
            # Jika user memilih file baru dari komputer
            dest_path = os.path.join(FOLDER_IMG, img_filename)
            try:
                shutil.copy(self.source_image_path, dest_path)
            except Exception as e:
                messagebox.showerror("Error Gambar", f"Gagal mengcopy gambar: {e}")
                return
        else:
            # Jika user mengetik manual, pastikan file ada
            if not os.path.exists(os.path.join(FOLDER_IMG, img_filename)):
                # Cek apakah file ada di folder source code (kadang user taruh di root)
                if os.path.exists(img_filename):
                     shutil.move(img_filename, os.path.join(FOLDER_IMG, img_filename))
                else:
                    confirm = messagebox.askyesno("Gambar Tidak Ditemukan", f"File '{img_filename}' tidak ada di folder 'img'. Lanjut simpan?")
                    if not confirm: return

        # 3. Buat Object Manga Baru
        new_manga = {
            "id": int(time.time()), # ID unik pakai waktu
            "title": title,
            "image": final_image_path,
            "genres": genres,
            "status": status,
            "latestChapter": chapter,
            "link": link,
            "synopsis": synopsis
        }

        # 4. Update Database
        current_data = self.load_existing_data()
        current_data.insert(0, new_manga) # Tambah ke paling atas

        # 5. Tulis Ulang ke data.js
        try:
            js_content = "const mangaList = " + json.dumps(current_data, indent=4) + ";"
            with open(FILE_DATA, 'w', encoding='utf-8') as f:
                f.write(js_content)
            
            self.lbl_status.config(text=f"Berhasil menyimpan '{title}'!", foreground="green")
            messagebox.showinfo("Sukses", "Data Manga Berhasil Ditambahkan!")
            
            # Reset Form
            self.entry_title.delete(0, tk.END)
            self.entry_genres.delete(0, tk.END)
            self.entry_chapter.delete(0, tk.END)
            self.entry_link.delete(0, tk.END)
            self.text_synopsis.delete("1.0", tk.END)
            self.entry_image.delete(0, tk.END)
            self.source_image_path = ""
            
        except Exception as e:
            messagebox.showerror("Gagal Simpan", f"Error menulis file: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = MangaAdminApp(root)
    root.mainloop()