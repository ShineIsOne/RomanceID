// 1. DOM SELECTION
const container = document.getElementById('mangaContainer');
const emptyMessage = document.getElementById('emptyMessage');
const modal = document.getElementById('mangaModal');
const closeBtn = document.querySelector('.close-btn');

// Elemen Modal
const modalTitle = document.getElementById('modalTitle');
const modalImg = document.getElementById('modalImg');
const modalGenres = document.getElementById('modalGenres');
const modalSynopsis = document.getElementById('modalSynopsis');
const modalLink = document.getElementById('modalLink');
const modalDetails = document.getElementById('modalDetails');

// 2. FUNGSI RENDER
function renderManga() {
    container.innerHTML = "";

    // Cek apakah variabel mangaList ada dan memiliki isi
    if (typeof mangaList === 'undefined' || mangaList.length === 0) {
        if(emptyMessage) emptyMessage.style.display = 'block';
        return;
    } else {
        if(emptyMessage) emptyMessage.style.display = 'none';
    }

    // --- SORTING: Ongoing First ---
    mangaList.sort((a, b) => {
        if (a.status === "Ongoing" && b.status !== "Ongoing") return -1;
        if (a.status !== "Ongoing" && b.status === "Ongoing") return 1;
        return 0;
    });

    mangaList.forEach(manga => {
        // Genre Tags
        const genreTags = manga.genres.map(genre => 
            `<span class="genre-tag">${genre}</span>`
        ).join('');

        // Status Logic
        let statusIcon = "";
        let statusClass = "";
        if(manga.status === "Ongoing") {
            statusIcon = '<i class="fa-solid fa-hourglass-half"></i>';
            statusClass = "status-ongoing";
        } else {
            statusIcon = '<i class="fa-solid fa-check"></i>';
            statusClass = "status-completed";
        }

        const card = document.createElement('div');
        card.classList.add('card');
        
        // Open Modal
        card.addEventListener('click', () => openModal(manga));

        // HTML Structure
        // PERUBAHAN DISINI: Menambahkan decoding="async" dan width/height
        card.innerHTML = `
            <div class="card-image">
                <span class="status-badge ${statusClass}">
                    ${statusIcon} ${manga.status}
                </span>
                <img 
                    src="${manga.image}" 
                    alt="${manga.title}" 
                    loading="lazy" 
                    decoding="async" 
                    width="200" 
                    height="300" 
                    onerror="this.src='https://via.placeholder.com/200x300?text=No+Image'"
                >
            </div>
            <div class="card-content">
                <div>
                    <h3 class="manga-title">${manga.title}</h3>
                    <div class="manga-info">
                        ${genreTags}
                    </div>
                    <div class="chapter-text">
                        <i class="fa-solid fa-book-open"></i> ${manga.latestChapter}
                    </div>
                </div>
                
                <a href="${manga.link}" target="_blank" class="btn-read" onclick="event.stopPropagation()">
                    Baca di Mangadex <i class="fa-solid fa-arrow-up-right-from-square"></i>
                </a>
            </div>
        `;

        container.appendChild(card);
    });
}

// 3. LOGIKA MODAL
function openModal(manga) {
    modalTitle.textContent = manga.title;
    modalImg.src = manga.image;
    
    // --- FITUR BARU: Set Background Blur ---
    // Kita kirim URL gambar ke CSS variable pada elemen pembungkus (modal-image)
    if(modalImg.parentElement) {
        modalImg.parentElement.style.setProperty('--bg-image', `url('${manga.image}')`);
    }

    modalSynopsis.textContent = manga.synopsis;
    modalLink.href = manga.link;

    modalGenres.innerHTML = manga.genres.map(genre => 
        `<span class="genre-tag">${genre}</span>`
    ).join('');

    // Render Status & Chapter di Modal
    const statusColor = manga.status === "Ongoing" ? "#fee715" : "#00b894";
    modalDetails.innerHTML = `
        <span style="color: ${statusColor}; font-weight: 600; font-size: 0.9rem;">
            <i class="fa-solid ${manga.status === 'Ongoing' ? 'fa-hourglass-half' : 'fa-check'}"></i> 
            Status: ${manga.status}
        </span>
        <span style="color: var(--text-gray); font-weight: 500; font-size: 0.9rem;">
            <i class="fa-solid fa-book-open" style="color: var(--accent);"></i> 
            Terakhir: ${manga.latestChapter}
        </span>
    `;

    modal.classList.add('show');
    document.body.style.overflow = 'hidden';
}

function closeModalAction() {
    modal.classList.remove('show');
    document.body.style.overflow = 'auto';
}

closeBtn.addEventListener('click', closeModalAction);
window.addEventListener('click', (e) => {
    if (e.target == modal) closeModalAction();
});

document.addEventListener('DOMContentLoaded', renderManga);