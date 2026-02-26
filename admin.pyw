import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
import time

FILE_DATA = 'data.js'
FOLDER_IMG = 'img'


class MangaAdminApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Admin Manga Project")
        self.root.geometry("650x900")

        if not os.path.exists(FOLDER_IMG):
            os.makedirs(FOLDER_IMG)

        self.current_editing_id = None
        self.manga_data_list = []

        main_frame = ttk.Frame(root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # ================= SEARCH =================
        search_frame = ttk.LabelFrame(main_frame, text="Cari / Edit Manga", padding="10")
        search_frame.pack(fill=tk.X, pady=(0, 15))

        self.combo_search = ttk.Combobox(search_frame, state="readonly")
        self.combo_search.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.combo_search.set("Pilih Manga untuk diedit...")
        self.combo_search.bind("<<ComboboxSelected>>", self.on_manga_select)

        ttk.Button(search_frame, text="Reset / Mode Baru",
                   command=self.reset_form).pack(side=tk.RIGHT)

        # ================= FORM =================
        form_frame = ttk.LabelFrame(main_frame, text="Data Manga", padding="10")
        form_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(form_frame, text="Judul Manga").pack(anchor=tk.W)
        self.entry_title = ttk.Entry(form_frame)
        self.entry_title.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(form_frame, text="Status").pack(anchor=tk.W)
        self.combo_status = ttk.Combobox(
            form_frame, values=["Ongoing", "Completed"], state="readonly")
        self.combo_status.current(0)
        self.combo_status.pack(fill=tk.X, pady=(0, 10))

        # ================= BAHASA =================
        ttk.Label(form_frame, text="Bahasa").pack(anchor=tk.W)

        self.lang_id = tk.BooleanVar()
        self.lang_en = tk.BooleanVar()

        ttk.Checkbutton(form_frame, text="Indonesia",
                        variable=self.lang_id,
                        command=self.update_synopsis_fields).pack(anchor=tk.W)

        ttk.Checkbutton(form_frame, text="English",
                        variable=self.lang_en,
                        command=self.update_synopsis_fields).pack(anchor=tk.W)

        self.synopsis_frame = ttk.Frame(form_frame)
        self.synopsis_frame.pack(fill=tk.X, pady=(10, 10))

        self.text_synopsis_id = None
        self.text_synopsis_en = None

        # ================= IMAGE =================
        ttk.Label(form_frame, text="Cover Image").pack(anchor=tk.W)
        img_frame = ttk.Frame(form_frame)
        img_frame.pack(fill=tk.X, pady=(0, 10))

        self.entry_image = ttk.Entry(img_frame)
        self.entry_image.pack(side=tk.LEFT, fill=tk.X, expand=True)

        ttk.Button(img_frame, text="Pilih Gambar...",
                   command=self.browse_image).pack(side=tk.RIGHT)

        ttk.Label(form_frame, text="Genre (Pisahkan dengan koma)").pack(anchor=tk.W)
        self.entry_genres = ttk.Entry(form_frame)
        self.entry_genres.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(form_frame, text="Chapter Terakhir").pack(anchor=tk.W)
        self.entry_chapter = ttk.Entry(form_frame)
        self.entry_chapter.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(form_frame, text="Link Mangadex").pack(anchor=tk.W)
        self.entry_link = ttk.Entry(form_frame)
        self.entry_link.pack(fill=tk.X, pady=(0, 10))

        self.btn_save = tk.Button(main_frame, text="TAMBAH MANGA BARU",
                                  bg="#00b894", fg="white",
                                  font=('Segoe UI', 12, 'bold'),
                                  command=self.save_data)
        self.btn_save.pack(fill=tk.X, ipady=10)

        self.load_and_refresh_data()

    # ================= SINOPSIS DINAMIS =================
    def update_synopsis_fields(self):
        for widget in self.synopsis_frame.winfo_children():
            widget.destroy()

        self.text_synopsis_id = None
        self.text_synopsis_en = None

        if self.lang_id.get():
            ttk.Label(self.synopsis_frame, text="Sinopsis (Indonesia)").pack(anchor=tk.W)
            self.text_synopsis_id = tk.Text(self.synopsis_frame, height=6)
            self.text_synopsis_id.pack(fill=tk.X, pady=(0, 10))

        if self.lang_en.get():
            ttk.Label(self.synopsis_frame, text="Synopsis (English)").pack(anchor=tk.W)
            self.text_synopsis_en = tk.Text(self.synopsis_frame, height=6)
            self.text_synopsis_en.pack(fill=tk.X, pady=(0, 10))

    # ================= LOAD DATA =================
    def load_and_refresh_data(self):
        self.manga_data_list = self.read_data_from_file()
        titles = [m['title'] for m in self.manga_data_list]
        self.combo_search['values'] = titles

    def read_data_from_file(self):
        if not os.path.exists(FILE_DATA):
            return []
        with open(FILE_DATA, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if not content:
                return []
            json_str = content.replace("const mangaList = ", "").rstrip(";")
            return json.loads(json_str)

    # ================= IMAGE =================
    def browse_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Images", "*.jpg;*.jpeg;*.png;*.webp")])
        if file_path:
            filename = os.path.basename(file_path)
            target_path = os.path.join(FOLDER_IMG, filename)
            if not os.path.exists(target_path):
                with open(file_path, 'rb') as src, open(target_path, 'wb') as dst:
                    dst.write(src.read())
            self.entry_image.delete(0, tk.END)
            self.entry_image.insert(0, filename)

    # ================= EDIT MODE =================
    def on_manga_select(self, event):
        selected_title = self.combo_search.get()
        manga = next((m for m in self.manga_data_list if m['title'] == selected_title), None)
        if not manga:
            return

        self.current_editing_id = manga.get('id')
        self.btn_save.config(text="SIMPAN PERUBAHAN (UPDATE)", bg="#0984e3")

        self.entry_title.delete(0, tk.END)
        self.entry_title.insert(0, manga.get('title', ''))

        self.combo_status.set(manga.get('status', 'Ongoing'))

        self.entry_image.delete(0, tk.END)
        self.entry_image.insert(0, os.path.basename(manga.get('image', '')))

        self.entry_genres.delete(0, tk.END)
        self.entry_genres.insert(0, ", ".join(manga.get('genres', [])))

        self.entry_chapter.delete(0, tk.END)
        self.entry_chapter.insert(0, manga.get('latestChapter', ''))

        self.entry_link.delete(0, tk.END)
        self.entry_link.insert(0, manga.get('link', ''))

        self.lang_id.set("id" in manga.get("lang", []))
        self.lang_en.set("en" in manga.get("lang", []))

        self.update_synopsis_fields()

        synopsis = manga.get("synopsis", "")

        if self.text_synopsis_id and "(IDN)" in synopsis:
            id_part = synopsis.split("(IDN)")[1]
            if "(ENG)" in id_part:
                id_part = id_part.split("(ENG)")[0]
            self.text_synopsis_id.insert("1.0", id_part.strip())

        if self.text_synopsis_en and "(ENG)" in synopsis:
            en_part = synopsis.split("(ENG)")[1]
            self.text_synopsis_en.insert("1.0", en_part.strip())

    # ================= RESET =================
    def reset_form(self):
        self.current_editing_id = None
        self.entry_title.delete(0, tk.END)
        self.entry_genres.delete(0, tk.END)
        self.entry_chapter.delete(0, tk.END)
        self.entry_link.delete(0, tk.END)
        self.entry_image.delete(0, tk.END)
        self.combo_search.set("Pilih Manga untuk diedit...")
        self.lang_id.set(False)
        self.lang_en.set(False)
        self.update_synopsis_fields()
        self.btn_save.config(text="TAMBAH MANGA BARU", bg="#00b894")

    # ================= SAVE =================
    def save_data(self):
        title = self.entry_title.get()
        status = self.combo_status.get()
        genres = [g.strip() for g in self.entry_genres.get().split(',') if g.strip()]
        chapter = self.entry_chapter.get()
        link = self.entry_link.get()

        synopsis_parts = []
        lang = []

        if self.lang_id.get() and self.text_synopsis_id:
            lang.append("id")
            synopsis_parts.append("(IDN)\n" + self.text_synopsis_id.get("1.0", tk.END).strip())

        if self.lang_en.get() and self.text_synopsis_en:
            lang.append("en")
            synopsis_parts.append("(ENG)\n" + self.text_synopsis_en.get("1.0", tk.END).strip())

        synopsis = "\n\n".join(synopsis_parts)

        img_filename = self.entry_image.get()
        if not title or not img_filename:
            messagebox.showwarning("Peringatan", "Judul dan Gambar wajib diisi!")
            return

        final_image_db_path = f"img/{img_filename}"

        if self.current_editing_id:
            for manga in self.manga_data_list:
                if manga.get('id') == self.current_editing_id:
                    manga.update({
                        "title": title,
                        "image": final_image_db_path,
                        "genres": genres,
                        "status": status,
                        "latestChapter": chapter,
                        "link": link,
                        "synopsis": synopsis,
                        "lang": lang
                    })
                    break
        else:
            self.manga_data_list.insert(0, {
                "id": int(time.time()),
                "title": title,
                "image": final_image_db_path,
                "genres": genres,
                "status": status,
                "latestChapter": chapter,
                "link": link,
                "synopsis": synopsis,
                "lang": lang
            })

        js_content = "const mangaList = " + json.dumps(self.manga_data_list, indent=4) + ";"

        with open(FILE_DATA, 'w', encoding='utf-8') as f:
            f.write(js_content)

        self.load_and_refresh_data()
        self.reset_form()
        messagebox.showinfo("Sukses", "Data berhasil disimpan!")


if __name__ == "__main__":
    root = tk.Tk()
    app = MangaAdminApp(root)
    root.mainloop()