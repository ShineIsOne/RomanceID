let currentLang = "id";

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

// =========================
// RENDER
// =========================

function renderManga() {
    container.innerHTML = "";

    if (!mangaList || mangaList.length === 0) {
        emptyMessage.innerHTML = `
            <i class="fa-solid fa-folder-open" style="font-size: 3rem; margin-bottom: 10px;"></i>
            <p>${translateText(
                "Belum ada manga yang ditambahkan.",
                "No manga has been added yet."
            )}</p>
        `;
        emptyMessage.style.display = "block";
        return;
    }

    emptyMessage.style.display = "none";

    mangaList.forEach(manga => {

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
                    ${manga.lang.includes("en") ? '<img src="https://flagcdn.com/w40/gb.png">' : ""}
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