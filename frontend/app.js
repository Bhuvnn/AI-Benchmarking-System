/* ══════════════════════════════════════════════════════════════
   AI Benchmarking System — App (SPA)
   Flow: Home → Projects → Runs → Run Detail | Analytics (combined)
   ══════════════════════════════════════════════════════════════ */

const API = window.location.origin;

// Colour palette for charts
const VERSION_COLORS = [
  '#22d3ee', '#10b981', '#f59e0b', '#f87171',
  '#8b5cf6', '#ec4899', '#fb923c', '#34d399',
];

// App-level state
const S = {
  view: 'dashboard',
  projects: [],
  pid: null, pname: null,
  runs: [], rid: null, rver: null,
};

// ═══════════════════════════════════════════
// INIT
// ═══════════════════════════════════════════
document.addEventListener('DOMContentLoaded', () => {
  mkToastBox();
  checkApi();
  loadDashboard();
});

async function api(path) {
  const r = await fetch(`${API}${path}`);
  if (!r.ok) throw new Error(`HTTP ${r.status}`);
  return r.json();
}

async function checkApi() {
  const d = document.getElementById('api-dot');
  const t = document.getElementById('api-status-text');
  try {
    await api('/projects');
    d.className = 'conn-dot ok'; t.textContent = 'API Connected';
  } catch {
    d.className = 'conn-dot fail'; t.textContent = 'API Offline';
  }
}

// ═══════════════════════════════════════════
// NAVIGATION
// ═══════════════════════════════════════════
function navigateTo(view, p = {}) {
  document.querySelectorAll('.view').forEach(v => v.classList.add('hidden'));
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  S.view = view;

  switch (view) {

    case 'dashboard':
      show('view-dashboard'); activate('nav-dashboard');
      setBc([{ l: 'Home', active: true }]);
      loadDashboard();
      break;

    case 'projects':
      show('view-projects'); activate('nav-projects');
      setBc([{ l: 'Projects', active: true }]);
      loadProjects();
      break;

    // ── Analytics: combined dashboard + compare ──
    case 'analytics':
      S.pid = p.projectId || S.pid; S.pname = p.projectName || S.pname;
      show('view-analytics'); activate('nav-projects');
      setBc([
        { l: 'Projects', fn: () => navigateTo('projects') },
        { l: S.pname, fn: () => navigateTo('runs', { projectId: S.pid, projectName: S.pname }) },
        { l: 'Analytics', active: true },
      ]);
      loadAnalytics(S.pid);
      break;

    case 'runs':
      S.pid = p.projectId || S.pid; S.pname = p.projectName || S.pname;
      show('view-runs'); activate('nav-projects');
      document.getElementById('runs-title').textContent = S.pname;
      document.getElementById('runs-desc').textContent = 'All training versions · click to view details';
      setBc([
        { l: 'Projects', fn: () => navigateTo('projects') },
        { l: S.pname, active: true },
      ]);
      loadRuns(S.pid);
      break;

    case 'run-detail':
      S.rid = p.runId; S.rver = p.versionName;
      show('view-run-detail'); activate('nav-projects');
      document.getElementById('rd-version').textContent = p.versionName;
      document.getElementById('rd-project').textContent = S.pname;
      document.getElementById('rd-id').textContent = `Run #${p.runId}`;
      setBc([
        { l: 'Projects', fn: () => navigateTo('projects') },
        { l: S.pname, fn: () => navigateTo('runs', { projectId: S.pid, projectName: S.pname }) },
        { l: p.versionName, active: true },
      ]);
      loadRunDetail(S.pid, p.runId);
      break;

    case 'error':
      show('view-error');
      if (p.message) document.getElementById('error-message').textContent = p.message;
      break;
  }
}

// Sidebar "Compare" button → goes to unified analytics
function quickCompare() {
  if (S.pid) navigateTo('analytics', { projectId: S.pid, projectName: S.pname });
  else if (S.projects.length > 0) navigateTo('analytics', { projectId: S.projects[0].id, projectName: S.projects[0].project_name });
  else navigateTo('projects');
}

function show(id) { document.getElementById(id).classList.remove('hidden'); }
function activate(id) { document.getElementById(id).classList.add('active'); }

function setBc(items) {
  const c = document.getElementById('breadcrumbs'); c.innerHTML = '';
  items.forEach((it, i) => {
    if (i > 0) { const s = document.createElement('span'); s.className = 'bc-sep'; s.textContent = '›'; c.appendChild(s); }
    const sp = document.createElement('span'); sp.className = 'bc' + (it.active ? ' active' : '');
    sp.textContent = it.l;
    if (it.fn) { sp.style.cursor = 'pointer'; sp.onclick = it.fn; }
    c.appendChild(sp);
  });
}

function refreshCurrentView() {
  const b = document.getElementById('btn-refresh'); b.classList.add('spin');
  setTimeout(() => b.classList.remove('spin'), 800);
  switch (S.view) {
    case 'dashboard':  loadDashboard(); break;
    case 'projects':   loadProjects(); break;
    case 'analytics':  loadAnalytics(S.pid); break;
    case 'runs':       loadRuns(S.pid); break;
    case 'run-detail': loadRunDetail(S.pid, S.rid); break;
    default:           navigateTo('dashboard');
  }
}

// ═══════════════════════════════════════════
// PAGE 1: HOME / DASHBOARD
// ═══════════════════════════════════════════
async function loadDashboard() {
  try {
    const d = await api('/projects');
    S.projects = d.projects || [];
    document.getElementById('kpi-projects').textContent = S.projects.length;
    document.getElementById('kpi-active').textContent =
      S.projects.filter(p => (p.status || '').toLowerCase() === 'active').length;

    let totalRuns = 0, latest = null;
    for (const pr of S.projects) {
      try {
        const rd = await api(`/projects/${pr.id}/runs`);
        const runs = rd.runs || [];
        totalRuns += runs.length;
        for (const r of runs) {
          if (r.created_at) { const dt = new Date(r.created_at); if (!latest || dt > latest) latest = dt; }
        }
      } catch {}
    }
    document.getElementById('kpi-runs').textContent = totalRuns;
    document.getElementById('kpi-latest').textContent = latest ? relTime(latest) : 'N/A';

    const box = document.getElementById('dashboard-projects');
    if (!S.projects.length) { box.innerHTML = '<div class="empty-msg" style="grid-column:1/-1">No projects yet. Use the SDK to create your first run!</div>'; return; }
    box.innerHTML = S.projects.slice(0, 6).map((p, i) => projectCard(p, i)).join('');

  } catch (err) {
    console.error(err);
    toast('Could not reach the API server', 'err');
    navigateTo('error');
  }
}

// ═══════════════════════════════════════════
// PAGE 2: ALL PROJECTS
// ═══════════════════════════════════════════
async function loadProjects() {
  const box = document.getElementById('projects-list');
  box.innerHTML = '<div class="loader" style="grid-column:1/-1"><div class="spinner"></div></div>';
  try {
    const d = await api('/projects');
    S.projects = d.projects || [];
    if (!S.projects.length) { box.innerHTML = '<div class="empty-msg" style="grid-column:1/-1">No projects found.</div>'; return; }
    box.innerHTML = S.projects.map((p, i) => projectCard(p, i)).join('');
  } catch {
    box.innerHTML = '<div class="empty-msg" style="grid-column:1/-1">Failed to load projects.</div>';
    toast('Failed to load projects', 'err');
  }
}

function projectCard(p, i) {
  const sc = (p.status || '').toLowerCase() === 'active' ? 'active' : 'inactive';
  return `<div class="p-card" onclick="navigateTo('runs',{projectId:${p.id},projectName:'${esc(p.project_name)}'})" style="animation-delay:${i * 55}ms">
    <div class="p-card-top"><span class="p-name">${esc(p.project_name)}</span><span class="p-id">#${p.id}</span></div>
    <span class="status-pill ${sc}"><span></span>${p.status || 'Unknown'}</span>
    <div class="p-card-bottom">
      <span class="p-action">View Versions <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="9 18 15 12 9 6"/></svg></span>
    </div>
  </div>`;
}

// ═══════════════════════════════════════════
// PROJECT ANALYTICS — combined dashboard + compare
// Sections: KPIs · Legend · Metric cards · Trend chart ·
//           Bar chart · Parameter evolution · Dataset overview
// ═══════════════════════════════════════════
async function loadAnalytics(pid) {
  console.log('[Analytics] loadAnalytics called, pid =', pid, '| S.pid =', S.pid);

  if (!pid) {
    toast('No project selected — go to Projects first', 'err');
    return;
  }

  const projNameEl = document.getElementById('an-proj-name');
  if (projNameEl) projNameEl.textContent = S.pname || 'Project';

  // Show loading placeholders
  ['an-kpi-best', 'an-kpi-runs', 'an-kpi-improvement', 'an-kpi-latest'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.textContent = '…';
  });
  ['an-trend-chart', 'an-bar-chart', 'an-metric-cards', 'an-params-table', 'an-dataset-overview'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.innerHTML = '<div class="loader"><div class="spinner"></div></div>';
  });
  document.getElementById('an-legend').innerHTML = '';

  try {
    const data = await api(`/projects/${pid}/compare`);
    const runs = (data.runs || []).sort((a, b) =>
      a.version_name.localeCompare(b.version_name, undefined, { numeric: true })
    );

    if (!runs.length) {
      ['an-kpi-best', 'an-kpi-runs', 'an-kpi-improvement', 'an-kpi-latest'].forEach(id =>
        document.getElementById(id).textContent = '—'
      );
      document.getElementById('an-legend').innerHTML = '<div class="empty-msg">No runs found for this project.</div>';
      return;
    }

    // Determine primary metric for KPI calculation
    const allMetricNames = [...new Set(runs.flatMap(r => (r.metrics || []).map(m => m.metric_name)))];
    const metricPriority = ['accuracy', 'f1_score', 'auc_roc', 'precision', 'recall'];
    const primaryKey = metricPriority.find(k => allMetricNames.includes(k)) || allMetricNames[0] || null;

    const getVal = (run, key) => {
      const m = (run.metrics || []).find(x => x.metric_name === key);
      return m ? parseFloat(m.metric_value) : null;
    };
    const fmtM = v => v === null ? '—' : (v <= 1 ? (v * 100).toFixed(1) + '%' : v.toFixed(3));

    // KPIs
    if (primaryKey) {
      const vals = runs.map(r => getVal(r, primaryKey)).filter(v => v !== null);
      const bestVal  = vals.length ? Math.max(...vals) : null;
      const firstVal = vals[0] ?? null;
      const lastVal  = vals[vals.length - 1] ?? null;
      const improvement = (firstVal !== null && lastVal !== null && firstVal !== 0)
        ? ((lastVal - firstVal) / Math.abs(firstVal) * 100) : null;
      document.getElementById('an-kpi-best').textContent = fmtM(bestVal);
      document.getElementById('an-kpi-improvement').textContent =
        improvement !== null ? (improvement >= 0 ? '+' : '') + improvement.toFixed(1) + '%' : '—';
    } else {
      document.getElementById('an-kpi-best').textContent = '—';
      document.getElementById('an-kpi-improvement').textContent = '—';
    }
    document.getElementById('an-kpi-runs').textContent = runs.length;
    document.getElementById('an-kpi-latest').textContent = runs[runs.length - 1]?.version_name || '—';

    // Render all sections
    renderAnLegend(runs);
    renderAnMetricCards(runs, allMetricNames);
    renderAnTrendChart(runs, allMetricNames);
    renderAnBarChart(runs, allMetricNames);
    renderAnParamsTable(runs);
    renderAnDatasetOverview(runs);

  } catch (err) {
    console.error(err);
    toast('Failed to load project analytics', 'err');
  }
}

// ── Version colour legend ──
function renderAnLegend(runs) {
  document.getElementById('an-legend').innerHTML =
    runs.map((r, i) =>
      `<div class="legend-item"><div class="legend-dot" style="background:${VERSION_COLORS[i % VERSION_COLORS.length]}"></div>${esc(r.version_name)}</div>`
    ).join('');
}

// ── Per-metric mini cards with sparkline + % delta ──
function renderAnMetricCards(runs, allMetricNames) {
  const container = document.getElementById('an-metric-cards');
  container.innerHTML = '';
  const metricsToShow = allMetricNames.slice(0, 5);
  if (!metricsToShow.length) return;

  let html = '';
  metricsToShow.forEach(mn => {
    const values = runs.map(r => {
      const m = (r.metrics || []).find(x => x.metric_name === mn);
      return m ? parseFloat(m.metric_value) : null;
    });
    const valid = values.filter(v => v !== null);
    if (!valid.length) return;

    const latest  = valid[valid.length - 1];
    const isLoss  = mn.toLowerCase().includes('loss');
    let diffHtml  = '<span class="cmc-diff neutral">—</span>';
    if (valid.length > 1) {
      const prev = valid[valid.length - 2];
      if (prev !== 0) {
        const pct    = ((latest - prev) / Math.abs(prev)) * 100;
        const isGood = isLoss ? pct < 0 : pct > 0;
        diffHtml = `<span class="cmc-diff ${pct === 0 ? 'neutral' : isGood ? 'up' : 'down'}">${pct > 0 ? '+' : ''}${pct.toFixed(2)}%</span>`;
      }
    }

    const Hc = 40, Wc = 160;
    const minM = Math.min(...valid), maxM = Math.max(...valid);
    const pts = values
      .map((v, i) => v !== null ? { x: (i / (runs.length - 1 || 1)) * Wc, y: Hc - ((v - minM) / (maxM - minM || 1)) * Hc } : null)
      .filter(Boolean);

    let miSvg = `<svg viewBox="-5 -5 ${Wc + 10} ${Hc + 10}" preserveAspectRatio="none">`;
    if (pts.length > 1)
      miSvg += `<path d="${pts.map((p, i) => `${i === 0 ? 'M' : 'L'}${p.x},${p.y}`).join(' ')}" class="cmc-line" stroke="${VERSION_COLORS[0]}" fill="none"/>`;
    pts.forEach((p, i) => { miSvg += `<circle cx="${p.x}" cy="${p.y}" r="${i === pts.length - 1 ? 3.5 : 2}" class="cmc-dot ${i === pts.length - 1 ? 'last' : ''}"/>`; });
    miSvg += '</svg>';

    const dv = latest <= 1 ? (latest * 100).toFixed(2) + '%' : latest.toFixed(4);
    html += `<div class="cmp-metric-card">
      <div class="cmc-head">
        <div class="cmc-title">${capitalize(mn)}</div>
        <div class="cmc-icon"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg></div>
      </div>
      <div class="cmc-val">${dv}</div>
      ${diffHtml}
      <div class="cmc-chart">${miSvg}</div>
    </div>`;
  });
  container.innerHTML = html;
}

// ── Performance Trend — SVG line chart with hover tooltips ──
function renderAnTrendChart(runs, allMetricNames) {
  const container = document.getElementById('an-trend-chart');
  if (!container || !runs.length) return;

  const sub = document.getElementById('an-trend-sub');
  if (sub) sub.textContent = allMetricNames.slice(0, 4).map(capitalize).join(' · ') + ` across ${runs.length} versions`;

  const W = 700, H = 260, pad = { t: 28, r: 24, b: 44, l: 54 };
  const cw = W - pad.l - pad.r, ch = H - pad.t - pad.b;

  const series = {};
  allMetricNames.forEach(mn => {
    series[mn] = runs.map(r => {
      const m = (r.metrics || []).find(x => x.metric_name === mn);
      return { v: m ? parseFloat(m.metric_value) : null, ver: r.version_name };
    });
  });

  const allVals = Object.values(series).flatMap(s => s.map(p => p.v).filter(v => v !== null));
  if (!allVals.length) { container.innerHTML = '<div class="empty-msg">No metric data available</div>'; return; }

  let minV = Math.min(...allVals), maxV = Math.max(...allVals);
  const rng = maxV - minV || 1;
  minV = Math.max(0, minV - rng * 0.12); maxV += rng * 0.12;

  const xPos = i => pad.l + (runs.length > 1 ? (i / (runs.length - 1)) * cw : cw / 2);
  const yPos = v => pad.t + ch - ((v - minV) / (maxV - minV)) * ch;

  let svg = `<svg viewBox="0 0 ${W} ${H}" preserveAspectRatio="xMidYMid meet" style="width:100%;height:100%">`;

  // Grid + Y-axis labels
  for (let i = 0; i <= 5; i++) {
    const y = pad.t + (ch / 5) * i;
    const v = maxV - ((maxV - minV) / 5) * i;
    svg += `<line x1="${pad.l}" y1="${y}" x2="${W - pad.r}" y2="${y}" class="chart-grid-line"/>`;
    svg += `<text x="${pad.l - 8}" y="${y + 4}" text-anchor="end" class="chart-axis-label">${v <= 1 ? (v * 100).toFixed(0) + '%' : v.toFixed(3)}</text>`;
  }

  // X-axis version labels + vertical guides
  runs.forEach((r, i) => {
    const x = xPos(i);
    svg += `<line x1="${x}" y1="${pad.t}" x2="${x}" y2="${pad.t + ch}" stroke="rgba(255,255,255,.025)" stroke-width="1"/>`;
    svg += `<text x="${x}" y="${H - 6}" text-anchor="middle" class="chart-axis-label" style="fill:var(--tx2);font-weight:600">${esc(r.version_name)}</text>`;
  });

  // Series: gradient area + line + dots
  allMetricNames.forEach((mn, mi) => {
    const color = VERSION_COLORS[mi % VERSION_COLORS.length];
    const pts = series[mn]
      .map((p, i) => p.v !== null ? { x: xPos(i), y: yPos(p.v), v: p.v, ver: p.ver } : null)
      .filter(Boolean);
    if (!pts.length) return;
    const gid = `ang${mi}`;
    svg += `<defs><linearGradient id="${gid}" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="${color}" stop-opacity="0.28"/><stop offset="100%" stop-color="${color}" stop-opacity="0"/></linearGradient></defs>`;
    if (pts.length > 1) {
      const lp = pts.map((p, i) => `${i === 0 ? 'M' : 'L'}${p.x.toFixed(1)},${p.y.toFixed(1)}`).join(' ');
      const ap = `M${pts[0].x},${pad.t + ch} ` + pts.map(p => `L${p.x.toFixed(1)},${p.y.toFixed(1)}`).join(' ') + ` L${pts[pts.length - 1].x},${pad.t + ch} Z`;
      svg += `<path d="${ap}" fill="url(#${gid})" class="chart-area"/>`;
      svg += `<path d="${lp}" fill="none" stroke="${color}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" opacity="0.9"/>`;
    }
    pts.forEach((p, pi) => {
      svg += `<circle cx="${p.x.toFixed(1)}" cy="${p.y.toFixed(1)}" r="${pi === pts.length - 1 ? 5 : 3.5}" fill="${color}" stroke="var(--bg-card)" stroke-width="2" class="chart-dot" data-metric="${esc(mn)}" data-val="${p.v}" data-ver="${esc(p.ver)}"/>`;
    });
  });
  svg += '</svg>';

  const legend = `<div style="display:flex;flex-wrap:wrap;gap:14px;padding:10px 20px 14px;border-top:1px solid var(--bdr)">
    ${allMetricNames.map((mn, i) => `<div style="display:flex;align-items:center;gap:6px;font-size:.72rem;color:var(--tx2)"><div style="width:14px;height:3px;border-radius:2px;background:${VERSION_COLORS[i % VERSION_COLORS.length]}"></div>${capitalize(mn)}</div>`).join('')}
  </div>`;

  container.innerHTML = svg + `<div class="chart-tooltip" id="an-tt"></div>` + legend;

  // Hover tooltips
  const tt = document.getElementById('an-tt');
  container.querySelectorAll('.chart-dot').forEach(dot => {
    dot.addEventListener('mouseenter', () => {
      const svgEl = container.querySelector('svg');
      const sr = svgEl.getBoundingClientRect();
      const cx = parseFloat(dot.getAttribute('cx')) * (sr.width / W);
      const cy = parseFloat(dot.getAttribute('cy')) * (sr.height / H);
      const v = parseFloat(dot.dataset.val);
      tt.innerHTML = `<div class="tt-metric">${dot.dataset.metric}</div><div class="tt-val">${dot.dataset.ver}: ${v <= 1 ? (v * 100).toFixed(2) + '%' : v.toFixed(4)}</div>`;
      tt.classList.add('show'); tt.style.left = (cx + 12) + 'px'; tt.style.top = (cy - 18) + 'px';
    });
    dot.addEventListener('mouseleave', () => tt.classList.remove('show'));
  });
}

// ── Grouped Bar Chart ──
function renderAnBarChart(runs, allMetricNames) {
  const container = document.getElementById('an-bar-chart');
  if (!container) return;

  const allMetrics = allMetricNames.slice(0, 5);
  let allVals = [];
  runs.forEach(r => allMetrics.forEach(mn => {
    const m = (r.metrics || []).find(x => x.metric_name === mn);
    if (m) allVals.push(Math.abs(parseFloat(m.metric_value)));
  }));
  const maxVal = Math.max(...allVals, 0.01);

  // Y-axis ticks
  const ticks = [100, 75, 50, 25, 0];
  let yAxis = '<div class="bar-y-axis">';
  ticks.forEach(t => {
    const val = maxVal * t / 100;
    const label = maxVal <= 1 ? (val * 100).toFixed(0) + '%' : val.toFixed(2);
    yAxis += `<div class="bar-y-tick"><span class="bar-y-label">${label}</span></div>`;
  });
  yAxis += '</div>';

  // Bar groups per version
  let bars = '<div class="bar-chart-container">';
  runs.forEach((r, ri) => {
    bars += '<div class="bar-group"><div class="bar-group-bars">';
    allMetrics.forEach((mn, mi) => {
      const m = (r.metrics || []).find(x => x.metric_name === mn);
      const v = m ? parseFloat(m.metric_value) : 0;
      const pct = Math.min((Math.abs(v) / maxVal) * 100, 100);
      const color = VERSION_COLORS[mi % VERSION_COLORS.length];
      bars += `<div class="bar-single" style="height:${Math.max(pct, 2)}%;background:${color};animation-delay:${ri * 80 + mi * 40}ms" data-metric="${esc(mn)}" data-val="${v}" data-ver="${esc(r.version_name)}"><div class="bar-val">${v <= 1 ? (v * 100).toFixed(1) + '%' : v.toFixed(3)}</div></div>`;
    });
    bars += `</div><div class="bar-group-label">${esc(r.version_name)}</div></div>`;
  });
  bars += '</div>';

  container.innerHTML = `<div class="bar-chart-wrap" style="position:relative">${yAxis}${bars}</div>`;

  // Hover tooltips for bar chart
  let tt = document.getElementById('an-bar-tt');
  if (!tt) {
    tt = document.createElement('div');
    tt.id = 'an-bar-tt';
    tt.className = 'chart-tooltip';
    tt.style.zIndex = '9999';
    document.body.appendChild(tt);
  }

  container.querySelectorAll('.bar-single').forEach(bar => {
    bar.addEventListener('mouseenter', () => {
      const rect = bar.getBoundingClientRect();
      const v = parseFloat(bar.dataset.val);
      const displayVal = v <= 1 ? (v * 100).toFixed(2) + '%' : v.toFixed(4);
      tt.innerHTML = `<div class="tt-metric">${bar.dataset.metric}</div><div class="tt-val">${bar.dataset.ver}: ${displayVal}</div>`;
      tt.classList.add('show');
      
      const ttRect = tt.getBoundingClientRect();
      tt.style.left = (rect.left + rect.width / 2 - ttRect.width / 2 + window.scrollX) + 'px';
      tt.style.top = (rect.top - ttRect.height - 8 + window.scrollY) + 'px';
    });
    bar.addEventListener('mouseleave', () => tt.classList.remove('show'));
  });
}

// ── Parameter Evolution Table ──
function renderAnParamsTable(runs) {
  const container = document.getElementById('an-params-table');
  if (!container) return;

  const allParams = [...new Set(runs.flatMap(r => (r.parameters || []).map(p => p.parameter_name)))];
  if (!allParams.length) { container.innerHTML = '<div class="empty-msg">No parameters logged</div>'; return; }

  const lookup = {};
  allParams.forEach(pn => {
    lookup[pn] = {};
    runs.forEach(r => {
      const p = (r.parameters || []).find(x => x.parameter_name === pn);
      lookup[pn][r.version_name] = p ? String(p.parameter_value) : '—';
    });
  });

  let html = `<table class="diff-table"><thead><tr><th>Parameter</th>`;
  runs.forEach((r, i) => {
    html += `<th class="version-header" style="color:${VERSION_COLORS[i % VERSION_COLORS.length]};border-color:${VERSION_COLORS[i % VERSION_COLORS.length]}">${esc(r.version_name)}</th>`;
  });
  html += '</tr></thead><tbody>';
  allParams.forEach(pn => {
    const vals = runs.map(r => lookup[pn][r.version_name]);
    html += `<tr><td class="param-name">${esc(pn)}</td>`;
    runs.forEach((r, i) => {
      const changed = i > 0 && vals[i] !== vals[i - 1];
      html += `<td class="version-col${changed ? ' changed' : ''}">${esc(vals[i])}</td>`;
    });
    html += '</tr>';
  });
  html += '</tbody></table>';
  container.innerHTML = html;
}

// ── Dataset Overview Table ──
function renderAnDatasetOverview(runs) {
  const container = document.getElementById('an-dataset-overview');
  if (!container) return;

  const fields = ['dataset_name', 'dataset_version', 'train_images', 'val_images', 'classes'];
  const labels = ['Dataset', 'Version', 'Train Images', 'Val Images', 'Classes'];

  let html = `<table class="cmp-info-table"><thead><tr><th>Field</th>`;
  runs.forEach((r, i) => {
    html += `<th class="version-header" style="color:${VERSION_COLORS[i % VERSION_COLORS.length]};border-color:${VERSION_COLORS[i % VERSION_COLORS.length]}">${esc(r.version_name)}</th>`;
  });
  html += '</tr></thead><tbody>';
  fields.forEach((f, fi) => {
    html += `<tr><td class="field-name">${labels[fi]}</td>`;
    runs.forEach(r => {
      const di = (r.dataset_info || [])[0];
      let v = di ? di[f] : '—';
      if (v != null && typeof v === 'number') v = v.toLocaleString();
      html += `<td class="version-col">${esc(String(v ?? '—'))}</td>`;
    });
    html += '</tr>';
  });
  html += '</tbody></table>';
  container.innerHTML = html;
}

// ═══════════════════════════════════════════
// VERSIONS / RUNS LIST
// ═══════════════════════════════════════════
async function loadRuns(pid) {
  const box = document.getElementById('runs-list');
  box.innerHTML = '<div class="loader" style="grid-column:1/-1"><div class="spinner"></div></div>';
  try {
    const d = await api(`/projects/${pid}/runs`);
    S.runs = d.runs || [];
    if (!S.runs.length) { box.innerHTML = '<div class="empty-msg" style="grid-column:1/-1">No versions logged yet.</div>'; return; }
    box.innerHTML = S.runs.map((r, i) => runCard(r, i)).join('');
  } catch {
    box.innerHTML = '<div class="empty-msg" style="grid-column:1/-1">Failed to load versions.</div>';
    toast('Failed to load versions', 'err');
  }
}

function runCard(r, i) {
  const sc = (r.status || '').toLowerCase().replace(/\s+/g, '-');
  const ca = r.created_at ? fmtDate(new Date(r.created_at)) : 'N/A';
  const ea = r.ended_at   ? fmtDate(new Date(r.ended_at))   : '—';
  return `<div class="r-card" onclick="navigateTo('run-detail',{runId:${r.id},versionName:'${esc(r.version_name)}'})" style="animation-delay:${i * 55}ms">
    <div class="r-card-top">
      <div>
        <div class="r-version">${esc(r.version_name)}</div>
        <span class="r-id">Run #${r.id}</span>
      </div>
      <span class="r-status ${sc}">${r.status || 'Unknown'}</span>
    </div>
    <div class="r-meta">
      <div class="r-meta-item">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
        Started: ${ca}
      </div>
      <div class="r-meta-item">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
        Ended: ${ea}
      </div>
    </div>
    <div class="r-action">View Details <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="9 18 15 12 9 6"/></svg></div>
  </div>`;
}

// ═══════════════════════════════════════════
// RUN / VERSION DETAIL
// ═══════════════════════════════════════════
async function loadRunDetail(pid, rid) {
  loadSysBadges(pid, rid);
  const run = S.runs.find(r => r.id === rid);
  const el = document.getElementById('rd-status');
  if (run && el) {
    const sc = (run.status || '').toLowerCase().replace(/\s+/g, '-');
    el.textContent = run.status || 'Unknown';
    el.className = 'run-hero-status ' + sc;
  }
  loadMetrics(pid, rid);
  loadParams(pid, rid);
  loadDataset(pid, rid);
  loadArtifacts(pid, rid);
}

async function loadSysBadges(pid, rid) {
  const box = document.getElementById('sys-badges'); box.innerHTML = '';
  try {
    const d = await api(`/projects/${pid}/runs/${rid}/system_info`);
    const arr = d.system_info || [];
    if (!arr.length) { box.innerHTML = '<span style="font-size:.78rem;color:var(--muted)">No system info</span>'; return; }
    const si = arr[0];
    box.innerHTML = `
      <div class="sys-badge"><div class="sys-badge-icon os"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg></div><div class="sys-badge-text"><span class="sys-badge-label">OS</span><span class="sys-badge-val">${esc(si.os || 'N/A')}</span></div></div>
      <div class="sys-badge"><div class="sys-badge-icon py"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg></div><div class="sys-badge-text"><span class="sys-badge-label">Python</span><span class="sys-badge-val">${esc(si.python_version || 'N/A')}</span></div></div>
      <div class="sys-badge"><div class="sys-badge-icon gpu"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="4" y="4" width="16" height="16" rx="2"/><rect x="9" y="9" width="6" height="6"/></svg></div><div class="sys-badge-text"><span class="sys-badge-label">GPU</span><span class="sys-badge-val">${esc(si.gpu || 'None')}</span></div></div>`;
  } catch { box.innerHTML = '<span style="font-size:.78rem;color:var(--muted)">Unavailable</span>'; }
}

async function loadMetrics(pid, rid) {
  const b = document.getElementById('body-metrics'); b.innerHTML = '<div class="loader"><div class="spinner"></div></div>';
  try {
    const d = await api(`/projects/${pid}/runs/${rid}/metrics`); const m = d.metrics || [];
    if (!m.length) { b.innerHTML = '<div class="empty-msg">No metrics logged</div>'; return; }
    const mx = Math.max(...m.map(x => Math.abs(parseFloat(x.metric_value) || 0)), 1);
    b.innerHTML = `<table class="dtable"><thead><tr><th>Metric</th><th>Value</th><th>Relative Magnitude</th></tr></thead><tbody>${m.map(x => {
      const v    = parseFloat(x.metric_value) || 0;
      const pct  = Math.min((Math.abs(v) / mx) * 100, 100);
      const display = v <= 1 ? (v * 100).toFixed(2) + '%' : v.toFixed(4);
      return `<tr>
        <td class="name">${esc(x.metric_name)}</td>
        <td class="val">${display}</td>
        <td>
          <div class="m-bar-wrap">
            <div class="m-track"><div class="m-fill" style="width:${pct}%"></div></div>
            <span class="m-pct">${pct.toFixed(0)}%</span>
          </div>
        </td>
      </tr>`;
    }).join('')}</tbody></table>`;
  } catch { b.innerHTML = '<div class="empty-msg">Failed to load metrics</div>'; }
}

async function loadParams(pid, rid) {
  const b = document.getElementById('body-params'); b.innerHTML = '<div class="loader"><div class="spinner"></div></div>';
  try {
    const d = await api(`/projects/${pid}/runs/${rid}/parameters`); const p = d.parameters || [];
    if (!p.length) { b.innerHTML = '<div class="empty-msg">No parameters logged</div>'; return; }
    b.innerHTML = `<table class="dtable"><thead><tr><th>Parameter</th><th>Value</th></tr></thead><tbody>${p.map(x => `<tr><td class="name">${esc(x.parameter_name)}</td><td class="val">${esc(String(x.parameter_value))}</td></tr>`).join('')}</tbody></table>`;
  } catch { b.innerHTML = '<div class="empty-msg">Failed to load parameters</div>'; }
}

async function loadDataset(pid, rid) {
  const b = document.getElementById('body-dataset'); b.innerHTML = '<div class="loader"><div class="spinner"></div></div>';
  try {
    const d = await api(`/projects/${pid}/runs/${rid}/dataset_info`); const a = d.dataset_info || [];
    if (!a.length) { b.innerHTML = '<div class="empty-msg">No dataset info</div>'; return; }
    const ds = a[0];
    b.innerHTML = `<div class="info-chips">
      <div class="info-chip"><div class="chip-label">Dataset</div><div class="chip-val">${esc(ds.dataset_name || 'N/A')}</div></div>
      <div class="info-chip"><div class="chip-label">Version</div><div class="chip-val mono">${esc(ds.dataset_version || 'N/A')}</div></div>
      <div class="info-chip"><div class="chip-label">Train Images</div><div class="chip-val">${ds.train_images != null ? ds.train_images.toLocaleString() : 'N/A'}</div></div>
      <div class="info-chip"><div class="chip-label">Val Images</div><div class="chip-val">${ds.val_images != null ? ds.val_images.toLocaleString() : 'N/A'}</div></div>
      <div class="info-chip"><div class="chip-label">Classes</div><div class="chip-val">${ds.classes != null ? ds.classes : 'N/A'}</div></div>
    </div>`;
  } catch { b.innerHTML = '<div class="empty-msg">Failed to load dataset info</div>'; }
}

async function loadArtifacts(pid, rid) {
  const b = document.getElementById('body-artifacts'); b.innerHTML = '<div class="loader"><div class="spinner"></div></div>';
  try {
    const d = await api(`/projects/${pid}/runs/${rid}/artifacts`); const a = d.artifacts || [];
    if (!a.length) { b.innerHTML = '<div class="empty-msg">No artifacts saved</div>'; return; }
    b.innerHTML = `<table class="dtable"><thead><tr><th>Artifact Path</th><th>Type</th></tr></thead><tbody>${a.map(x => `<tr><td class="val">${esc(x.artifact_path)}</td><td class="name">${esc(x.artifact_type)}</td></tr>`).join('')}</tbody></table>`;
  } catch { b.innerHTML = '<div class="empty-msg">Failed to load artifacts</div>'; }
}

// ═══════════════════════════════════════════
// UTILITIES
// ═══════════════════════════════════════════
function capitalize(s) { return s ? s.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase()) : ''; }
function esc(t) { const d = document.createElement('div'); d.textContent = t || ''; return d.innerHTML; }
function fmtDate(d) {
  if (!d || isNaN(d)) return 'N/A';
  return d.toLocaleString('en-US', { month: 'short', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit' });
}
function relTime(d) {
  if (!d || isNaN(d)) return 'Unknown';
  const diff = Date.now() - d;
  const m = Math.floor(diff / 60000), h = Math.floor(diff / 3600000), dy = Math.floor(diff / 86400000);
  if (m < 1) return 'Just now';
  if (m < 60) return `${m}m ago`;
  if (h < 24) return `${h}h ago`;
  if (dy < 7) return `${dy}d ago`;
  return fmtDate(d);
}

function toast(msg, type = 'inf') {
  const box = document.getElementById('toast-box'); if (!box) return;
  const t = document.createElement('div'); t.className = `toast ${type}`;
  const icons = { ok: '✓', err: '✕', inf: 'i' };
  t.innerHTML = `<span class="toast-icon">${icons[type] || 'i'}</span><span>${esc(msg)}</span>`;
  box.appendChild(t);
  setTimeout(() => {
    t.style.opacity = '0'; t.style.transform = 'translateX(12px)'; t.style.transition = 'all .3s';
    setTimeout(() => t.remove(), 320);
  }, 4200);
}

function mkToastBox() {
  if (document.getElementById('toast-box')) return;
  const b = document.createElement('div'); b.id = 'toast-box'; b.className = 'toast-box';
  document.body.appendChild(b);
}
