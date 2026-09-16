/**
 * ROUGHSET CHALLENGE - GAMEPLAY JS
 * Interactive mechanics for Levels 1, 2, 3, 4 and Quiz.
 */

// ==========================================================
// LEVEL 1: FEATURE HUNTER
// ==========================================================
let l1SelectedAttr = null;
let l1RemovedAttrs = new Set();

function initLevel1() {
    const tableHeaders = document.querySelectorAll('.col-attr');
    const removeBtn = document.getElementById('btn-remove-feature');
    const feedback = document.getElementById('l1-feedback');
    const continueBox = document.getElementById('l1-continue-box');

    tableHeaders.forEach(th => {
        th.addEventListener('click', () => {
            const attr = th.getAttribute('data-attr');
            if (l1RemovedAttrs.has(attr)) return;

            // Remove selected class from all
            document.querySelectorAll('.decision-table th, .decision-table td').forEach(el => {
                el.classList.remove('col-selected');
            });

            // Select this column
            l1SelectedAttr = attr;
            document.querySelectorAll(`[data-attr="${attr}"]`).forEach(el => {
                el.classList.add('col-selected');
            });

            removeBtn.disabled = false;
            removeBtn.textContent = `REMOVE FEATURE: [${attr}]`;
        });
    });

    if (removeBtn) {
        removeBtn.addEventListener('click', async () => {
            if (!l1SelectedAttr) return;

            removeBtn.disabled = true;
            removeBtn.textContent = 'ANALYZING CLASSIFICATION...';

            try {
                const res = await fetch('/api/check-feature', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ level: 1, attribute: l1SelectedAttr })
                });
                const data = await res.json();

                feedback.className = 'feedback-box show';

                if (data.dispensable) {
                    // Feature is Dispensable!
                    feedback.className = 'feedback-box show feedback-success glow-success';
                    feedback.innerHTML = `
                        <h4>✓ CLASSIFICATION PRESERVED (100%)</h4>
                        <p><strong>${l1SelectedAttr}</strong> is a <strong>DISPENSABLE</strong> feature! Removing it does not harm classification power.</p>
                    `;
                    showXPToast(data.xp_awarded);
                    updateHUDScore(data.total_score);

                    // Fade out column
                    document.querySelectorAll(`[data-attr="${l1SelectedAttr}"]`).forEach(el => {
                        el.style.opacity = '0.25';
                        el.style.textDecoration = 'line-through';
                    });
                    l1RemovedAttrs.add(l1SelectedAttr);
                    l1SelectedAttr = null;

                    // Show educational reveal & continue
                    continueBox.style.display = 'block';
                    removeBtn.style.display = 'none';
                    triggerConfetti();
                } else {
                    // Feature is Indispensable!
                    feedback.className = 'feedback-box show feedback-danger shake';
                    feedback.innerHTML = `
                        <h4>⚠ CLASSIFICATION LOST (${Math.round((data.classification_power || 0) * 100)}%)</h4>
                        <p><strong>${l1SelectedAttr}</strong> contains critical information! Removing it causes conflicting objects.</p>
                    `;
                    showXPToast(data.xp_awarded);
                    updateHUDScore(data.total_score);
                    removeBtn.disabled = false;
                    removeBtn.textContent = `TRY ANOTHER FEATURE`;
                }
            } catch (err) {
                console.error(err);
                feedback.className = 'feedback-box show feedback-danger';
                feedback.innerHTML = '<p>Error contacting server. Please try again.</p>';
                removeBtn.disabled = false;
            }
        });
    }
}


// ==========================================================
// LEVEL 2: UNLOCK THE CORE
// ==========================================================
let l2TestedAttrs = new Set();
let l2LockedCoreAttrs = new Set();

function initLevel2(requiredCoreCount) {
    const attrButtons = document.querySelectorAll('.l2-attr-btn');
    const feedback = document.getElementById('l2-feedback');
    const coreDisplay = document.getElementById('l2-core-items');
    const continueBox = document.getElementById('l2-continue-box');

    attrButtons.forEach(btn => {
        btn.addEventListener('click', async () => {
            const attr = btn.getAttribute('data-attr');
            if (l2TestedAttrs.has(attr)) return;

            btn.disabled = true;
            btn.textContent = `TESTING [${attr}]...`;

            try {
                const res = await fetch('/api/check-core', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ level: 2, attribute: attr })
                });
                const data = await res.json();

                l2TestedAttrs.add(attr);
                feedback.className = 'feedback-box show';

                if (data.is_indispensable) {
                    btn.className = 'btn btn-success';
                    btn.innerHTML = `🔒 ${attr} (INDISPENSABLE)`;
                    feedback.className = 'feedback-box show feedback-success';
                    feedback.innerHTML = `
                        <h4>🔒 INDISPENSABLE ATTRIBUTE FOUND!</h4>
                        <p>Removing <strong>${attr}</strong> dropped classification to ${Math.round(data.classification_power * 100)}%. It MUST be part of the CORE.</p>
                    `;
                    l2LockedCoreAttrs.add(attr);
                    coreDisplay.textContent = `{ ${Array.from(l2LockedCoreAttrs).join(', ')} }`;
                } else {
                    btn.className = 'btn btn-secondary';
                    btn.innerHTML = `🗑️ ${attr} (DISPENSABLE)`;
                    feedback.className = 'feedback-box show feedback-warning';
                    feedback.innerHTML = `
                        <h4>🗑️ DISPENSABLE FEATURE</h4>
                        <p>Classification remains 100% without <strong>${attr}</strong>. It is not in the CORE.</p>
                    `;
                }

                showXPToast(data.xp_awarded);
                updateHUDScore(data.total_score);

                // Check if all CORE attributes have been discovered
                if (data.core_unlocked) {
                    feedback.className = 'feedback-box show feedback-success glow-success';
                    feedback.innerHTML = `
                        <h3>🔐 CORE UNLOCKED!</h3>
                        <p>You successfully discovered the CORE: <strong>{ ${data.core.join(', ')} }</strong></p>
                    `;
                    continueBox.style.display = 'block';
                    triggerConfetti();
                }
            } catch (err) {
                console.error(err);
                btn.disabled = false;
            }
        });
    });
}


// ==========================================================
// LEVEL 3: REDUCT CHALLENGE
// ==========================================================
let l3SelectedAttrs = new Set(["A", "B", "C", "D", "E", "F", "G", "H"]);
let l3Attempts = 0;

function initLevel3() {
    const pills = document.querySelectorAll('.l3-pill');
    const checkBtn = document.getElementById('btn-check-reduct');
    const feedback = document.getElementById('l3-feedback');
    const countDisplay = document.getElementById('l3-feat-count');
    const reductionDisplay = document.getElementById('l3-reduction-rate');
    const attemptsDisplay = document.getElementById('l3-attempts');
    const continueBox = document.getElementById('l3-continue-box');

    function updateLiveDashboard() {
        const count = l3SelectedAttrs.size;
        countDisplay.textContent = `8 → ${count}`;
        const reductionPct = Math.round(((8 - count) / 8) * 100);
        reductionDisplay.textContent = `${reductionPct}%`;
    }

    pills.forEach(pill => {
        pill.addEventListener('click', () => {
            const attr = pill.getAttribute('data-attr');
            if (l3SelectedAttrs.has(attr)) {
                l3SelectedAttrs.delete(attr);
                pill.classList.remove('active');
                pill.innerHTML = `✕ ${attr}`;
            } else {
                l3SelectedAttrs.add(attr);
                pill.classList.add('active');
                pill.innerHTML = `✓ ${attr}`;
            }
            updateLiveDashboard();
        });
    });

    if (checkBtn) {
        checkBtn.addEventListener('click', async () => {
            if (l3SelectedAttrs.size === 0) {
                alert('Please select at least one feature!');
                return;
            }

            l3Attempts++;
            if (attemptsDisplay) attemptsDisplay.textContent = l3Attempts;

            checkBtn.disabled = true;
            checkBtn.textContent = 'CHECKING REDUCT CONDITIONS...';

            try {
                const res = await fetch('/api/check-reduct', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        level: 3,
                        attributes: Array.from(l3SelectedAttrs),
                        attempts: l3Attempts
                    })
                });
                const data = await res.json();

                feedback.className = 'feedback-box show';

                if (data.status === 'valid_reduct') {
                    // Valid minimal reduct!
                    feedback.className = 'feedback-box show feedback-success glow-success';
                    feedback.innerHTML = `
                        <h2>🎉 REDUCT FOUND!</h2>
                        <p style="font-size: 1.15rem; margin-top: 0.5rem;">
                            Features: <strong>8 → ${l3SelectedAttrs.size}</strong> (${data.reduction_percentage}% Reduction)<br>
                            Classification Power: <strong>100% ✓</strong>
                        </p>
                        <p style="margin-top: 0.5rem; color: #E2E8F0;">
                            A <strong>REDUCT</strong> is a minimal subset of attributes that preserves the required discernibility.
                        </p>
                    `;
                    showXPToast(data.xp_awarded);
                    updateHUDScore(data.total_score);
                    continueBox.style.display = 'block';
                    checkBtn.style.display = 'none';
                    triggerConfetti();
                } else if (data.status === 'classification_lost') {
                    feedback.className = 'feedback-box show feedback-danger shake';
                    feedback.innerHTML = `
                        <h4>⚠ CLASSIFICATION LOST (${Math.round(data.candidate_gamma * 100)}%)</h4>
                        <p>Some objects can no longer be distinctively classified. You need to keep more features or choose a different combination.</p>
                    `;
                    checkBtn.disabled = false;
                    checkBtn.textContent = 'CHECK MY REDUCT';
                } else if (data.status === 'not_minimal') {
                    feedback.className = 'feedback-box show feedback-warning';
                    feedback.innerHTML = `
                        <h4>✓ CLASSIFICATION PRESERVED (100%)</h4>
                        <p>Great! But this set is <strong>NOT MINIMAL</strong> yet. You can still remove more superfluous features to find a true REDUCT.</p>
                    `;
                    checkBtn.disabled = false;
                    checkBtn.textContent = 'CHECK MY REDUCT';
                }
            } catch (err) {
                console.error(err);
                checkBtn.disabled = false;
                checkBtn.textContent = 'CHECK MY REDUCT';
            }
        });
    }
}


// ==========================================================
// LEVEL 4: FACE RECOGNITION LAB
// ==========================================================
let l4SelectedAttrs = new Set(["PC1", "PC2", "PC3", "PC4", "PC5", "PC6"]);

function initLevel4() {
    const pills = document.querySelectorAll('.l4-pill');
    const checkBtn = document.getElementById('btn-validate-face');
    const feedback = document.getElementById('l4-feedback');
    const continueBox = document.getElementById('l4-continue-box');

    pills.forEach(pill => {
        pill.addEventListener('click', () => {
            const attr = pill.getAttribute('data-attr');
            if (l4SelectedAttrs.has(attr)) {
                l4SelectedAttrs.delete(attr);
                pill.classList.remove('active');
                pill.innerHTML = `✕ ${attr}`;
            } else {
                l4SelectedAttrs.add(attr);
                pill.classList.add('active');
                pill.innerHTML = `✓ ${attr}`;
            }
        });
    });

    if (checkBtn) {
        checkBtn.addEventListener('click', async () => {
            if (l4SelectedAttrs.size === 0) {
                alert('Please select at least one PCA component!');
                return;
            }

            checkBtn.disabled = true;
            checkBtn.textContent = 'VALIDATING FACE REDUCT...';

            try {
                const res = await fetch('/api/check-reduct', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        level: 4,
                        attributes: Array.from(l4SelectedAttrs)
                    })
                });
                const data = await res.json();

                feedback.className = 'feedback-box show';

                if (data.status === 'valid_reduct') {
                    feedback.className = 'feedback-box show feedback-success glow-success';
                    feedback.innerHTML = `
                        <h2>👤 FACE CLASSIFICATION READY!</h2>
                        <p style="font-size: 1.1rem; margin-top: 0.5rem;">
                            ✓ Feature Reduction Complete<br>
                            ✓ REDUCT Found: <strong>{ ${Array.from(l4SelectedAttrs).join(', ')} }</strong><br>
                            ✓ LVQ Classifier Ready (Reported <strong>97.3% accuracy</strong> on test set)
                        </p>
                    `;
                    showXPToast(data.xp_awarded);
                    updateHUDScore(data.total_score);
                    continueBox.style.display = 'block';
                    checkBtn.style.display = 'none';
                    triggerConfetti();
                } else if (data.status === 'classification_lost') {
                    feedback.className = 'feedback-box show feedback-danger shake';
                    feedback.innerHTML = `
                        <h4>⚠ IDENTITY CLASSIFICATION LOST</h4>
                        <p>With these components, different subjects become indistinguishable. Try keeping other components.</p>
                    `;
                    checkBtn.disabled = false;
                    checkBtn.textContent = 'TEST FACE REDUCT';
                } else {
                    feedback.className = 'feedback-box show feedback-warning';
                    feedback.innerHTML = `
                        <h4>✓ CLASSIFICATION PRESERVED</h4>
                        <p>Classification works, but you can remove even more PCA components to get a minimal REDUCT!</p>
                    `;
                    checkBtn.disabled = false;
                    checkBtn.textContent = 'TEST FACE REDUCT';
                }
            } catch (err) {
                console.error(err);
                checkBtn.disabled = false;
            }
        });
    }
}


// ==========================================================
// QUIZ MECHANICS
// ==========================================================
function initQuiz() {
    const forms = document.querySelectorAll('.quiz-question-form');

    forms.forEach(form => {
        const qId = form.getAttribute('data-qid');
        const submitBtn = form.querySelector('.btn-submit-answer');
        const feedback = form.querySelector('.quiz-feedback');
        const inputs = form.querySelectorAll('input[type="radio"]');

        submitBtn.addEventListener('click', async () => {
            const selected = form.querySelector('input[type="radio"]:checked');
            if (!selected) {
                alert('Please select an answer!');
                return;
            }

            submitBtn.disabled = true;
            inputs.forEach(i => i.disabled = true);

            try {
                const res = await fetch('/api/quiz-answer', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        question_id: Number(qId),
                        selected_key: selected.value
                    })
                });
                const data = await res.json();

                feedback.style.display = 'block';
                if (data.correct) {
                    feedback.className = 'feedback-box show feedback-success';
                    feedback.innerHTML = `<h4>✓ CORRECT! (+${data.points_awarded} XP)</h4><p>${data.explanation}</p>`;
                    showXPToast(data.points_awarded);
                    updateHUDScore(data.total_score);
                } else {
                    feedback.className = 'feedback-box show feedback-danger';
                    feedback.innerHTML = `<h4>✕ INCORRECT</h4><p>${data.explanation}</p>`;
                }
                submitBtn.style.display = 'none';
            } catch (err) {
                console.error(err);
                submitBtn.disabled = false;
            }
        });
    });
}
