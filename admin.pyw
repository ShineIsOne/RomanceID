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
        self.root.title("Admin Manga Project - Edit & Add Mode")
        self.root.geometry("600x800")
        
        # Pastikan folder img ada
        if not os.path.exists(FOLDER_IMG):
            os.makedirs(FOLDER_IMG)

        # Style
        style = ttk.Style()
        style.configure('TLabel', font=('Segoe UI', 10))
        style.configure('TButton', font=('Segoe UI', 10))
        
        # Variabel State
        self.current_editing_id = None # Jika None = Mode Tambah Baru, Jika ada isi = Mode Edit
        self.source_image_path = ""
        self.manga_data_list = [] # Menyimpan data di memori

        # --- UI ELEMENTS ---
        main_frame = ttk.Frame(root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- BAGIAN PENCARIAN (BARU) ---
        search_frame = ttk.LabelFrame(main_frame, text="Cari / Edit Manga", padding="10")
        search_frame.pack(fill=tk.X, pady=(0, 15))

        self.combo_search = ttk.Combobox(search_frame, state="readonly")
        self.combo_search.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.combo_search.set("Pilih Manga untuk diedit...")
        self.combo_search.bind("<<ComboboxSelected>>", self.on_manga_select)

        btn_reset = ttk.Button(search_frame, text="Reset / Mode Baru", command=self.reset_form)
        btn_reset.pack(side=tk.RIGHT)

        # --- BAGIAN FORM ---
        form_frame = ttk.LabelFrame(main_frame, text="Data Manga", padding="10")
        form_frame.pack(fill=tk.BOTH, expand=True)

        # Judul
        ttk.Label(form_frame, text="Judul Manga").pack(anchor=tk.W)
        self.entry_title = ttk.Entry(form_frame, width=50)
        self.entry_title.pack(fill=tk.X, pady=(0, 10))

        # Status
        ttk.Label(form_frame, text="Status").pack(anchor=tk.W)
        self.combo_status = ttk.Combobox(form_frame, values=["Ongoing", "Completed"], state="readonly")
        self.combo_status.current(0)
        self.combo_status.pack(fill=tk.X, pady=(0, 10))

        # Gambar (Browse)
        ttk.Label(form_frame, text="Cover Image").pack(anchor=tk.W)
        img_frame = ttk.Frame(form_frame)
        img_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.entry_image = ttk.Entry(img_frame)
        self.entry_image.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        btn_browse = ttk.Button(img_frame, text="Pilih Gambar...", command=self.browse_image)
        btn_browse.pack(side=tk.RIGHT, padx=(5, 0))

        # Genre
        ttk.Label(form_frame, text="Genre (Pisahkan dengan koma)").pack(anchor=tk.W)
        self.entry_genres = ttk.Entry(form_frame)
        self.entry_genres.pack(fill=tk.X, pady=(0, 10))

        # Chapter
        ttk.Label(form_frame, text="Chapter Terakhir (Misal: Vol.1 Ch.10)").pack(anchor=tk.W)
        self.entry_chapter = ttk.Entry(form_frame)
        self.entry_chapter.pack(fill=tk.X, pady=(0, 10))

        # Link
        ttk.Label(form_frame, text="Link Mangadex").pack(anchor=tk.W)
        self.entry_link = ttk.Entry(form_frame)
        self.entry_link.pack(fill=tk.X, pady=(0, 10))

        # Sinopsis
        ttk.Label(form_frame, text="Sinopsis").pack(anchor=tk.W)
        self.text_synopsis = tk.Text(form_frame, height=5, font=('Segoe UI', 10))
        self.text_synopsis.pack(fill=tk.X, pady=(0, 20))

        # Tombol Simpan
        self.btn_save = tk.Button(main_frame, text="TAMBAH MANGA BARU", bg="#00b894", fg="white", font=('Segoe UI', 12, 'bold'), command=self.save_data)
        self.btn_save.pack(fill=tk.X, ipady=10)

        # Status Bar
        self.lbl_status = ttk.Label(main_frame, text="Siap.", foreground="gray")
        self.lbl_status.pack(pady=10)

        # Load data awal
        self.load_and_refresh_data()

    def load_and_refresh_data(self):
        """Membaca data.js dan mengisi dropdown pencarian"""
        self.manga_data_list = self.read_data_from_file()
        
        # Isi Combobox dengan judul-judul manga
        titles = [m['title'] for m in self.manga_data_list]
        self.combo_search['values'] = titles
        
    def read_data_from_file(self):
        if not os.path.exists(FILE_DATA) or os.stat(FILE_DATA).st_size == 0:
            return []
        try:
            with open(FILE_DATA, 'r', encoding='utf-8') as f:
                content = f.read()
                if not content.strip(): return []
                # Hapus bagian JS prefix/suffix
                json_str = content.replace("const mangaList = ", "").replace(";", "")
                return json.loads(json_str)
        except Exception as e:
            messagebox.showerror("Error", f"Gagal membaca database: {e}")
            return []

    def browse_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Images", "*.jpg;*.jpeg;*.png;*.webp")])
        if file_path:
            self.source_image_path = file_path
            filename = os.path.basename(file_path)
            self.entry_image.delete(0, tk.END)
            self.entry_image.insert(0, filename)

    def on_manga_select(self, event):
        """Saat user memilih manga dari dropdown"""
        selected_title = self.combo_search.get()
        
        # Cari data berdasarkan judul
        selected_manga = next((m for m in self.manga_data_list if m['title'] == selected_title), None)
        
        if selected_manga:
            self.current_editing_id = selected_manga.get('id')
            
            # Ubah tampilan tombol
            self.btn_save.config(text="SIMPAN PERUBAHAN (UPDATE)", bg="#0984e3")
            self.lbl_status.config(text=f"Mode Edit: {selected_title}", foreground="blue")

            # Isi Form
            self.entry_title.delete(0, tk.END)
            self.entry_title.insert(0, selected_manga.get('title', ''))

            self.combo_status.set(selected_manga.get('status', 'Ongoing'))
            
            # Handle Image path (hapus 'img/' biar bersih di inputan jika mau, tapi biarkan standard)
            img_path = selected_manga.get('image', '')
            self.entry_image.delete(0, tk.END)
            # Kita ambil nama filenya saja untuk ditampilkan di input, biar user gak bingung path
            self.entry_image.insert(0, os.path.basename(img_path)) 

            # Genre join koma
            genres_str = ", ".join(selected_manga.get('genres', []))
            self.entry_genres.delete(0, tk.END)
            self.entry_genres.insert(0, genres_str)

            self.entry_chapter.delete(0, tk.END)
            self.entry_chapter.insert(0, selected_manga.get('latestChapter', ''))

            self.entry_link.delete(0, tk.END)
            self.entry_link.insert(0, selected_manga.get('link', ''))

            self.text_synopsis.delete("1.0", tk.END)
            self.text_synopsis.insert("1.0", selected_manga.get('synopsis', ''))
            
            # Reset source image path karena kita belum pilih gambar baru
            self.source_image_path = ""

    def reset_form(self):
        """Kembali ke mode tambah baru"""
        self.current_editing_id = None
        self.entry_title.delete(0, tk.END)
        self.entry_genres.delete(0, tk.END)
        self.entry_chapter.delete(0, tk.END)
        self.entry_link.delete(0, tk.END)
        self.text_synopsis.delete("1.0", tk.END)
        self.entry_image.delete(0, tk.END)
        self.combo_search.set("Pilih Manga untuk diedit...")
        self.source_image_path = ""
        
        # Balikin tombol ke mode tambah
        self.btn_save.config(text="TAMBAH MANGA BARU", bg="#00b894")
        self.lbl_status.config(text="Mode Tambah Baru", foreground="gray")

    def save_data(self):
        # 1. Ambil Data Form
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

        # 2. Proses Gambar
        # Jika user tidak memilih file baru (source_image_path kosong),
        # berarti pakai gambar lama (cuma nama file di entry).
        # Kita pastikan pathnya lengkap "img/namafile"
        
        final_image_db_path = f"img/{os.path.basename(img_filename)}"

        if self.source_image_path:
            # Ada gambar baru dipilih dari komputer
            dest_path = os.path.join(FOLDER_IMG, os.path.basename(img_filename))
            try:
                shutil.copy(self.source_image_path, dest_path)
            except Exception as e:
                messagebox.showerror("Error Gambar", f"Gagal copy gambar: {e}")
                return
        
        # 3. Update List Data di Memory
        if self.current_editing_id:
            # --- MODE UPDATE ---
            found = False
            for manga in self.manga_data_list:
                if manga.get('id') == self.current_editing_id:
                    manga['title'] = title
                    manga['status'] = status
                    manga['genres'] = genres
                    manga['latestChapter'] = chapter
                    manga['link'] = link
                    manga['synopsis'] = synopsis
                    manga['image'] = final_image_db_path 
                    found = True
                    break
            if not found:
                messagebox.showerror("Error", "ID Manga tidak ditemukan (mungkin file berubah eksternal).")
                return
            msg_success = f"Data '{title}' berhasil diperbarui!"
        else:
            # --- MODE TAMBAH BARU ---
            new_manga = {
                "id": int(time.time()),
                "title": title,
                "image": final_image_db_path,
                "genres": genres,
                "status": status,
                "latestChapter": chapter,
                "link": link,
                "synopsis": synopsis
            }
            self.manga_data_list.insert(0, new_manga)
            msg_success = "Manga Baru Berhasil Ditambahkan!"

        # 4. Tulis Ulang ke File
        try:
            js_content = "const mangaList = " + json.dumps(self.manga_data_list, indent=4) + ";"
            with open(FILE_DATA, 'w', encoding='utf-8') as f:
                f.write(js_content)
            
            self.lbl_status.config(text=msg_success, foreground="green")
            messagebox.showinfo("Sukses", msg_success)
            
            # Refresh dropdown list kalau judul berubah atau ada baru
            self.load_and_refresh_data()
            self.reset_form()
            
        except Exception as e:
            messagebox.showerror("Gagal Simpan", f"Error menulis file: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = MangaAdminApp(root)
    root.mainloop()