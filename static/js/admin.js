/**
 * ROUGHSET CHALLENGE - ADMIN LIVE DASHBOARD JS
 * 2.5-second polling for real-time student tracking, metrics, and session states.
 */

let adminPollTimer = null;

function escapeAdminHtml(str) {
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

function updateAdminUI(data) {
    if (!data || !data.stats) return;

    const stats = data.stats;
    const sessionData = data.session || {};

    // 1. Update Metrics Cards
    const elTotal = document.getElementById('stat-total-players');
    if (elTotal) elTotal.textContent = stats.total_players;

    const elCompleted = document.getElementById('stat-completed-players');
    if (elCompleted) elCompleted.textContent = stats.completed_players;

    const elAvgScore = document.getElementById('stat-avg-score');
    if (elAvgScore) {
        elAvgScore.innerHTML = `${stats.average_score} <span style="font-size: 0.85rem;">XP</span>`;
    }

    const elAvgTime = document.getElementById('stat-avg-time');
    if (elAvgTime) elAvgTime.textContent = stats.average_time || '--:--';

    // 2. Update Session Code and Status
    const elCode = document.getElementById('admin-session-code');
    if (elCode && sessionData.code) {
        elCode.textContent = sessionData.code;
    }

    const elStatus = document.getElementById('admin-session-status');
    if (elStatus) {
        if (sessionData.active) {
            elStatus.innerHTML = '<span style="color: var(--accent-success); font-weight: 700;">● LIVE</span>';
        } else {
            elStatus.innerHTML = '<span style="color: var(--text-dim);">● ENDED</span>';
        }
    }

    const elJoining = document.getElementById('admin-session-joining');
    if (elJoining) {
        if (sessionData.joining_open) {
            elJoining.innerHTML = '<span style="color: var(--primary-cyan); font-weight: 700;">OPEN</span>';
        } else {
            elJoining.innerHTML = '<span style="color: var(--accent-warning); font-weight: 700;">CLOSED</span>';
        }
    }

    // 3. Update Student Progress Table
    const tbody = document.getElementById('admin-students-body');
    if (!tbody) return;

    const students = stats.leaderboard || [];
    if (students.length === 0) {
        const sessionCode = sessionData.code || '---';
        tbody.innerHTML = `
            <tr>
                <td colspan="6" style="text-align: center; color: var(--text-dim); padding: 2rem;">
                    No students in this session yet. Share code <strong>${escapeAdminHtml(sessionCode)}</strong> with the class!
                </td>
            </tr>
        `;
        return;
    }

    let rowsHtml = '';
    students.forEach((p, idx) => {
        const rank = p.rank || (idx + 1);
        const statusBadge = p.completed
            ? '<span style="color: var(--accent-success); font-weight: 700;">✓ Completed</span>'
            : `<span style="color: var(--primary-cyan); font-weight: 600;">Playing (Lvl ${p.level})...</span>`;

        rowsHtml += `
            <tr>
                <td style="font-weight: 800;">#${rank}</td>
                <td style="text-align: left; padding-left: 1.5rem; font-weight: 600;">
                    ${escapeAdminHtml(p.first_name)} <span style="color: var(--text-dim); font-size: 0.85rem;">(@${escapeAdminHtml(p.nickname)})</span>
                </td>
                <td>Level ${p.level}</td>
                <td style="font-family: var(--font-mono); color: var(--primary-cyan); font-weight: 700;">${p.score.toLocaleString()} XP</td>
                <td style="font-family: var(--font-mono);">${p.duration_formatted}</td>
                <td>${statusBadge}</td>
            </tr>
        `;
    });

    tbody.innerHTML = rowsHtml;
}

async function fetchAdminLiveData(sessionCode) {
    try {
        const url = `/api/admin/live?code=${encodeURIComponent(sessionCode || '')}`;
        const res = await fetch(url);
        if (!res.ok) return;
        const data = await res.json();
        updateAdminUI(data);
    } catch (err) {
        console.warn('Admin live poll error:', err);
    }
}

function initAdminLiveSync(sessionCode) {
    // Initial fetch
    fetchAdminLiveData(sessionCode);
    // Poll every 2.5s for real-time responsive updates
    if (adminPollTimer) clearInterval(adminPollTimer);
    adminPollTimer = setInterval(() => fetchAdminLiveData(sessionCode), 2500);
}
