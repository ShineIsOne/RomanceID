// ============================================================
// FIREBASE COMMENTS - Romance ID Project
// ============================================================
// LANGKAH SETUP:
// 1. Buka https://console.firebase.google.com
// 2. Buat project baru
// 3. Klik "Web" (</>) untuk daftarkan app
// 4. Copy config dan tempel di bagian FIREBASE CONFIG di bawah
// 5. Di Firebase console: Build > Firestore Database > Create database
//    Pilih "Start in test mode" > Next > Enable
// ============================================================

import { initializeApp } from "https://www.gstatic.com/firebasejs/10.12.0/firebase-app.js";
import {
  getFirestore,
  collection,
  addDoc,
  query,
  where,
  orderBy,
  onSnapshot,
  serverTimestamp,
  limit
} from "https://www.gstatic.com/firebasejs/10.12.0/firebase-firestore.js";

// ============================================================
// FIREBASE CONFIG — ganti dengan config milik kamu!
// ============================================================
const firebaseConfig = {
  apiKey: "AIzaSyBzNcyO-hBYCjB_dkSfwLHa5pqafNa56NA",
  authDomain: "romance-id.firebaseapp.com",
  projectId: "romance-id",
  storageBucket: "romance-id.firebasestorage.app",
  messagingSenderId: "738021781035",
  appId: "1:738021781035:web:6c4175b2764bb63269c46e",
  measurementId: "G-TZL7WSP527"
};
// ============================================================

const app = initializeApp(firebaseConfig);
const db = getFirestore(app);

let unsubscribeComments = null; // untuk hentikan listener lama saat ganti manga

// ============================================================
// BUKA MODAL KOMENTAR
// ============================================================
window.openCommentModal = function(manga) {
  const modal = document.getElementById("commentModal");
  const titleEl = document.getElementById("commentModalTitle");
  const imgEl = document.getElementById("commentModalImg");
  const listEl = document.getElementById("commentList");
  const input = document.getElementById("commentInput");
  const usernameInput = document.getElementById("commentUsername");
  const sendBtn = document.getElementById("commentSendBtn");
  const charCount = document.getElementById("commentCharCount");

  // Reset
  input.value = "";
  charCount.textContent = "0/300";
  listEl.innerHTML = `<div class="comment-loading"><i class="fa-solid fa-spinner fa-spin"></i> Memuat komentar...</div>`;

  // Isi header modal
  titleEl.textContent = manga.title;
  imgEl.src = manga.image;

  // Simpan mangaId ke tombol kirim
  sendBtn.dataset.mangaId = manga.id;
  sendBtn.dataset.mangaTitle = manga.title;

  // Buka modal
  modal.classList.add("show");
  document.body.style.overflow = "hidden";

  // Hentikan listener sebelumnya
  if (unsubscribeComments) unsubscribeComments();

  // Load komentar real-time
  const q = query(
    collection(db, "comments"),
    where("mangaId", "==", String(manga.id)),
    orderBy("timestamp", "desc"),
    limit(100)
  );

  unsubscribeComments = onSnapshot(q, (snapshot) => {
    if (snapshot.empty) {
      listEl.innerHTML = `
        <div class="comment-empty">
          <i class="fa-regular fa-comment-dots"></i>
          <p>Belum ada komentar. Jadilah yang pertama!</p>
        </div>`;
      return;
    }

    listEl.innerHTML = "";
    snapshot.forEach(doc => {
      const d = doc.data();
      const time = d.timestamp?.toDate();
      const timeStr = time ? formatTime(time) : "baru saja";

      const item = document.createElement("div");
      item.className = "comment-item";
      item.innerHTML = `
        <div class="comment-avatar">${getInitial(d.username)}</div>
        <div class="comment-body">
          <div class="comment-meta">
            <span class="comment-username">${escapeHtml(d.username)}</span>
            <span class="comment-time">${timeStr}</span>
          </div>
          <p class="comment-text">${escapeHtml(d.text)}</p>
        </div>
      `;
      listEl.appendChild(item);
    });
  }, (error) => {
    console.error("Error loading comments:", error);
    listEl.innerHTML = `<div class="comment-empty"><p>Gagal memuat komentar.</p></div>`;
  });
};

// ============================================================
// TUTUP MODAL KOMENTAR
// ============================================================
window.closeCommentModal = function() {
  const modal = document.getElementById("commentModal");
  modal.classList.remove("show");
  document.body.style.overflow = "";
  if (unsubscribeComments) {
    unsubscribeComments();
    unsubscribeComments = null;
  }
};

// ============================================================
// KIRIM KOMENTAR
// ============================================================
window.sendComment = async function() {
  const input = document.getElementById("commentInput");
  const usernameInput = document.getElementById("commentUsername");
  const sendBtn = document.getElementById("commentSendBtn");
  const errorEl = document.getElementById("commentError");

  const mangaId = sendBtn.dataset.mangaId;
  const mangaTitle = sendBtn.dataset.mangaTitle;
  const username = usernameInput.value.trim();
  const text = input.value.trim();

  // Validasi
  errorEl.textContent = "";
  if (!username) { errorEl.textContent = "Isi username dulu ya!"; usernameInput.focus(); return; }
  if (username.length > 30) { errorEl.textContent = "Username maksimal 30 karakter."; return; }
  if (!text) { errorEl.textContent = "Komentarnya kosong nih!"; input.focus(); return; }
  if (text.length > 300) { errorEl.textContent = "Komentar maksimal 300 karakter."; return; }

  // Anti-spam sederhana (simpan waktu terakhir komentar di localStorage)
  const lastComment = localStorage.getItem("lastCommentTime");
  const now = Date.now();
  if (lastComment && now - parseInt(lastComment) < 15000) {
    errorEl.textContent = "Tunggu sebentar sebelum komentar lagi ya!";
    return;
  }

  sendBtn.disabled = true;
  sendBtn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i>`;

  try {
    await addDoc(collection(db, "comments"), {
      mangaId: String(mangaId),
      mangaTitle: mangaTitle,
      username: username,
      text: text,
      timestamp: serverTimestamp()
    });

    input.value = "";
    document.getElementById("commentCharCount").textContent = "0/300";
    localStorage.setItem("lastCommentTime", String(now));
  } catch (err) {
    console.error("Gagal kirim komentar:", err);
    errorEl.textContent = "Gagal mengirim komentar. Coba lagi.";
  }

  sendBtn.disabled = false;
  sendBtn.innerHTML = `<i class="fa-solid fa-paper-plane"></i> Kirim`;
};

// ============================================================
// HELPER
// ============================================================
function getInitial(name) {
  return name ? name.charAt(0).toUpperCase() : "?";
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.appendChild(document.createTextNode(str));
  return div.innerHTML;
}

function formatTime(date) {
  const now = new Date();
  const diff = Math.floor((now - date) / 1000);
  if (diff < 60) return "baru saja";
  if (diff < 3600) return `${Math.floor(diff / 60)} mnt lalu`;
  if (diff < 86400) return `${Math.floor(diff / 3600)} jam lalu`;
  return date.toLocaleDateString("id-ID", { day: "numeric", month: "short", year: "numeric" });
}
