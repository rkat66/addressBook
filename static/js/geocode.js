// ── Street address autocomplete ───────────────────────────────────────────────

(function () {
  let debounceTimer = null;
  let activeIndex   = -1;
  let suggestions   = [];

  function init() {
    const street = document.getElementById('street');
    if (!street) return;

    // Wrap the input so we can position the dropdown relative to it
    const wrapper = street.parentElement;
    wrapper.style.position = 'relative';

    const dropdown = document.createElement('ul');
    dropdown.id = 'street-suggestions';
    dropdown.className = 'list-group shadow';
    dropdown.style.cssText =
      'position:absolute; top:100%; left:0; right:0; z-index:1055; ' +
      'max-height:260px; overflow-y:auto; display:none;';
    wrapper.appendChild(dropdown);

    street.setAttribute('autocomplete', 'off');

    street.addEventListener('input', () => {
      clearTimeout(debounceTimer);
      const q = street.value.trim();
      if (q.length < 3) { hideDrop(); return; }
      debounceTimer = setTimeout(() => fetchSuggestions(q, dropdown, street), 400);
    });

    street.addEventListener('keydown', e => {
      if (dropdown.style.display === 'none') return;
      if (e.key === 'ArrowDown') { e.preventDefault(); moveFocus(1, dropdown); }
      else if (e.key === 'ArrowUp') { e.preventDefault(); moveFocus(-1, dropdown); }
      else if (e.key === 'Enter' && activeIndex >= 0) {
        e.preventDefault();
        selectSuggestion(suggestions[activeIndex], street);
        hideDrop();
      } else if (e.key === 'Escape') { hideDrop(); }
    });

    document.addEventListener('click', e => {
      if (!wrapper.contains(e.target)) hideDrop();
    });
  }

  function fetchSuggestions(q, dropdown, street) {
    fetch('/api/suggest?q=' + encodeURIComponent(q))
      .then(r => r.json())
      .then(data => {
        suggestions  = Array.isArray(data) ? data : [];
        activeIndex  = -1;
        dropdown.innerHTML = '';

        if (suggestions.length === 0) { hideDrop(); return; }

        suggestions.forEach((s, i) => {
          const li = document.createElement('li');
          li.className = 'list-group-item list-group-item-action py-2 px-3';
          li.style.cursor = 'pointer';
          li.innerHTML =
            `<div class="fw-semibold text-truncate" style="max-width:100%">${esc(s.display_name)}</div>`;
          li.addEventListener('mouseenter', () => setActive(i, dropdown));
          li.addEventListener('click', () => {
            selectSuggestion(s, street);
            hideDrop();
          });
          dropdown.appendChild(li);
        });

        dropdown.style.display = '';
      })
      .catch(() => hideDrop());
  }

  function selectSuggestion(s, streetInput) {
    setField('street',      s.street      || streetInput.value);
    setField('city',        s.city);
    setField('state',       s.state);
    setField('postal_code', s.postal_code);
    setField('country',     s.country);
    setField('latitude',    s.lat  != null ? String(s.lat) : '');
    setField('longitude',   s.lon  != null ? String(s.lon) : '');
    showGeocodeStatus('success',
      'Address filled — ' + s.lat.toFixed(5) + ', ' + s.lon.toFixed(5));
  }

  function setField(id, value) {
    const el = document.getElementById(id);
    if (el) el.value = value || '';
  }

  function moveFocus(dir, dropdown) {
    const items = dropdown.querySelectorAll('li');
    activeIndex = Math.max(0, Math.min(items.length - 1, activeIndex + dir));
    setActive(activeIndex, dropdown);
  }

  function setActive(i, dropdown) {
    activeIndex = i;
    dropdown.querySelectorAll('li').forEach((li, idx) => {
      li.classList.toggle('active', idx === i);
    });
  }

  function hideDrop() {
    const d = document.getElementById('street-suggestions');
    if (d) d.style.display = 'none';
    activeIndex = -1;
  }

  document.addEventListener('DOMContentLoaded', init);
})();


// ── Manual "Geocode Address" button ──────────────────────────────────────────

function geocodeAddress() {
  const fields = ['street', 'city', 'state', 'postal_code', 'country'];
  const q = fields
    .map(id => { const el = document.getElementById(id); return el ? el.value.trim() : ''; })
    .filter(Boolean)
    .join(', ');

  if (!q) {
    showGeocodeStatus('warning', 'Enter at least one address field before geocoding.');
    return;
  }

  showGeocodeStatus('info', 'Looking up coordinates…');

  fetch('/api/geocode?q=' + encodeURIComponent(q))
    .then(r => r.json().then(data => ({ ok: r.ok, data })))
    .then(({ ok, data }) => {
      if (ok && data.lat != null) {
        if (data.street)      setField('street',      data.street);
        if (data.city)        setField('city',        data.city);
        if (data.state)       setField('state',       data.state);
        if (data.postal_code) setField('postal_code', data.postal_code);
        if (data.country)     setField('country',     data.country);
        setField('latitude',  String(data.lat));
        setField('longitude', String(data.lon));
        showGeocodeStatus('success', 'Found: ' + data.lat.toFixed(5) + ', ' + data.lon.toFixed(5));
      } else {
        showGeocodeStatus('danger', data.error || 'Address not found. Try a broader query.');
      }
    })
    .catch(() => {
      showGeocodeStatus('danger', 'Geocoding service unavailable. Try again later.');
    });
}

function setField(id, value) {
  const el = document.getElementById(id);
  if (el) el.value = value || '';
}

function showGeocodeStatus(type, msg) {
  const el = document.getElementById('geocode-status');
  if (!el) return;
  el.className = 'alert alert-' + type + ' py-2';
  el.textContent = msg;
  el.classList.remove('d-none');
}

function esc(str) {
  if (!str) return '';
  return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
            .replace(/"/g,'&quot;').replace(/'/g,'&#39;');
}
