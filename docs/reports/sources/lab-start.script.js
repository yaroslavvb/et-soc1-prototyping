/* New user? Start now. D is brief.json (docs/lab-start/make_page_data.py): D.md is START.md word for word, D.cards the
   card tiles. The copy box shows D.md with the viewer's login and card filled in; the rendered view below it is the
   same text through a small markdown renderer that knows only what START.md uses (headings, paragraphs, flat lists,
   pipe tables, fenced code, inline code, bold, links). Nothing is stored or sent anywhere. */
(function () {
  const q = sel => document.querySelector(sel);
  const esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  const slug = t => t.toLowerCase().replace(/<[^>]+>/g, '').replace(/&[a-z]+;/g, '').replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '').slice(0, 50);

  /* ---- the card tiles, from the data */
  const tiles = q('#cards4');
  D.cards.forEach(c => {
    const k = CK.card(c.id), d = document.createElement('div');
    d.className = 'card' + (c.use ? '' : ' off');
    d.style.setProperty('--c', k.color);
    d.innerHTML = `<div class="nm">${esc(k.label)}<span class="tag ${c.use ? 'yes' : 'no'}">${c.use ? 'usable' : 'off limits'}</span></div>`
      + `<div class="fw">firmware ${esc(c.firmware)}` + (c.use ? ` · lock <code>etsoc-shire${c.n}.lock</code>` : '') + '</div>'
      + `<div class="ck">${esc(c.clock)}</div><div class="nt">${esc(c.note)}</div>`;
    tiles.appendChild(d);
  });

  /* ---- the setup fields: login and card fill the brief's <login>, <host> and <N> */
  const sel = q('#f-card'), inp = q('#f-login'), hint = q('[data-role=hint]');
  const opt = (v, t, dis) => { const o = document.createElement('option'); o.value = v; o.textContent = t; o.disabled = !!dis; sel.appendChild(o); };
  opt('', 'not chosen yet');
  D.cards.forEach(c => opt(c.use ? c.host + '|' + c.n : '', CK.card(c.id).label + (c.use ? '' : ' (not used)'), !c.use));
  const LOGIN = /^[a-z_][a-z0-9_-]{0,31}$/;
  const S1 = '\u0001', S2 = '\u0002';                    // around a filled value, marked after rendering
  function values() {
    const v = {}, l = inp.value.trim();
    if (l && LOGIN.test(l)) v.login = l;
    if (sel.value) { const [h, n] = sel.value.split('|'); v.host = h; v.N = n; }
    hint.textContent = l && !LOGIN.test(l)
      ? 'A login is lower-case letters, digits, "-" and "_"; this one is left out.'
      : 'Optional. Anything left blank stays in angle brackets, and the agent asks you.';
    return v;
  }
  const fill = (md, v, mark) => md.replace(/<(login|host|N)>/g, (m, k) => v[k] == null ? m : (mark ? S1 + v[k] + S2 : v[k]));

  /* ---- a small markdown renderer for START.md */
  function inline(s) {
    const code = [];
    s = s.replace(/`([^`]+)`/g, (m, c) => { code.push(c); return '\u0000' + (code.length - 1) + '\u0000'; });
    s = esc(s)
      .replace(/\*\*(.+?)\*\*/g, '<b>$1</b>')
      .replace(/\[([^\]]+)\]\((https?:\/\/[^)\s]+)\)/g, '<a href="$2">$1</a>')
      .replace(/(^|[\s(])(https?:\/\/[^\s<)"]*[^\s<)".,;:])/g, '$1<a href="$2">$2</a>');
    return s.replace(/\u0000(\d+)\u0000/g, (m, i) => '<code>' + esc(code[+i]) + '</code>');
  }
  function cells(row) {                                   // split a pipe row, ignoring pipes inside code spans
    const out = []; let cur = '', inCode = false;
    const r = row.trim().replace(/^\|/, '').replace(/\|$/, '');
    for (const ch of r) {
      if (ch === '`') inCode = !inCode;
      if (ch === '|' && !inCode) { out.push(cur.trim()); cur = ''; } else cur += ch;
    }
    out.push(cur.trim());
    return out;
  }
  const ITEM = /^(?:[-*]|(\d+)\.)\s+(.*)$/;
  const BLOCK = /^(```|#{1,6}\s|\||[-*]\s|\d+\.\s)/;
  function render(md) {
    const L = md.split('\n'), out = [], heads = [];
    let i = 0;
    while (i < L.length) {
      const l = L[i];
      if (!l.trim()) { i++; continue; }
      if (l.startsWith('```')) {
        const buf = []; i++;
        while (i < L.length && !L[i].startsWith('```')) buf.push(L[i++]);
        i++;
        out.push('<pre><code>' + esc(buf.join('\n')) + '</code></pre>');
        continue;
      }
      let m = l.match(/^(#{1,4})\s+(.*)$/);
      if (m) {
        i++;
        if (m[1].length === 1) continue;                  // the title: the page has its own
        const tag = m[1].length === 2 ? 'h3' : 'h4', id = 'brief-' + slug(m[2]);
        if (tag === 'h3') heads.push([id, inline(m[2])]);
        out.push(`<${tag} id="${id}">${inline(m[2])}</${tag}>`);
        continue;
      }
      if (l.startsWith('|')) {
        const rows = [];
        while (i < L.length && L[i].startsWith('|')) rows.push(L[i++]);
        const hd = cells(rows[0]), body = rows.slice(2).map(cells);
        out.push('<div class="table-wrap"><table class="stack"><thead><tr>' + hd.map(h => '<th>' + inline(h) + '</th>').join('')
          + '</tr></thead><tbody>' + body.map(r => '<tr>' + r.map((c, j) =>
            `<td data-label="${esc(hd[j] || '')}">${inline(c)}</td>`).join('') + '</tr>').join('') + '</tbody></table></div>');
        continue;
      }
      m = l.match(ITEM);
      if (m) {
        const ordered = m[1] != null, start = ordered ? +m[1] : 1, items = [];
        while (i < L.length) {
          const x = L[i], mm = x.match(ITEM);
          if (mm && (mm[1] != null) === ordered) { items.push(mm[2]); i++; continue; }
          if (x.trim() && /^\s{2,}\S/.test(x) && items.length) { items[items.length - 1] += ' ' + x.trim(); i++; continue; }
          break;
        }
        const tag = ordered ? 'ol' : 'ul';
        out.push(`<${tag}${ordered && start !== 1 ? ` start="${start}"` : ''}>` + items.map(t => '<li>' + inline(t) + '</li>').join('') + `</${tag}>`);
        continue;
      }
      const buf = [l.trim()]; i++;
      while (i < L.length && L[i].trim() && !BLOCK.test(L[i])) buf.push(L[i++].trim());
      out.push('<p>' + inline(buf.join(' ')) + '</p>');
    }
    const nav = '<nav class="bnav card"><b>In the brief</b><ol>' + heads.map(([id, t]) => `<li><a href="#${id}">${t}</a></li>`).join('') + '</ol></nav>';
    return nav + out.join('\n');
  }

  /* ---- fill the copy box and the rendered view */
  const raw = q('[data-role=raw]'), view = q('#brief-view'), meta = q('[data-role=meta]');
  let text = D.md;
  function update() {
    const v = values();
    text = fill(D.md, v, false);
    raw.textContent = text;
    const html = render(fill(D.md, v, true))
      .replace(/\u0001([^\u0002]*)\u0002/g, '<span class="fill">$1</span>')
      .replace(/&lt;(login|host|N)&gt;/g, '<span class="ph">&lt;$1&gt;</span>');
    view.innerHTML = html;
    view.querySelectorAll('h3[id]').forEach(h => {         // the same "#" links the template gives other headings
      const a = document.createElement('a'); a.href = '#' + h.id; a.className = 'hlink'; a.textContent = '#';
      a.title = 'link to this section'; h.appendChild(a);
    });
    view.querySelectorAll('code').forEach(c => {           // repository paths as links, as the template does once
      const t = c.textContent.trim();
      if (c.closest('pre, a') || !/^(docs|workloads|tools|scripts|kernels|rtl-sim)\/[\w./-]+$/.test(t)) return;
      const a = document.createElement('a'); a.href = 'https://github.com/yaroslavvb/et-soc1-prototyping/tree/main/' + t;
      c.parentNode.insertBefore(a, c); a.appendChild(c);
    });
    const left = (text.match(/<(login|host|N)>/g) || []).length;
    meta.innerHTML = `<b>START.md</b> · ${CK.fmt.num(D.words, 0)} words · version of 30 September 2026`
      + (left ? ` · ${left} placeholder${left === 1 ? '' : 's'} left for the agent to ask about` : ' · filled in');
  }
  inp.addEventListener('input', update);
  sel.addEventListener('change', update);
  update();

  /* ---- copy and download. Clipboard first; inside a frame that forbids it, a selected textarea and execCommand. */
  function copyText(t, stat, btn) {
    const done = ok => {
      stat.textContent = ok ? 'Copied' : 'Select the text and copy it';
      stat.style.color = ok ? 'var(--ok)' : 'var(--warn)';
      if (!ok && btn === 'raw') { const r = document.createRange(); r.selectNodeContents(raw); const s = getSelection(); s.removeAllRanges(); s.addRange(r); }
      clearTimeout(copyText.t); copyText.t = setTimeout(() => { stat.innerHTML = '&nbsp;'; }, 4000);
    };
    const fallback = () => {
      try {
        const ta = document.createElement('textarea'); ta.value = t; ta.setAttribute('readonly', '');
        ta.style.position = 'fixed'; ta.style.opacity = '0'; ta.style.top = '0'; document.body.appendChild(ta);
        ta.select(); const ok = document.execCommand('copy'); ta.remove(); done(ok);
      } catch (_) { done(false); }
    };
    try {
      if (navigator.clipboard && window.isSecureContext) navigator.clipboard.writeText(t).then(() => done(true), fallback);
      else fallback();
    } catch (_) { fallback(); }
  }
  const stat = q('[data-role=stat]');
  q('[data-role=copy]').addEventListener('click', () => copyText(text, stat, 'raw'));
  q('[data-role=copyalt]').addEventListener('click', () => copyText(q('[data-role=alttext]').textContent.trim(), stat, 'alt'));
  q('[data-role=download]').addEventListener('click', () => {
    try {
      const url = URL.createObjectURL(new Blob([text], {type: 'text/markdown'}));
      const a = document.createElement('a'); a.href = url; a.download = 'START.md'; document.body.appendChild(a); a.click(); a.remove();
      setTimeout(() => URL.revokeObjectURL(url), 2000);
    } catch (_) { stat.textContent = 'Download blocked: copy instead'; stat.style.color = 'var(--warn)'; }
  });
})();
