/**
 * ROUGHSET CHALLENGE - LEADERBOARD JS
 * 5-second polling, podium updates, and classroom live projector view.
 */

let pollInterval = null;

function renderLeaderboard(data, currentSessionPlayerId) {
    const listBody = document.getElementById('leaderboard-body');
    const goldName = document.getElementById('podium-gold-name');
    const goldScore = document.getElementById('podium-gold-score');
    const silverName = document.getElementById('podium-silver-name');
    const silverScore = document.getElementById('podium-silver-score');
    const bronzeName = document.getElementById('podium-bronze-name');
    const bronzeScore = document.getElementById('podium-bronze-score');

    if (!listBody) return;

    // Update Podium Top 3
    if (goldName) {
        if (data.length > 0) {
            goldName.textContent = data[0].first_name || data[0].nickname;
            goldScore.textContent = `${data[0].score.toLocaleString()} XP (${data[0].duration_formatted})`;
        } else {
            goldName.textContent = 'Waiting...';
            goldScore.textContent = '--';
        }
    }
    if (silverName) {
        if (data.length > 1) {
            silverName.textContent = data[1].first_name || data[1].nickname;
            silverScore.textContent = `${data[1].score.toLocaleString()} XP (${data[1].duration_formatted})`;
        } else {
            silverName.textContent = 'Waiting...';
            silverScore.textContent = '--';
        }
    }
    if (bronzeName) {
        if (data.length > 2) {
            bronzeName.textContent = data[2].first_name || data[2].nickname;
            bronzeScore.textContent = `${data[2].score.toLocaleString()} XP (${data[2].duration_formatted})`;
        } else {
            bronzeName.textContent = 'Waiting...';
            bronzeScore.textContent = '--';
        }
    }

    // Build Table Rows
    let html = '';
    data.forEach((p, idx) => {
        const isCurrent = p.player_id === currentSessionPlayerId;
        const rankIcon = idx === 0 ? '🥇' : (idx === 1 ? '🥈' : (idx === 2 ? '🥉' : `#${idx + 1}`));
        const rowClass = isCurrent ? 'style="background: rgba(6, 182, 212, 0.2); border-left: 4px solid var(--primary-cyan);"' : '';
        const statusBadge = p.completed
            ? '<span style="color: var(--accent-success); font-weight: 700;">✓ FINISHED</span>'
            : `<span style="color: var(--primary-cyan);">LEVEL ${p.level}</span>`;

        html += `
            <tr ${rowClass}>
                <td style="font-weight: 800; font-size: 1.1rem;">${rankIcon}</td>
                <td style="font-weight: 600;">
                    ${escapeHtml(p.first_name)} 
                    <span style="color: var(--text-dim); font-size: 0.85rem;">(@${escapeHtml(p.nickname)})</span>
                    ${isCurrent ? '<span style="color: var(--primary-cyan); font-weight: 700; margin-left: 5px;">(YOU)</span>' : ''}
                </td>
                <td style="font-family: var(--font-mono); font-weight: 700; color: var(--primary-cyan);">${p.score.toLocaleString()} XP</td>
                <td style="font-family: var(--font-mono);">${p.duration_formatted}</td>
                <td>${statusBadge}</td>
            </tr>
        `;
    });

    if (data.length === 0) {
        html = '<tr><td colspan="5" style="text-align: center; color: var(--text-dim); padding: 2rem;">No students have joined yet.</td></tr>';
    }

    listBody.innerHTML = html;
}

function escapeHtml(str) {
    if (!str) return '';
    return String(str).replace(/[&<>"']/g, function (m) {
        return {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        }[m];
    });
}

async function fetchLeaderboard(currentSessionPlayerId) {
    try {
        const query = window.location.search || '';
        const res = await fetch('/api/leaderboard' + query);
        if (!res.ok) return;
        const data = await res.json();
        renderLeaderboard(data.leaderboard || [], currentSessionPlayerId);

        if (data.challenge_ended) {
            const banner = document.getElementById('challenge-ended-banner');
            if (banner) banner.style.display = 'block';
            triggerConfetti();
        }
    } catch (err) {
        console.error('Leaderboard poll error:', err);
    }
}

function initLeaderboardPolling(currentSessionPlayerId) {
    fetchLeaderboard(currentSessionPlayerId);
    if (pollInterval) clearInterval(pollInterval);
    pollInterval = setInterval(() => fetchLeaderboard(currentSessionPlayerId), 2500);
}
