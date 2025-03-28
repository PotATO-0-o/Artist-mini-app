const tg = window.Telegram.WebApp;
const app = document.getElementById('app');
let currentLessons = [];

function initApp() {
    tg.expand();
    loadLessons();
}

function loadLessons() {
    app.innerHTML = '<div class="loader">Загрузка...</div>';
    
    fetch('lessons.json')
        .then(response => response.json())
        .then(lessons => {
            currentLessons = lessons;
            renderLessonList();
        })
        .catch(error => {
            app.innerHTML = '<p class="error">Ошибка загрузки уроков</p>';
        });
}

function renderLessonList() {
    app.innerHTML = `
        <div class="lesson-list">
            ${currentLessons.map(lesson => `
                <div class="lesson-card" data-id="${lesson.id}">
                    <h3>${lesson.title}</h3>
                    <p>🔴 ${lesson.materials}</p>
                </div>
            `).join('')}
        </div>
    `;

    document.querySelectorAll('.lesson-card').forEach(card => {
        card.addEventListener('click', () => {
            const id = parseInt(card.dataset.id);
            renderSingleLesson(id);
        });
    });
}

function renderSingleLesson(id) {
    const lesson = currentLessons.find(l => l.id === id);
    
    if (tg.platform !== "unknown") {
        try {
            tg.sendData(JSON.stringify({
                action: "lesson_start",
                lesson_id: id
            }));
        } catch (e) {
            console.error("Ошибка отправки прогресса:", e);
        }
    }

    app.innerHTML = `
        <div class="single-lesson">
            <button class="back-button">← Назад</button>
            <h2>${lesson.title}</h2>
            <div class="materials">🔧 <b>Материалы:</b> ${lesson.materials}</div>
            
            <div class="steps">
                <h3>Шаги:</h3>
                <ol>${lesson.steps.map(step => `<li>${step}</li>`).join('')}</ol>
            </div>
            
            ${lesson.video ? `
            <div class="video-container">
                <iframe src="${lesson.video}" frameborder="0" allowfullscreen></iframe>
            </div>
            ` : ''}
        </div>
    `;

    document.querySelector('.back-button').addEventListener('click', renderLessonList);
}

initApp();