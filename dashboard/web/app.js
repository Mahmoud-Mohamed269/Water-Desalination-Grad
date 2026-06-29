const API = 'http://localhost:8000/api/v1';

// Format helpers
const num = (v, d = 2) => typeof v === 'number' ? v.toFixed(d) : '—';
const boolMap = (v, t, f) => v === true ? t : (v === false ? f : '—');
const cap = s => typeof s === 'string' ? s.charAt(0).toUpperCase() + s.slice(1) : '—';

// Auto-refresh interval
let refreshTimer = null;
let lastAlertCount = 0;
let shownAlerts = new Set();

async function apiFetch(url, method = 'GET', body = null) {
  try {
    const opts = { method, headers: { 'Content-Type': 'application/json' } };
    if (body) opts.body = JSON.stringify(body);
    const res = await fetch(API + url, opts);
    return await res.json();
  } catch { return null; }
}

// ── NAVIGATION & THEME ─────────────────────────────────────────
function navigate(el, pageId) {
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  el.classList.add('active');
  document.getElementById(`page-${pageId}`).classList.add('active');

  const titles = {
    overview: 'System Overview',
    sensors: 'Live Sensors',
    history: 'Historical Charts',
    predictions: 'ML Predictions',
    chatbot: 'AI Assistant'
  };
  document.getElementById('page-title').textContent = titles[pageId];

  if (pageId === 'history') loadHistory();
}

function toggleTheme() {
  const isDark = document.getElementById('themeToggle').checked;
  document.body.className = isDark ? 'dark' : 'light';
  if (window.charts) {
    Object.values(window.charts).forEach(c => {
      c.options.scales.x.grid.color = isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)';
      c.options.scales.y.grid.color = isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)';
      c.options.plugins.legend.labels.color = isDark ? '#f1f5f9' : '#1e293b';
      c.update();
    });
  }
}

// ── AUTO REFRESH LOOP ──────────────────────────────────────────
async function loadCurrentPage() {
  const btn = document.getElementById('btn-refresh');
  btn.style.opacity = '0.5';
  
  const [liveRes, statusRes] = await Promise.all([
    apiFetch('/sensors/live'),
    apiFetch('/status/device_001') // assuming status endpoint or mock
  ]);
  
  if (liveRes && liveRes.data) {
    updateOverview(liveRes.data);
    updateSensors(liveRes.data);
    document.getElementById('system-status').className = 'status-badge online';
    document.getElementById('system-status').textContent = '● ONLINE';
    
    // Auto run predictions silently
    runPredictions(liveRes.data);
  } else {
    document.getElementById('system-status').className = 'status-badge offline';
    document.getElementById('system-status').textContent = '○ OFFLINE';
  }

  // Update System Status (Diagnostics) if available
  if (statusRes && statusRes.status === 'ok') {
      const s = statusRes.data;
      document.getElementById('ss-cpu').textContent = num(s.cpu_temp_celsius, 1) + ' °C';
      document.getElementById('ss-heap').textContent = Math.round(s.heap_free_bytes / 1024) + ' KB';
      document.getElementById('ss-rssi').textContent = s.wifi_rssi + ' dBm';
      
      const healthGrid = document.getElementById('health-grid');
      if (s.sensor_health && healthGrid) {
          healthGrid.innerHTML = '';
          for (const [sensor, state] of Object.entries(s.sensor_health)) {
              healthGrid.innerHTML += `<div class="health-badge ${state}"><span class="h-dot">●</span> ${sensor.toUpperCase()}</div>`;
          }
      }
  }

  btn.style.opacity = '1';
}

function startAutoRefresh() {
  loadCurrentPage();
  refreshTimer = setInterval(loadCurrentPage, 5000);
  setInterval(pollAlerts, 10000); // Check alerts every 10s
}

// ── TOAST NOTIFICATIONS ─────────────────────────────────────────
function showToast(title, message, severity) {
  const container = document.getElementById('toast-container');
  const toast = document.createElement('div');
  toast.className = `toast ${severity}`;
  toast.innerHTML = `
    <button class="toast-close" onclick="this.parentElement.remove()">&times;</button>
    <div class="toast-title">${title}</div>
    <div class="toast-msg">${message}</div>
  `;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.animation = 'slideOutRight 0.3s ease-in forwards';
    setTimeout(() => toast.remove(), 300);
  }, 8000);
}

async function pollAlerts() {
  const res = await apiFetch('/alerts/history?limit=5');
  if (res && res.alerts) {
    res.alerts.forEach(a => {
      const id = a.timestamp + a.sensor;
      if (!shownAlerts.has(id)) {
        shownAlerts.add(id);
        showToast(`Alert: ${a.sensor}`, a.message, a.severity);
      }
    });
  }
}

// ── UI UPDATERS ────────────────────────────────────────────────
function updateOverview(d) {
  document.getElementById('ov-status').textContent = d.pump_status === 'running' ? 'Active' : 'Standby';
  document.getElementById('ov-status').style.color = d.pump_status === 'running' ? 'var(--success)' : 'var(--text)';
  document.getElementById('ov-pump').textContent = cap(d.pump_status);
  
  document.getElementById('ov-recovery').textContent = num(d.recovery_rate, 1) + '%';
  document.getElementById('ov-rejection').textContent = num(d.rejection_rate, 1) + '%';

  const mini = document.getElementById('mini-sensors');
  mini.innerHTML = `
    <div class="sensor-card">
      <div class="sensor-name">pH Feed</div>
      <div class="sensor-val">${num(d.ph_feed, 2)}</div>
    </div>
    <div class="sensor-card">
      <div class="sensor-name">TDS Feed</div>
      <div class="sensor-val">${num(d.tds_feed, 1)}<span class="sensor-unit">ppm</span></div>
    </div>
    <div class="sensor-card">
      <div class="sensor-name">Pressure Feed</div>
      <div class="sensor-val">${num(d.pressure_feed, 2)}<span class="sensor-unit">bar</span></div>
    </div>
    <div class="sensor-card">
      <div class="sensor-name">Flow Feed</div>
      <div class="sensor-val">${num(d.flow_rate_feed, 1)}<span class="sensor-unit">L/min</span></div>
    </div>
  `;
}

function updateSensors(d) {
  const n1 = document.getElementById('node1-sensors');
  n1.innerHTML = `
    <div class="sensor-card"><div class="sensor-name">pH Feed</div><div class="sensor-val">${num(d.ph_feed)}</div></div>
    <div class="sensor-card"><div class="sensor-name">pH Permeate</div><div class="sensor-val">${num(d.ph_permeate)}</div></div>
    <div class="sensor-card"><div class="sensor-name">TDS Feed</div><div class="sensor-val">${num(d.tds_feed, 1)} <span class="sensor-unit">ppm</span></div></div>
    <div class="sensor-card"><div class="sensor-name">TDS Permeate</div><div class="sensor-val">${num(d.tds_permeate, 1)} <span class="sensor-unit">ppm</span></div></div>
    <div class="sensor-card"><div class="sensor-name">Turbidity</div><div class="sensor-val">${num(d.turbidity_feed)} <span class="sensor-unit">NTU</span></div></div>
    <div class="sensor-card"><div class="sensor-name">Temp Feed</div><div class="sensor-val">${num(d.temperature_feed, 1)} <span class="sensor-unit">°C</span></div></div>
    <div class="sensor-card"><div class="sensor-name">Temp Permeate</div><div class="sensor-val">${num(d.temperature_permeate, 1)} <span class="sensor-unit">°C</span></div></div>
    <div class="sensor-card"><div class="sensor-name">Pressure</div><div class="sensor-val">${num(d.pressure_feed)} <span class="sensor-unit">bar</span></div></div>
    <div class="sensor-card"><div class="sensor-name">Flow Feed</div><div class="sensor-val">${num(d.flow_rate_feed, 1)} <span class="sensor-unit">L/min</span></div></div>
    <div class="sensor-card"><div class="sensor-name">Flow Permeate</div><div class="sensor-val">${num(d.flow_rate_permeate, 1)} <span class="sensor-unit">L/min</span></div></div>
    <div class="sensor-card"><div class="sensor-name">Feed Tank</div><div class="sensor-val">${d.water_level_feed_tank > 0 ? 'Full' : 'Empty'}</div></div>
    <div class="sensor-card"><div class="sensor-name">Product Tank</div><div class="sensor-val">${d.water_level_product_tank > 0 ? 'Full' : 'Empty'}</div></div>
    <div class="sensor-card"><div class="sensor-name">Valve</div><div class="sensor-val">${cap(d.valve_status)}</div></div>
  `;

  const n2 = document.getElementById('node2-sensors');
  n2.innerHTML = `
    <div class="sensor-card"><div class="sensor-name">Ambient Temp</div><div class="sensor-val">${num(d.ambient_temp, 1)} <span class="sensor-unit">°C</span></div></div>
    <div class="sensor-card"><div class="sensor-name">Humidity</div><div class="sensor-val">${num(d.ambient_humidity, 1)} <span class="sensor-unit">%</span></div></div>
    <div class="sensor-card"><div class="sensor-name">Tank 1 Level</div><div class="sensor-val">${num(d.tank1_level_cm, 1)} <span class="sensor-unit">cm</span></div></div>
    <div class="sensor-card"><div class="sensor-name">Tank 2 Level</div><div class="sensor-val">${num(d.tank2_level_cm, 1)} <span class="sensor-unit">cm</span></div></div>
    <div class="sensor-card"><div class="sensor-name">Gas 1</div><div class="sensor-val">${num(d.gas_1_ppm, 0)} <span class="sensor-unit">ppm</span></div></div>
    <div class="sensor-card"><div class="sensor-name">Gas 2</div><div class="sensor-val">${num(d.gas_2_ppm, 0)} <span class="sensor-unit">ppm</span></div></div>
    <div class="sensor-card"><div class="sensor-name">Fan 1</div><div class="sensor-val">${boolMap(d.fan_1_status, 'ON', 'OFF')}</div></div>
    <div class="sensor-card"><div class="sensor-name">Fan 2</div><div class="sensor-val">${boolMap(d.fan_2_status, 'ON', 'OFF')}</div></div>
  `;
}

// ── HISTORY CHARTS ─────────────────────────────────────────────
window.charts = {};
async function loadHistory() {
  const res = await apiFetch('/sensors/history?limit=30');
  if (!res || !res.readings) return;
  
  const labels = res.readings.map(r => {
      const d = new Date(r.timestamp);
      return `${d.getHours().toString().padStart(2,'0')}:${d.getMinutes().toString().padStart(2,'0')}:${d.getSeconds().toString().padStart(2,'0')}`;
  });

  const extract = (key) => res.readings.map(r => r[key] || 0);

  createChart('chart-ph', labels, 
      [{label: 'Feed pH', data: extract('ph_feed'), borderColor: '#00d2fc'},
       {label: 'Permeate pH', data: extract('ph_permeate'), borderColor: '#7c3aed'}]);
       
  createChart('chart-tds', labels, 
      [{label: 'Feed TDS', data: extract('tds_feed'), borderColor: '#fbbf24'},
       {label: 'Permeate TDS', data: extract('tds_permeate'), borderColor: '#22d3a0'}]);
       
  createChart('chart-turbidity', labels, 
      [{label: 'Feed Turbidity', data: extract('turbidity_feed'), borderColor: '#f43f5e'}]);
      
  createChart('chart-pressure', labels, 
      [{label: 'Feed Pressure', data: extract('pressure_feed'), borderColor: '#a78bfa'}]);

  createChart('chart-flow', labels, 
      [{label: 'Feed Flow', data: extract('flow_rate_feed'), borderColor: '#00d2fc'},
       {label: 'Permeate Flow', data: extract('flow_rate_permeate'), borderColor: '#7c3aed'}]);

  createChart('chart-temp', labels, 
      [{label: 'Feed Temp', data: extract('temperature_feed'), borderColor: '#fbbf24'},
       {label: 'Permeate Temp', data: extract('temperature_permeate'), borderColor: '#22d3a0'}]);
}

function createChart(id, labels, datasets) {
    const ctx = document.getElementById(id);
    if (!ctx) return;
    
    if (window.charts[id]) {
        window.charts[id].data.labels = labels;
        window.charts[id].data.datasets.forEach((ds, i) => {
            ds.data = datasets[i].data;
        });
        window.charts[id].update();
        return;
    }

    const isDark = document.body.classList.contains('dark');
    const gridColor = isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)';
    const textColor = isDark ? '#f1f5f9' : '#1e293b';

    window.charts[id] = new Chart(ctx, {
        type: 'line',
        data: { labels, datasets: datasets.map(d => ({...d, tension: 0.4, borderWidth: 2, pointRadius: 0})) },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: { duration: 0 },
            scales: {
                x: { grid: { color: gridColor }, ticks: { maxTicksLimit: 6, color: textColor } },
                y: { grid: { color: gridColor }, ticks: { color: textColor } }
            },
            plugins: { legend: { labels: { color: textColor } } }
        }
    });
}

// ── ML PREDICTIONS ─────────────────────────────────────────────
async function loadPredictions() {
  const liveRes = await apiFetch('/sensors/live');
  if (liveRes && liveRes.data) {
    runPredictions(liveRes.data);
  }
}

async function runPredictions(d) {
  const reqBody = {
    pH_before: d.ph_feed || 7.0,
    TDS_before: d.tds_feed || 300.0,
    Turbidity_before: d.turbidity_feed || 2.0,
    Temperature_before: d.temperature_feed || 25.0,
    Pressure_before: d.pressure_feed || 2.5,
    pH_after: d.ph_permeate || 6.8,
    TDS_after: d.tds_permeate || 30.0,
    Turbidity_after: 0.1, // assuming permeate turbidity is ~0
    Temperature_after: d.temperature_permeate || 25.0,
    Efficiency: d.recovery_rate || 50.0,
    TDS_Reduction: d.rejection_rate || 90.0,
    Turbidity_Reduction: 95.0,
    pH_Change: Math.abs((d.ph_feed||7)-(d.ph_permeate||7))
  };

  const preds = await apiFetch('/predict/', 'POST', reqBody);

  if (preds?.status === 'ok') {
    const p = preds.predictions;
    const wq = p?.water_quality || {};
    const ms = p?.membrane_status || {};

    // Update main overview cards
    document.getElementById('ov-wq').textContent = wq.label ?? '—';
    document.getElementById('ov-wq').style.color = wq.label === 'Excellent' ? 'var(--success)' : 'var(--warning)';
    document.getElementById('ov-ms').textContent = ms.label ?? '—';
    document.getElementById('ov-ms').style.color = ms.label === 'Healthy' ? 'var(--success)' : 'var(--danger)';

    // Update predictions page cards
    if (document.getElementById('pred-wq-label')) {
      document.getElementById('pred-wq-label').textContent = wq.label ?? '—';
      document.getElementById('pred-wq-label').style.color = wq.label === 'Excellent' ? 'var(--success)' : 'var(--warning)';
      document.getElementById('pred-wq-conf').textContent = wq.confidence ? `Confidence: ${wq.confidence}%` : '';
      document.getElementById('pred-wq-bar').style.width = (wq.confidence ?? 0) + '%';
      document.getElementById('pred-wq-bar').style.background = wq.label === 'Excellent' ? 'var(--success)' : 'var(--warning)';
    }

    if (document.getElementById('pred-ms-label')) {
      document.getElementById('pred-ms-label').textContent = ms.label ?? '—';
      document.getElementById('pred-ms-label').style.color = ms.label === 'Healthy' ? 'var(--success)' : 'var(--danger)';
      document.getElementById('pred-ms-conf').textContent = ms.confidence ? `Confidence: ${ms.confidence}%` : '';
      document.getElementById('pred-ms-bar').style.width = (ms.confidence ?? 0) + '%';
      document.getElementById('pred-ms-bar').style.background = ms.label === 'Healthy' ? 'var(--success)' : 'var(--danger)';
    }
  }
}

// ── CHATBOT ───────────────────────────────────────────────────────
function formatMarkdown(text) {
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/\n/g, '<br>');
}

function addBubble(text, role) {
  const msgs = document.getElementById('chat-messages');
  const div = document.createElement('div');
  div.className = `chat-bubble ${role}`;
  if (role === 'thinking') {
    div.innerHTML = `<span class="spinner"></span> &nbsp;Thinking…`;
  } else {
    const label = role === 'user' ? 'You' : 'Gemini AI';
    div.innerHTML = `<strong>${label}</strong><div style="margin-top: 5px; line-height: 1.5;">${formatMarkdown(text)}</div>`;
  }
  msgs.appendChild(div);
  msgs.scrollTop = msgs.scrollHeight;
  return div;
}

async function sendMessage() {
  const input = document.getElementById('chat-input');
  const msg = input.value.trim();
  if (!msg) return;

  input.value = '';
  addBubble(msg, 'user');
  const thinking = addBubble('', 'thinking');

  const sensorsRes = await apiFetch('/sensors/live');
  const d = sensorsRes?.data || {};

  const contextData = {
    ph_feed: d.ph_feed,
    tds_feed: d.tds_feed,
    pressure_feed: d.pressure_feed,
    flow_rate_feed: d.flow_rate_feed,
    recovery_rate: d.recovery_rate,
    pump_status: d.pump_status
  };

  const res = await apiFetch('/chat/', 'POST', { message: msg, context: contextData });
  thinking.remove();

  if (res?.status === 'ok') {
    addBubble(res.reply, 'assistant');
  } else {
    addBubble('Sorry, I encountered an error. Please try again.', 'assistant');
  }
}

// Init
window.onload = startAutoRefresh;
