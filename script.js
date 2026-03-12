let currentLang = "id";
let currentView = "TL"; // default tampilan TL
// =========================
// LANGUAGE SYSTEM
// =========================

function setLanguage(lang) {
    currentLang = lang;

    btnID.classList.remove("active");
    btnEN.classList.remove("active");

    if (lang === "id") btnID.classList.add("active");
    if (lang === "en") btnEN.classList.add("active");

    document.querySelector(".header-subtitle").textContent =
        translateText("Project TL Manga", "Manga TL Project");

    document.querySelector(".synopsis-label").textContent =
        translateText("Sinopsis:", "Synopsis:");

    renderManga();
}

function translateText(idText, enText) {
    return currentLang === "id" ? idText : enText;
}

function extractSynopsis(fullText) {
    if (!fullText) return "";

    const idMatch = fullText.match(/\(IDN\)([\s\S]*?)(\(ENG\)|$)/);
    const enMatch = fullText.match(/\(ENG\)([\s\S]*)/);

    if (currentLang === "id" && idMatch) return idMatch[1].trim();
    if (currentLang === "en" && enMatch) return enMatch[1].trim();

    return fullText;
}

function translateStatus(status) {
    if (currentLang === "id") return status;
    if (status === "Ongoing") return "Ongoing";
    if (status === "Completed") return "Completed";
    return status;
}

// =========================
// DOM
// =========================

const container = document.getElementById('mangaContainer');
const emptyMessage = document.getElementById('emptyMessage');
const modal = document.getElementById('mangaModal');
const closeBtn = document.querySelector('.close-btn');

const modalTitle = document.getElementById('modalTitle');
const modalImg = document.getElementById('modalImg');
const modalGenres = document.getElementById('modalGenres');
const modalSynopsis = document.getElementById('modalSynopsis');
const modalLink = document.getElementById('modalLink');
const modalDetails = document.getElementById('modalDetails');

const btnID = document.getElementById("langID");
const btnEN = document.getElementById("langEN");
const btnTL = document.getElementById("btnTL");
const btnOrder = document.getElementById("btnOrder");

// =========================
// RENDER
// =========================

function renderManga() {
    container.innerHTML = "";

    const filteredList = mangaList.filter(manga =>
        manga.type === currentView
    );

    if (!filteredList || filteredList.length === 0) {
        emptyMessage.innerHTML = `
            <i class="fa-solid fa-folder-open" style="font-size: 3rem; margin-bottom: 10px;"></i>
            <p>${translateText(
                "Belum ada manga di kategori ini.",
                "No manga in this category."
            )}</p>
        `;
        emptyMessage.style.display = "block";
        return;
    }

    emptyMessage.style.display = "none";

    const sortedList = [...filteredList].sort((a, b) => {
        if (a.status === "Ongoing" && b.status === "Completed") return -1;
        if (a.status === "Completed" && b.status === "Ongoing") return 1;
        return 0;
    });

sortedList.forEach(manga => {

        const genreTags = manga.genres.map(g =>
            `<span class="genre-tag">${g}</span>`
        ).join('');

        let statusClass = manga.status === "Ongoing"
            ? "status-ongoing"
            : "status-completed";

        let statusIcon = manga.status === "Ongoing"
            ? '<i class="fa-solid fa-hourglass-half"></i>'
            : '<i class="fa-solid fa-check"></i>';

        let flags = "";
        if (Array.isArray(manga.lang)) {
            flags = `
                <div class="lang-flags">
                    ${manga.lang.includes("id") ? '<img src="https://flagcdn.com/w40/id.png">' : ""}
                    ${manga.lang.includes("en") ? '<img src="https://flagcdn.com/w40/gb.png" alt="English" style="aspect-ratio: 5/3; object-fit: fill;">' : ""}
                </div>
            `;
        }

        const card = document.createElement('div');
        card.classList.add('card');

        card.innerHTML = `
            <div class="card-image">
                <span class="status-badge ${statusClass}">
                    ${statusIcon} ${translateStatus(manga.status)}
                </span>

                ${flags}

                <img src="${manga.image}">
            </div>

            <div class="card-content">
                <div>
                    <h3 class="manga-title">${manga.title}</h3>
                    <div class="manga-info">
                        ${genreTags}
                    </div>
                    <div class="chapter-text">
                        <i class="fa-solid fa-book-open"></i>
                        ${manga.latestChapter}
                    </div>
                </div>

                <a href="${manga.link}" target="_blank" class="btn-read">
                    ${translateText("Baca di Mangadex", "Read on Mangadex")}
                </a>
            </div>
        `;

        card.addEventListener('click', () => openModal(manga));
        container.appendChild(card);
    });
}

// =========================
// MODAL
// =========================

function openModal(manga) {

    modalTitle.textContent = manga.title;
    modalImg.src = manga.image;

    // set background image untuk blur mobile
    modal.querySelector(".modal-content")
        .style.setProperty("--bg-image", `url(${manga.image})`);

    modalSynopsis.textContent = extractSynopsis(manga.synopsis);
    modalLink.href = manga.link;

    modalLink.innerHTML = `
        ${translateText("Baca di Mangadex", "Read on Mangadex")}
        <i class="fa-solid fa-external-link-alt"></i>
    `;

    modalGenres.innerHTML = manga.genres.map(g =>
        `<span class="genre-tag">${g}</span>`
    ).join('');

    modalDetails.innerHTML = `
        <span>
            ${translateText("Status", "Status")}:
            ${translateStatus(manga.status)}
        </span>
        <span>
            ${translateText("Terakhir", "Latest")}:
            ${manga.latestChapter}
        </span>
    `;

    modal.classList.add("show");
}

function closeModalAction() {
    modal.classList.remove("show");
}

closeBtn.addEventListener("click", closeModalAction);

window.addEventListener("click", (e) => {
    if (e.target == modal) closeModalAction();
});

// =========================
// INIT
// =========================

btnID.addEventListener("click", () => setLanguage("id"));
btnEN.addEventListener("click", () => setLanguage("en"));

document.addEventListener("DOMContentLoaded", () => {
    setLanguage("id");
});

btnTL.addEventListener("click", () => {
    currentView = "TL";
    btnTL.classList.add("active");
    btnOrder.classList.remove("active");
    renderManga();
});

btnOrder.addEventListener("click", () => {
    currentView = "Order";
    btnOrder.classList.add("active");
    btnTL.classList.remove("active");
    renderManga();
});

// =========================
// SUPPORT MODAL
// =========================

const supportModal = document.getElementById("supportModal");
const supportBtn = document.getElementById("supportBtn");
const supportCloseBtn = document.getElementById("supportCloseBtn");

function switchSupportLang(lang) {
    const panelID = document.getElementById("panelID");
    const panelEN = document.getElementById("panelEN");
    const tabID = document.getElementById("tabID");
    const tabEN = document.getElementById("tabEN");
    const titleEl = document.getElementById("supportTitle");
    const subtitleEl = document.getElementById("supportSubtitle");

    if (lang === "id") {
        panelID.style.display = "";
        panelEN.style.display = "none";
        tabID.classList.add("active");
        tabEN.classList.remove("active");
        titleEl.textContent = "Dukung Saya";
        subtitleEl.textContent = "Dukunganmu sangat berarti untuk melanjutkan proyek ini!";
    } else {
        panelID.style.display = "none";
        panelEN.style.display = "";
        tabID.classList.remove("active");
        tabEN.classList.add("active");
        titleEl.textContent = "Support Me";
        subtitleEl.textContent = "Your support means a lot to keep this project going!";
    }
}

supportBtn.addEventListener("click", () => {
    supportModal.classList.add("show");
    // Sync dengan bahasa aktif saat ini
    switchSupportLang(currentLang);
});

supportCloseBtn.addEventListener("click", () => {
    supportModal.classList.remove("show");
});

window.addEventListener("click", (e) => {
    if (e.target === supportModal) supportModal.classList.remove("show");
});

// =========================
// ORDER INFO FAB & MODAL
// =========================

const orderInfoBtn = document.getElementById("orderInfoBtn");
const orderInfoModal = document.getElementById("orderInfoModal");
const orderInfoCloseBtn = document.getElementById("orderInfoCloseBtn");

// Tampilkan/sembunyikan FAB sesuai view
function updateOrderFab() {
    if (currentView === "Order") {
        orderInfoBtn.style.display = "flex";
    } else {
        orderInfoBtn.style.display = "none";
        orderInfoModal.classList.remove("show");
    }
}

function switchOrderLang(lang) {
    const panelID = document.getElementById("orderPanelID");
    const panelEN = document.getElementById("orderPanelEN");
    const tabID = document.getElementById("orderTabID");
    const tabEN = document.getElementById("orderTabEN");

    if (lang === "id") {
        panelID.style.display = "";
        panelEN.style.display = "none";
        tabID.classList.add("active");
        tabEN.classList.remove("active");
    } else {
        panelID.style.display = "none";
        panelEN.style.display = "";
        tabID.classList.remove("active");
        tabEN.classList.add("active");
    }
}

orderInfoBtn.addEventListener("click", () => {
    orderInfoModal.classList.add("show");
    switchOrderLang(currentLang);
});

orderInfoCloseBtn.addEventListener("click", () => {
    orderInfoModal.classList.remove("show");
});

window.addEventListener("click", (e) => {
    if (e.target === orderInfoModal) orderInfoModal.classList.remove("show");
});

// Patch tombol TL/Order agar FAB ikut update
btnTL.addEventListener("click", updateOrderFab);
btnOrder.addEventListener("click", updateOrderFab);