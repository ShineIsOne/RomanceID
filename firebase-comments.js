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
  limit,
  getCountFromServer
} from "https://www.gstatic.com/firebasejs/10.12.0/firebase-firestore.js";

// ============================================================
// TELEGRAM BOT CONFIG
// Cara setup:
// 1. Chat @BotFather di Telegram, buat bot baru → dapat BOT_TOKEN
// 2. Chat bot kamu, lalu buka:
//    https://api.telegram.org/bot<BOT_TOKEN>/getUpdates
//    Ambil nilai "id" dari "chat" → itu CHAT_ID kamu
// ============================================================
const TELEGRAM_BOT_TOKEN = "8752213236:AAHxV7KDI-rjeyXw3iyQH8kLysXSF3E2Jos";
const TELEGRAM_CHAT_ID   = "5247945257";

async function sendTelegramNotif({ mangaTitle, username, text }) {
  const message =
    `💬 *Komentar Baru!*\n` +
    `📖 Manga: ${mangaTitle}\n` +
    `👤 User: ${username}\n` +
    `🕒 Waktu: ${new Date().toLocaleString("id-ID")}\n\n` +
    `💬 ${text}`;

  const url = `https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage`;

  fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      chat_id: TELEGRAM_CHAT_ID,
      text: message,
      parse_mode: "Markdown"
    })
  }).catch(err => console.warn("Telegram notif error:", err));
}

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
let currentCommentsData = []; // simpan data komentar aktif untuk re-format timestamp saat ganti bahasa

// ============================================================
// I18N DICTIONARY
// ============================================================
const COMMENT_I18N = {
  id: {
    header: "Komentar",
    placeholderUser: "Username kamu...",
    placeholderComment: "Tulis komentar tentang manga ini...",
    btnSend: "Kirim",
    loading: "Memuat komentar...",
    empty: "Belum ada komentar. Jadilah yang pertama!",
    loadError: "Gagal memuat komentar.",
    errNoUser: "Isi username dulu ya!",
    errUserTooLong: "Username maksimal 30 karakter.",
    errNoComment: "Komentarnya kosong nih!",
    errCommentTooLong: "Komentar maksimal 300 karakter.",
    errSpam: "Tunggu sebentar sebelum komentar lagi ya!",
    errSendFailed: "Gagal mengirim komentar. Coba lagi.",
    justNow: "baru saja",
    minAgo: (m) => `${m} mnt lalu`,
    hourAgo: (h) => `${h} jam lalu`,
    dateLocale: "id-ID"
  },
  en: {
    header: "Comments",
    placeholderUser: "Your username...",
    placeholderComment: "Write a comment about this manga...",
    btnSend: "Send",
    loading: "Loading comments...",
    empty: "No comments yet. Be the first to comment!",
    loadError: "Failed to load comments.",
    errNoUser: "Please enter your username!",
    errUserTooLong: "Username must be 30 characters or less.",
    errNoComment: "Comment cannot be empty!",
    errCommentTooLong: "Comment must be 300 characters or less.",
    errSpam: "Please wait a moment before commenting again!",
    errSendFailed: "Failed to send comment. Please try again.",
    justNow: "just now",
    minAgo: (m) => `${m}m ago`,
    hourAgo: (h) => `${h}h ago`,
    dateLocale: "en-US"
  }
};

function getLang() {
  return (window.currentLang === "en") ? "en" : "id";
}

// ============================================================
// UPDATE COMMENT MODAL LANGUAGE
// ============================================================
window.updateCommentLanguage = function(lang) {
  const current = lang === "en" ? "en" : "id";
  const dict = COMMENT_I18N[current];

  const headerLabel = document.getElementById("commentModalHeaderLabel");
  if (headerLabel) headerLabel.textContent = dict.header;

  const usernameInput = document.getElementById("commentUsername");
  if (usernameInput) usernameInput.placeholder = dict.placeholderUser;

  const commentInput = document.getElementById("commentInput");
  if (commentInput) commentInput.placeholder = dict.placeholderComment;

  const sendBtnText = document.getElementById("commentSendBtnText");
  if (sendBtnText) sendBtnText.textContent = dict.btnSend;

  const emptyP = document.querySelector("#commentList .comment-empty p");
  if (emptyP) emptyP.textContent = dict.empty;

  const loadingEl = document.querySelector("#commentList .comment-loading");
  if (loadingEl) {
    loadingEl.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> ${dict.loading}`;
  }

  // Update timestamps jika komentar sedang dibuka
  const items = document.querySelectorAll("#commentList .comment-item");
  if (items.length && currentCommentsData.length) {
    items.forEach((item, idx) => {
      const timeEl = item.querySelector(".comment-time");
      const d = currentCommentsData[idx];
      if (timeEl && d) {
        const time = d.timestamp?.toDate ? d.timestamp.toDate() : null;
        timeEl.textContent = time ? formatTime(time) : dict.justNow;
      }
    });
  }
};

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
  const errorEl = document.getElementById("commentError");

  const lang = getLang();
  const dict = COMMENT_I18N[lang];

  // Update teks sesuai bahasa aktif
  window.updateCommentLanguage(lang);

  // Reset
  input.value = "";
  if (errorEl) errorEl.textContent = "";
  charCount.textContent = "0/300";
  listEl.innerHTML = `<div class="comment-loading"><i class="fa-solid fa-spinner fa-spin"></i> ${dict.loading}</div>`;

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
  currentCommentsData = [];

  // Load komentar real-time
  const q = query(
    collection(db, "comments"),
    where("mangaId", "==", String(manga.id)),
    orderBy("timestamp", "desc"),
    limit(100)
  );

  unsubscribeComments = onSnapshot(q, (snapshot) => {
    currentCommentsData = [];
    if (snapshot.empty) {
      listEl.innerHTML = `
        <div class="comment-empty">
          <i class="fa-regular fa-comment-dots"></i>
          <p>${dict.empty}</p>
        </div>`;
      return;
    }

    listEl.innerHTML = "";
    snapshot.forEach(doc => {
      const d = doc.data();
      currentCommentsData.push(d);
      const time = d.timestamp?.toDate ? d.timestamp.toDate() : null;
      const timeStr = time ? formatTime(time) : dict.justNow;

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
    listEl.innerHTML = `<div class="comment-empty"><p>${dict.loadError}</p></div>`;
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
  currentCommentsData = [];
};

// ============================================================
// KIRIM KOMENTAR
// ============================================================
window.sendComment = async function() {
  const input = document.getElementById("commentInput");
  const usernameInput = document.getElementById("commentUsername");
  const sendBtn = document.getElementById("commentSendBtn");
  const errorEl = document.getElementById("commentError");

  const lang = getLang();
  const dict = COMMENT_I18N[lang];

  const mangaId = sendBtn.dataset.mangaId;
  const mangaTitle = sendBtn.dataset.mangaTitle;
  const username = usernameInput.value.trim();
  const text = input.value.trim();

  // Validasi
  errorEl.textContent = "";
  if (!username) { errorEl.textContent = dict.errNoUser; usernameInput.focus(); return; }
  if (username.length > 30) { errorEl.textContent = dict.errUserTooLong; return; }
  if (!text) { errorEl.textContent = dict.errNoComment; input.focus(); return; }
  if (text.length > 300) { errorEl.textContent = dict.errCommentTooLong; return; }

  // Anti-spam sederhana (simpan waktu terakhir komentar di localStorage)
  const lastComment = localStorage.getItem("lastCommentTime");
  const now = Date.now();
  if (lastComment && now - parseInt(lastComment) < 15000) {
    errorEl.textContent = dict.errSpam;
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

    // Kirim notif Telegram
    sendTelegramNotif({ mangaTitle, username, text });

    input.value = "";
    document.getElementById("commentCharCount").textContent = "0/300";
    localStorage.setItem("lastCommentTime", String(now));
  } catch (err) {
    console.error("Gagal kirim komentar:", err);
    errorEl.textContent = dict.errSendFailed;
  }

  sendBtn.disabled = false;
  sendBtn.innerHTML = `<i class="fa-solid fa-paper-plane"></i> <span id="commentSendBtnText">${dict.btnSend}</span>`;
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
  const lang = getLang();
  const dict = COMMENT_I18N[lang];
  const now = new Date();
  const diff = Math.floor((now - date) / 1000);
  if (diff < 60) return dict.justNow;
  if (diff < 3600) return dict.minAgo(Math.floor(diff / 60));
  if (diff < 86400) return dict.hourAgo(Math.floor(diff / 3600));
  return date.toLocaleDateString(dict.dateLocale, { day: "numeric", month: "short", year: "numeric" });
}

// ============================================================
// HITUNG KOMENTAR PER MANGA (untuk badge di card)
// ============================================================
window.loadCommentCounts = function(mangaIds) {
  mangaIds.forEach(id => {
    const q = query(
      collection(db, "comments"),
      where("mangaId", "==", String(id))
    );
    getCountFromServer(q).then(snapshot => {
      const count = snapshot.data().count;
      const badge = document.getElementById("comment-count-" + id);
      if (badge) badge.textContent = count > 0 ? count : "";
    }).catch(() => {});
  });
};

// Inisialisasi teks komentar saat module termuat
if (typeof window.updateCommentLanguage === "function") {
  window.updateCommentLanguage(window.currentLang || "id");
}
