/**
 * ROUGHSET CHALLENGE - MAIN JS
 * Global HUD management, Timer, Audio/Visual Helpers, Notifications
 */

// Show floating XP notification
function showXPToast(points) {
    const isPositive = points > 0;
    const toast = document.createElement('div');
    toast.className = 'xp-toast';
    toast.style.background = isPositive ? 'rgba(16, 185, 129, 0.95)' : 'rgba(239, 68, 68, 0.95)';
    toast.innerHTML = `${isPositive ? '+' : ''}${points} XP`;
    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(-20px)';
        setTimeout(() => toast.remove(), 500);
    }, 1800);
}

// Update HUD XP counter with roll-up animation
function updateHUDScore(newScore) {
    const scoreElem = document.getElementById('hud-score');
    if (scoreElem) {
        scoreElem.textContent = Number(newScore).toLocaleString();
    }
}

// Client-side timer ticker based on server started_at timestamp
function initClientTimer(startedAtIso) {
    const timerElem = document.getElementById('hud-timer');
    if (!timerElem || !startedAtIso) return;

    const startDate = new Date(startedAtIso);

    function tick() {
        const now = new Date();
        const diffMs = Math.max(0, now - startDate);
        const totalSecs = Math.floor(diffMs / 1000);
        const mins = Math.floor(totalSecs / 60);
        const secs = totalSecs % 60;
        timerElem.textContent = `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
    }

    tick();
    setInterval(tick, 1000);
}

// Trigger CSS Confetti Celebration
function triggerConfetti() {
    const wrapper = document.createElement('div');
    wrapper.className = 'confetti-wrapper';
    const colors = ['#06B6D4', '#8B5CF6', '#10B981', '#F59E0B', '#EC4899', '#3B82F6'];

    for (let i = 0; i < 70; i++) {
        const piece = document.createElement('div');
        piece.className = 'confetti-piece';
        piece.style.left = `${Math.random() * 100}vw`;
        piece.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
        piece.style.animationDuration = `${2 + Math.random() * 2.5}s`;
        piece.style.animationDelay = `${Math.random() * 0.8}s`;
        piece.style.transform = `scale(${0.6 + Math.random() * 0.8})`;
        wrapper.appendChild(piece);
    }

    document.body.appendChild(wrapper);
    setTimeout(() => wrapper.remove(), 5000);
}
