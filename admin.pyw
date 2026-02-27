import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
import time
from PIL import Image
import io

FILE_DATA = 'data.js'
FOLDER_IMG = 'img'
MAX_FILE_SIZE = 80 * 1024  # 80 KB dalam bytes


class MangaAdminApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Admin Manga Project")
        self.root.geometry("1000x680")
        self.root.minsize(900, 600)
        self.root.configure(bg="#111820")

        style = ttk.Style()
        style.theme_use("clam")

        style.configure(".", background="#111820", foreground="#e0e0e0",
                        fieldbackground="#1c2630", bordercolor="#444")
        style.configure("TLabel", background="#111820", foreground="#ffffff")
        style.configure("TFrame", background="#111820")
        style.configure("TLabelframe", background="#111820", foreground="#fee715")
        style.configure("TLabelframe.Label", background="#111820", foreground="#fee715")

        style.configure("Save.TButton", background="#00b894", foreground="#111820", font=('Segoe UI', 12, 'bold'))
        style.map("Save.TButton", background=[("active", "#00d4a0")])
        style.configure("Add.TButton", background="#3498db", foreground="#ffffff", font=('Segoe UI', 11, 'bold'))
        style.map("Add.TButton", background=[("active", "#2980b9")])
        style.configure("Cancel.TButton", background="#e74c3c", foreground="#ffffff")
        style.map("Cancel.TButton", background=[("active", "#c0392b")])

        style.configure("TCombobox", foreground="#ffffff", fieldbackground="#1c2630")
        style.map("TCombobox",
                  fieldbackground=[('readonly', '#1c2630')],
                  selectbackground=[('readonly', '#2c3e50')],
                  selectforeground=[('readonly', '#ffffff')])
        style.configure("TEntry", foreground="#ffffff", fieldbackground="#1c2630")

        self.root.option_add('*TCombobox*Listbox.Background', '#1c2630')
        self.root.option_add('*TCombobox*Listbox.Foreground', '#ffffff')
        self.root.option_add('*TCombobox*Listbox.selectBackground', '#34495e')
        self.root.option_add('*TCombobox*Listbox.selectForeground', '#ffffff')

        if not os.path.exists(FOLDER_IMG):
            os.makedirs(FOLDER_IMG)

        self.current_editing_id = None
        self.manga_data_list = []
        self.has_unsaved_changes = False

        self.text_synopsis_id = None
        self.text_synopsis_en = None

        # ── Canvas + Scroll ─────────────────────────────────────────
        self.canvas = tk.Canvas(root, bg="#111820", highlightthickness=0)
        scrollbar = ttk.Scrollbar(root, orient="vertical", command=self.canvas.yview)
        scrollable_frame = ttk.Frame(self.canvas)

        scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Mouse wheel binding HANYA di canvas dan scrollable frame
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        self.canvas.bind("<MouseWheel>", _on_mousewheel)
        scrollable_frame.bind("<MouseWheel>", _on_mousewheel)

        self.canvas.bind("<Button-4>", lambda e: self.canvas.yview_scroll(-1, "units"))
        self.canvas.bind("<Button-5>", lambda e: self.canvas.yview_scroll(1, "units"))
        scrollable_frame.bind("<Button-4>", lambda e: self.canvas.yview_scroll(-1, "units"))
        scrollable_frame.bind("<Button-5>", lambda e: self.canvas.yview_scroll(1, "units"))

        main_frame = ttk.Frame(scrollable_frame, padding="20 15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # ── Search + Add ────────────────────────────────────────────
        search_frame = ttk.LabelFrame(main_frame, text="Cari / Edit Manga", padding="10")
        search_frame.pack(fill=tk.X, pady=(0, 12))

        self.combo_search = ttk.Combobox(search_frame, state="readonly", font=("Segoe UI", 10))
        self.combo_search.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        self.combo_search.set("Pilih Manga untuk diedit...")
        self.combo_search.bind("<<ComboboxSelected>>", self.on_manga_select)

        ttk.Button(search_frame, text="+ Tambah Manga Baru", style="Add.TButton",
                   command=self.start_add_new_manga).pack(side=tk.RIGHT, padx=(8, 0))
        ttk.Button(search_frame, text="Reset Form", command=self.reset_form).pack(side=tk.RIGHT)

        # ── Form ────────────────────────────────────────────────────
        form_frame = ttk.LabelFrame(main_frame, text="Data Manga", padding="12")
        form_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self._create_labeled_entry(form_frame, "Judul Manga", "self.entry_title", pady=6)
        self._create_labeled_combobox(form_frame, "Status", ["Ongoing", "Completed"], "self.combo_status", pady=6)
        self._create_labeled_combobox(form_frame, "Type Project", ["TL", "Order"], "self.combo_type", pady=6)

        ttk.Label(form_frame, text="Bahasa").pack(anchor=tk.W, pady=(6, 2))
        lang_frame = ttk.Frame(form_frame)
        lang_frame.pack(anchor=tk.W, pady=(0, 6))
        self.lang_id = tk.BooleanVar(value=True)
        self.lang_en = tk.BooleanVar(value=True)
        ttk.Checkbutton(lang_frame, text="Indonesia", variable=self.lang_id, command=self.update_synopsis_fields).pack(side=tk.LEFT, padx=(0, 16))
        ttk.Checkbutton(lang_frame, text="English", variable=self.lang_en, command=self.update_synopsis_fields).pack(side=tk.LEFT)

        self.synopsis_frame = ttk.Frame(form_frame)
        self.synopsis_frame.pack(fill=tk.X, pady=(6, 10))

        ttk.Label(form_frame, text="Cover Image").pack(anchor=tk.W, pady=(4, 2))
        img_frame = ttk.Frame(form_frame)
        img_frame.pack(fill=tk.X, pady=(0, 8))
        self.entry_image = ttk.Entry(img_frame, font=("Segoe UI", 10))
        self.entry_image.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        ttk.Button(img_frame, text="Pilih Gambar...", command=self.browse_image).pack(side=tk.RIGHT)

        self._create_labeled_entry(form_frame, "Genre (pisahkan dengan koma)", "self.entry_genres", pady=6)
        self._create_labeled_entry(form_frame, "Chapter Terakhir", "self.entry_chapter", pady=6)
        self._create_labeled_entry(form_frame, "Link Mangadex", "self.entry_link", pady=6)

        # ── Action Buttons ──────────────────────────────────────────
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(15, 5))

        self.btn_save = tk.Button(btn_frame, text="SIMPAN", bg="#00b894", fg="#111820",
                                  font=('Segoe UI', 12, 'bold'), command=self.save_current,
                                  relief="flat", padx=20, pady=10)
        self.btn_save.pack(side=tk.LEFT, padx=5)

        self.btn_cancel = tk.Button(btn_frame, text="BATAL", bg="#e74c3c", fg="#ffffff",
                                    font=('Segoe UI', 11, 'bold'), command=self.cancel_all_changes,
                                    relief="flat", padx=18, pady=9)
        self.btn_cancel.pack(side=tk.RIGHT, padx=5)

        # Bind perubahan form
        self._bind_changes()

        self.load_and_refresh_data()
        self.update_synopsis_fields()
        self.update_button_states()

    def _create_labeled_entry(self, parent, label_text, attr_name, pady=6):
        ttk.Label(parent, text=label_text).pack(anchor=tk.W, pady=(pady, 2))
        entry = ttk.Entry(parent, font=("Segoe UI", 10))
        entry.pack(fill=tk.X, pady=(0, pady))
        setattr(self, attr_name.split('.')[-1], entry)

    def _create_labeled_combobox(self, parent, label_text, values, attr_name, pady=6):
        ttk.Label(parent, text=label_text).pack(anchor=tk.W, pady=(pady, 2))
        combo = ttk.Combobox(parent, values=values, state="readonly", font=("Segoe UI", 10))
        combo.current(0)
        combo.pack(fill=tk.X, pady=(0, pady))
        setattr(self, attr_name.split('.')[-1], combo)

    def _bind_changes(self):
        widgets = [
            self.entry_title, self.entry_genres, self.entry_chapter,
            self.entry_link, self.entry_image,
            self.combo_status, self.combo_type,
            self.lang_id, self.lang_en
        ]

        for w in widgets:
            if isinstance(w, ttk.Entry):
                w.bind("<KeyRelease>", self.mark_as_changed)
            elif isinstance(w, ttk.Combobox):
                w.bind("<<ComboboxSelected>>", self.mark_as_changed)
            elif isinstance(w, tk.BooleanVar):
                w.trace_add('write', self.mark_as_changed)

    def update_synopsis_fields(self):
        for widget in self.synopsis_frame.winfo_children():
            widget.destroy()
        self.text_synopsis_id = None
        self.text_synopsis_en = None

        if self.lang_id.get():
            ttk.Label(self.synopsis_frame, text="Sinopsis (Indonesia)").pack(anchor=tk.W, pady=(0, 3))
            self.text_synopsis_id = tk.Text(self.synopsis_frame, height=5, wrap=tk.WORD,
                                            font=("Segoe UI", 10), bg="#1c2630", fg="#e0e0e0", relief="flat")
            self.text_synopsis_id.pack(fill=tk.X, pady=(0, 8))
            self.text_synopsis_id.bind("<KeyRelease>", self.mark_as_changed)
            self.text_synopsis_id.bind("<FocusOut>", self.mark_as_changed)

        if self.lang_en.get():
            ttk.Label(self.synopsis_frame, text="Synopsis (English)").pack(anchor=tk.W, pady=(6, 3))
            self.text_synopsis_en = tk.Text(self.synopsis_frame, height=5, wrap=tk.WORD,
                                            font=("Segoe UI", 10), bg="#1c2630", fg="#e0e0e0", relief="flat")
            self.text_synopsis_en.pack(fill=tk.X, pady=(0, 6))
            self.text_synopsis_en.bind("<KeyRelease>", self.mark_as_changed)
            self.text_synopsis_en.bind("<FocusOut>", self.mark_as_changed)

        if self.has_unsaved_changes:
            self.update_button_states()

    def mark_as_changed(self, *args):
        self.has_unsaved_changes = True
        self.update_button_states()

    def load_and_refresh_data(self):
        self.manga_data_list = self.read_data_from_file()
        self.combo_search['values'] = [m['title'] for m in self.manga_data_list if 'title' in m]

    def read_data_from_file(self):
        if not os.path.exists(FILE_DATA):
            return []
        try:
            with open(FILE_DATA, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content or content.startswith("const mangaList = [];"):
                    return []
                json_str = content.replace("const mangaList = ", "").rstrip(";")
                return json.loads(json_str)
        except Exception:
            return []

    def start_add_new_manga(self):
        self.reset_form()
        self.current_editing_id = None
        self.has_unsaved_changes = True
        self.update_button_states()
        self.root.title("Admin Manga Project - Tambah Manga Baru")

    def browse_image(self):
        fp = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.jpeg *.png *.webp")])
        if not fp:
            return

        original_name = os.path.basename(fp)
        name, _ = os.path.splitext(original_name)
        new_filename = f"{name}.webp"
        target_path = os.path.join(FOLDER_IMG, new_filename)

        try:
            img = Image.open(fp).convert("RGB")  # hilangkan alpha channel

            # Resize dulu (maks lebar 480px, proporsional)
            max_width = 480
            if img.width > max_width:
                ratio = max_width / img.width
                new_size = (max_width, int(img.height * ratio))
                img = img.resize(new_size, Image.Resampling.LANCZOS)

            # Kompres agresif sampai < 80 KB
            quality = 92
            while quality >= 28:
                buf = io.BytesIO()
                img.save(buf, format="WEBP", quality=quality, method=6)
                size = buf.tell()

                if size <= MAX_FILE_SIZE:
                    break

                quality -= 6   # turun cukup agresif

            # Simpan hasil terakhir (paksa <80kb atau quality minimal)
            with open(target_path, "wb") as f:
                f.write(buf.getvalue())

            self.entry_image.delete(0, tk.END)
            self.entry_image.insert(0, new_filename)
            self.mark_as_changed()

            messagebox.showinfo("Sukses", f"Cover berhasil dikompres menjadi WebP\nUkuran: {size//1024} KB\nNama file: {new_filename}")

        except Exception as e:
            messagebox.showwarning("Gagal kompres", f"Error saat kompres:\n{e}\n\nGambar dicopy tanpa kompresi.")
            # fallback: copy original
            try:
                with open(fp, 'rb') as src, open(target_path, 'wb') as dst:
                    dst.write(src.read())
                self.entry_image.delete(0, tk.END)
                self.entry_image.insert(0, original_name)
                self.mark_as_changed()
            except:
                messagebox.showerror("Gagal total", "Tidak bisa menyalin gambar sama sekali.")

    def on_manga_select(self, event=None):
        if self.has_unsaved_changes:
            if not messagebox.askyesno("Ada perubahan belum disimpan",
                                       "Apakah Anda ingin menyimpan perubahan sebelum pindah ke manga lain?"):
                self.combo_search.set("Pilih Manga untuk diedit...")
                return

        sel = self.combo_search.get()
        if not sel or sel == "Pilih Manga untuk diedit...":
            self.reset_form()
            return

        manga = next((m for m in self.manga_data_list if m.get('title') == sel), None)
        if not manga:
            return

        self.current_editing_id = manga.get('id')
        self.fill_form_from_manga(manga)
        self.has_unsaved_changes = False
        self.update_button_states()
        self.root.title("Admin Manga Project - Edit Manga")

    def fill_form_from_manga(self, manga):
        self.entry_title.delete(0, tk.END)
        self.entry_title.insert(0, manga.get('title', ''))
        self.combo_status.set(manga.get('status', 'Ongoing'))
        self.combo_type.set(manga.get('type', 'TL'))
        self.entry_image.delete(0, tk.END)
        self.entry_image.insert(0, os.path.basename(manga.get('image', '')) or '')
        self.entry_genres.delete(0, tk.END)
        self.entry_genres.insert(0, ", ".join(manga.get('genres', [])))
        self.entry_chapter.delete(0, tk.END)
        self.entry_chapter.insert(0, manga.get('latestChapter', ''))
        self.entry_link.delete(0, tk.END)
        self.entry_link.insert(0, manga.get('link', ''))

        langs = manga.get("lang", [])
        self.lang_id.set("id" in langs)
        self.lang_en.set("en" in langs)
        self.update_synopsis_fields()

        syn = manga.get("synopsis", "")
        if self.text_synopsis_id and "(IDN)" in syn:
            try:
                self.text_synopsis_id.insert("1.0", syn.split("(IDN)", 1)[1].split("(ENG)", 1)[0].strip())
            except:
                pass
        if self.text_synopsis_en and "(ENG)" in syn:
            try:
                self.text_synopsis_en.insert("1.0", syn.split("(ENG)", 1)[1].strip())
            except:
                pass

    def get_form_data(self):
        title = self.entry_title.get().strip()
        if not title:
            raise ValueError("Judul manga wajib diisi!")

        status = self.combo_status.get()
        type_project = self.combo_type.get()
        genres = [g.strip() for g in self.entry_genres.get().split(',') if g.strip()]
        chapter = self.entry_chapter.get().strip()
        link = self.entry_link.get().strip()
        img_fn = self.entry_image.get().strip()

        lang = []
        syn_parts = []
        if self.lang_id.get() and self.text_synopsis_id:
            s = self.text_synopsis_id.get("1.0", tk.END).strip()
            if s:
                lang.append("id")
                syn_parts.append("(IDN)\n" + s)
        if self.lang_en.get() and self.text_synopsis_en:
            s = self.text_synopsis_en.get("1.0", tk.END).strip()
            if s:
                lang.append("en")
                syn_parts.append("(ENG)\n" + s)

        synopsis = "\n\n".join(syn_parts).strip()
        image_path = f"img/{img_fn}" if img_fn else ""

        data = {
            "title": title,
            "image": image_path,
            "genres": genres,
            "status": status,
            "latestChapter": chapter,
            "link": link,
            "synopsis": synopsis,
            "lang": lang,
            "type": type_project,
        }

        if self.current_editing_id is not None:
            data["id"] = self.current_editing_id
        else:
            data["id"] = int(time.time() * 1000)

        return data

    def save_current(self):
        try:
            new_data = self.get_form_data()

            if self.current_editing_id is None:
                self.manga_data_list.append(new_data)
                messagebox.showinfo("Sukses", f"Manga '{new_data['title']}' berhasil ditambahkan!")
            else:
                for item in self.manga_data_list:
                    if item.get('id') == self.current_editing_id:
                        item.update(new_data)
                        break
                messagebox.showinfo("Sukses", f"Perubahan '{new_data['title']}' berhasil disimpan!")

            self.save_to_file()
            self.load_and_refresh_data()
            self.reset_form()
            self.has_unsaved_changes = False
            self.update_button_states()

        except ValueError as ve:
            messagebox.showwarning("Perhatian", str(ve))
        except Exception as e:
            messagebox.showerror("Gagal", f"Error:\n{e}")

    def save_to_file(self):
        try:
            with open(FILE_DATA, 'w', encoding='utf-8') as f:
                f.write("const mangaList = " + json.dumps(self.manga_data_list, ensure_ascii=False, indent=2) + ";")
        except Exception as e:
            messagebox.showerror("Gagal Menyimpan", f"Tidak bisa menyimpan file:\n{e}")

    def reset_form(self):
        self.current_editing_id = None
        for e in [self.entry_title, self.entry_genres, self.entry_chapter, self.entry_link, self.entry_image]:
            e.delete(0, tk.END)
        self.combo_search.set("Pilih Manga untuk diedit...")
        self.combo_status.current(0)
        self.combo_type.current(0)
        self.lang_id.set(True)
        self.lang_en.set(True)
        self.update_synopsis_fields()
        self.has_unsaved_changes = False
        self.update_button_states()
        self.root.title("Admin Manga Project")

    def cancel_all_changes(self):
        if not self.has_unsaved_changes:
            self.reset_form()
            return

        if messagebox.askyesno("Konfirmasi", "Batalkan semua perubahan yang belum disimpan?"):
            self.reset_form()

    def update_button_states(self):
        if self.has_unsaved_changes:
            if self.current_editing_id is None:
                self.btn_save.config(text="TAMBAH MANGA", bg="#3498db", fg="#ffffff", state="normal")
            else:
                self.btn_save.config(text="SIMPAN PERUBAHAN", bg="#00b894", fg="#111820", state="normal")
        else:
            self.btn_save.config(text="TIDAK ADA PERUBAHAN", bg="#555", fg="#aaa", state="disabled")


if __name__ == "__main__":
    root = tk.Tk()
    app = MangaAdminApp(root)
    root.mainloop()