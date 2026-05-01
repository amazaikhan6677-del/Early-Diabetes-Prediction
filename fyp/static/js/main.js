/* DiabetesGuard — Frontend Logic */

// ─── State ────────────────────────────────────────────────
const state = {
  currentPage: 1,
  gender: '', activity: '', smoking: '',
  familyHistory: '', highBloodSugar: '', hypertension: '',
  heartDisease: '', pcos: '',
  polyuria: '', polydipsia: '', weightLoss: '',
  blurredVision: '', fatigue: '', slowHealing: ''
};

// ─── Init ─────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  updateClock();
  setInterval(updateClock, 1000);
  initRangeSliders();
  document.getElementById('weight').addEventListener('input', updateBMI);
  document.getElementById('height').addEventListener('input', updateBMI);
});

// ─── Live Clock ───────────────────────────────────────────
function updateClock() {
  const el = document.getElementById('live-time');
  if (!el) return;
  const now = new Date();
  const h = now.getHours();
  const m = String(now.getMinutes()).padStart(2, '0');
  const s = String(now.getSeconds()).padStart(2, '0');
  const ampm = h >= 12 ? 'PM' : 'AM';
  const hr = h % 12 || 12;
  el.textContent = `${hr}:${m}:${s} ${ampm}`;
}

// ─── Radio Pill Selection ─────────────────────────────────
function selectRadio(groupId, el, key) {
  document.querySelectorAll(`#${groupId} .radio-pill`).forEach(b => b.classList.remove('selected'));
  el.classList.add('selected');
  state[key] = el.dataset.val;
}

// ─── Range Slider Init & Update ───────────────────────────
function initRangeSliders() {
  const sliders = ['glucose', 'blood_pressure', 'insulin', 'skin_thickness', 'dpf', 'pregnancies'];
  sliders.forEach(id => {
    const el = document.getElementById(id);
    if (el) {
      updateSliderFill(el);
      el.addEventListener('input', () => updateSliderFill(el));
    }
  });
}

function updateSliderFill(el) {
  const min = parseFloat(el.min);
  const max = parseFloat(el.max);
  const val = parseFloat(el.value);
  const pct = ((val - min) / (max - min)) * 100;
  el.style.setProperty('--pct', pct + '%');

  const outId = el.id + '-val';
  const outEl = document.getElementById(outId);
  if (!outEl) return;

  if (el.id === 'dpf') {
    outEl.textContent = (val / 100).toFixed(2);
  } else {
    outEl.textContent = val;
  }

  // Update status badge
  updateSliderBadge(el.id, val);
}

function updateSliderBadge(id, val) {
  const badge = document.getElementById(id + '-badge');
  if (!badge) return;
  let cls = 'normal', txt = 'Normal';

  if (id === 'glucose') {
    if (val < 100)      { cls = 'normal'; txt = 'Normal'; }
    else if (val < 126) { cls = 'warning'; txt = 'Pre-diabetic'; }
    else                { cls = 'danger'; txt = 'High'; }
  } else if (id === 'blood_pressure') {
    if (val < 80)       { cls = 'normal'; txt = 'Normal'; }
    else if (val < 90)  { cls = 'warning'; txt = 'Elevated'; }
    else                { cls = 'danger'; txt = 'High'; }
  } else if (id === 'insulin') {
    if (val <= 25)      { cls = 'normal'; txt = 'Normal'; }
    else if (val <= 100){ cls = 'warning'; txt = 'Elevated'; }
    else                { cls = 'danger'; txt = 'High'; }
  }

  badge.className = 'range-badge ' + cls;
  badge.textContent = txt;
}

// ─── BMI Calculator ───────────────────────────────────────
function updateBMI() {
  const w = parseFloat(document.getElementById('weight').value);
  const h = parseFloat(document.getElementById('height').value);
  const el = document.getElementById('bmi-display');
  if (!el) return;

  if (w > 0 && h > 0) {
    const bmi = w / ((h / 100) ** 2);
    let cat = '', cls = 'good';
    if      (bmi < 18.5) { cat = 'Underweight';  cls = 'warn'; }
    else if (bmi < 25)   { cat = 'Normal weight'; cls = 'good'; }
    else if (bmi < 30)   { cat = 'Overweight';    cls = 'warn'; }
    else                  { cat = 'Obese';          cls = 'concern'; }

    el.style.display = 'flex';
    el.innerHTML = `
      <span class="bmi-value">${bmi.toFixed(1)}</span>
      <span style="font-size:13px;color:var(--text-muted)">BMI —</span>
      <span style="font-size:13.5px;font-weight:600;color:var(--${cls === 'good' ? 'green' : cls === 'warn' ? 'amber' : 'red'})">${cat}</span>
    `;
  } else {
    el.style.display = 'none';
  }
}

// ─── Page Navigation ──────────────────────────────────────
function goPage(n) {
  // Validate page 1 before proceeding
  if (n === 2) {
    const age = document.getElementById('age').value;
    const wt  = document.getElementById('weight').value;
    const ht  = document.getElementById('height').value;
    if (!age || !wt || !ht) {
      showValidationError('Please fill in Age, Weight, and Height to continue.');
      return;
    }
  }

  // Show/hide pages
  [1, 2, 3].forEach(i => {
    const pg = document.getElementById('page' + i);
    if (pg) pg.style.display = i === n ? 'block' : 'none';
  });

  // Update step indicators
  document.querySelectorAll('.step-item').forEach((item, idx) => {
    const step = idx + 1;
    item.classList.remove('active', 'done');
    if (step < n) item.classList.add('done');
    else if (step === n) item.classList.add('active');
  });

  state.currentPage = n;
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function showValidationError(msg) {
  let el = document.getElementById('val-error');
  if (!el) {
    el = document.createElement('div');
    el.id = 'val-error';
    el.style.cssText = 'background:#FEF2F2;border:1px solid #FECACA;color:#991B1B;padding:10px 14px;border-radius:8px;font-size:13px;margin-top:10px;';
    document.getElementById('page1').appendChild(el);
  }
  el.textContent = msg;
  el.style.display = 'block';
  setTimeout(() => { if (el) el.style.display = 'none'; }, 3500);
}

// ─── Predict ──────────────────────────────────────────────
async function predict() {
  // Build payload
  const payload = {
    age:            parseInt(document.getElementById('age').value) || 0,
    weight:         parseFloat(document.getElementById('weight').value) || 70,
    height:         parseFloat(document.getElementById('height').value) || 170,
    glucose:        parseInt(document.getElementById('glucose').value) || 100,
    blood_pressure: parseInt(document.getElementById('blood_pressure').value) || 80,
    insulin:        parseInt(document.getElementById('insulin').value) || 80,
    skin_thickness: parseInt(document.getElementById('skin_thickness').value) || 20,
    dpf:            parseFloat(document.getElementById('dpf').value) / 100 || 0.5,
    pregnancies:    parseInt(document.getElementById('pregnancies').value) || 0,
    gender:         state.gender,
    activity:       state.activity,
    smoking:        state.smoking,
    family_history: state.familyHistory,
    high_blood_sugar: state.highBloodSugar,
    hypertension:   state.hypertension,
    heart_disease:  state.heartDisease,
    pcos:           state.pcos,
    polyuria:       state.polyuria,
    polydipsia:     state.polydipsia,
    weight_loss:    state.weightLoss,
    blurred_vision: state.blurredVision,
    fatigue:        state.fatigue,
    slow_healing:   state.slowHealing
  };

  // Show loading screen
  document.getElementById('form-section').style.display = 'none';
  document.getElementById('loading-section').style.display = 'flex';
  window.scrollTo({ top: 0, behavior: 'smooth' });

  try {
    const resp = await fetch('/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await resp.json();

    document.getElementById('loading-section').style.display = 'none';

    if (data.success) {
      renderResult(data, payload);
    } else {
      showError(data.error || 'An error occurred.');
    }
  } catch (err) {
    document.getElementById('loading-section').style.display = 'none';
    showError('Could not connect to server. Please try again.');
  }
}

// ─── Render Result ────────────────────────────────────────
function renderResult(data, payload) {
  const section = document.getElementById('result-section');
  const w = payload.weight, h = payload.height;
  const bmi = (w / ((h / 100) ** 2)).toFixed(1);

  const levelText  = { high: 'High Risk', moderate: 'Moderate Risk', low: 'Low Risk' };
  const levelDesc  = {
    high:     'Your health data indicates a <strong>high likelihood</strong> of diabetes or pre-diabetes. We strongly recommend visiting a doctor immediately for a proper blood test (HbA1c or fasting glucose). Early diagnosis can prevent serious complications.',
    moderate: 'Your results show <strong>several risk factors</strong> for developing diabetes. Consult your doctor soon, monitor your blood sugar, and make lifestyle improvements. Acting now can prevent progression.',
    low:      'Your current health data suggests a <strong>lower risk</strong> of diabetes. Maintain your healthy habits, stay active, and schedule regular check-ups to keep it that way.'
  };

  const factors = [
    { label: 'Age', val: payload.age + ' years',  concern: payload.age >= 45, warn: payload.age >= 35 },
    { label: 'BMI',  val: bmi,                      concern: parseFloat(bmi) >= 30, warn: parseFloat(bmi) >= 25 },
    { label: 'Glucose', val: payload.glucose + ' mg/dL', concern: payload.glucose >= 140, warn: payload.glucose >= 100 },
    { label: 'Blood Pressure', val: payload.blood_pressure + ' mmHg', concern: payload.blood_pressure >= 90, warn: payload.blood_pressure >= 80 },
    { label: 'Insulin', val: payload.insulin + ' μU/mL', concern: payload.insulin > 100, warn: payload.insulin > 25 },
    { label: 'Pedigree Score', val: (payload.dpf).toFixed(2), concern: payload.dpf >= 1.5, warn: payload.dpf >= 0.8 },
    { label: 'Pregnancies', val: payload.pregnancies, concern: payload.pregnancies >= 4, warn: payload.pregnancies >= 2 },
    { label: 'Family History', val: state.familyHistory === 'yes' ? 'Present' : 'None / Unknown', concern: state.familyHistory === 'yes', warn: false }
  ];

  const factorsHTML = factors.map(f => {
    let cls = 'good';
    if (f.concern) cls = 'concern';
    else if (f.warn) cls = 'warn';
    return `<div class="factor-item">
      <div class="factor-lbl">${f.label}</div>
      <div class="factor-val ${cls}">${f.val}</div>
    </div>`;
  }).join('');

  const recsHTML = data.recommendations.map((rec, i) => `
    <div class="rec-item" style="animation-delay:${i * 0.06}s">
      <div class="rec-dot">${i + 1}</div>
      <span>${rec}</span>
    </div>`).join('');

  section.innerHTML = `
    <div class="result-hero ${data.level}">
      <div class="risk-level-badge">● ${levelText[data.level]}</div>
      <div class="risk-score-row">
        <div class="risk-score-num">${data.probability}%</div>
        <div>
          <div class="risk-label">${levelText[data.level]}</div>
          <div style="font-size:13px;color:var(--text-muted)">Risk Probability Score</div>
        </div>
      </div>
      <p class="risk-description">${levelDesc[data.level]}</p>
      <div class="prob-bar-wrap">
        <div class="prob-bar-label">
          <span>Diabetes Risk Probability</span>
          <span>${data.probability}%</span>
        </div>
        <div class="prob-bar-track">
          <div class="prob-bar-fill" id="result-bar" style="width:0%"></div>
        </div>
      </div>
      <div style="margin-top:10px;font-size:12px;color:var(--text-muted)">
        Assessment generated on ${data.timestamp}
      </div>
    </div>

    <div class="card">
      <div class="card-header">
        <div class="card-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
            <path d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
          </svg>
        </div>
        <div>
          <div class="card-title">Key Risk Factors Analyzed</div>
          <div class="card-subtitle">Based on your submitted health data</div>
        </div>
      </div>
      <div class="factor-grid">${factorsHTML}</div>
    </div>

    <div class="card">
      <div class="card-header">
        <div class="card-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
            <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
        </div>
        <div>
          <div class="card-title">Personalized Recommendations</div>
          <div class="card-subtitle">Steps you can take based on your results</div>
        </div>
      </div>
      <div class="rec-list">${recsHTML}</div>
    </div>

    <div class="disclaimer">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0zM12 9v4M12 17h.01"/>
      </svg>
      <span><strong>Medical Disclaimer:</strong> This tool provides an educational risk estimate only and is not a medical diagnosis. Always consult a qualified healthcare professional for accurate testing and personalized medical advice.</span>
    </div>

    <button class="btn-restart" onclick="restartForm()">
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/>
      </svg>
      Start a New Assessment
    </button>
  `;

  section.style.display = 'block';
  window.scrollTo({ top: 0, behavior: 'smooth' });

  // Animate bar
  setTimeout(() => {
    const bar = document.getElementById('result-bar');
    if (bar) bar.style.width = data.probability + '%';
  }, 200);
}

// ─── Error Display ────────────────────────────────────────
function showError(msg) {
  document.getElementById('form-section').style.display = 'block';
  alert('Error: ' + msg);
}

// ─── Restart ──────────────────────────────────────────────
function restartForm() {
  document.getElementById('result-section').style.display = 'none';
  document.getElementById('form-section').style.display = 'block';

  // Reset all state
  Object.keys(state).forEach(k => { state[k] = k === 'currentPage' ? 1 : ''; });

  // Clear radio selections
  document.querySelectorAll('.radio-pill.selected').forEach(el => el.classList.remove('selected'));

  // Reset inputs
  ['age', 'weight', 'height'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.value = '';
  });

  // Reset ranges to defaults
  const defaults = { glucose: 100, blood_pressure: 80, insulin: 80, skin_thickness: 20, dpf: 50, pregnancies: 0 };
  Object.entries(defaults).forEach(([id, val]) => {
    const el = document.getElementById(id);
    if (el) { el.value = val; updateSliderFill(el); }
  });

  document.getElementById('bmi-display').style.display = 'none';
  goPage(1);
  window.scrollTo({ top: 0, behavior: 'smooth' });
}
