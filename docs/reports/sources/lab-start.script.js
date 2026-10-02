/* New user? Start now. D is brief.json (docs/lab-start/make_page_data.py): D.md is START.md word for word, D.cards the
   card tiles. The one field fills the prompt's <login> (D.fills); <host> and <N> stay, for the agent's own choice.
   Nothing is stored or sent anywhere. */
(function () {
  const q = sel => document.querySelector(sel);
  const esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

  /* ---- the lab diagram: three machines, four cards, from the data */
  const lab = q('#lab');
  ['aifoundry1', 'aifoundry2', 'aifoundry3'].forEach(h => {
    const m = document.createElement('div');
    m.className = 'm';
    const cards = D.cards.filter(c => c.host === h).sort((a, b) => a.n - b.n);
    m.innerHTML = `<div class="h">${esc(h)}</div><div class="os">${cards.length === 1 ? 'one card' : cards.length + ' cards'}</div>`
      + cards.map(c => {
          const k = CK.card(c.id);
          return `<div class="cbox${c.use ? '' : ' off'}" style="--c:${k.color}"><div class="n">card ${c.n}</div>`
            + `<div class="d">firmware ${esc(c.firmware)} · ${esc(c.clock)}</div><div class="d">${esc(c.note)}</div></div>`;
        }).join('');
    lab.appendChild(m);
  });

  /* ---- the one field: a username fills <login>; anything else leaves the placeholder, and says why */
  const inp = q('#f-login'), hint = q('[data-role=hint]'), raw = q('[data-role=raw]'), meta = q('[data-role=meta]');
  /* Ubuntu's default for new accounts: lowercase letters, digits, - and _, starting with a letter (the same rule as START.md's account block). System accounts such as root are
     refused: the prompt would send the agent in as them. */
  const LOGIN = /^[a-z][a-z0-9_-]{0,31}$/;
  const SYSTEM = /^(root|toor|daemon|bin|sys|sync|games|man|lp|mail|news|uucp|proxy|www-data|backup|list|irc|nobody|sshd|syslog|messagebus|systemd-.*)$/;
  const HINT = hint.textContent;
  const PH = /<(login)>/g;
  let text = D.md, ok = true;
  function update() {
    const l = inp.value.trim(), sys = SYSTEM.test(l);
    ok = !l || (LOGIN.test(l) && !sys);
    const login = l && ok ? l : null;
    inp.setAttribute('aria-invalid', ok ? 'false' : 'true');
    hint.classList.toggle('bad', !ok);
    hint.textContent = ok ? HINT
      : sys ? 'Use your own username, not a system account such as root: the prompt keeps <login> for now.'
      : 'Lowercase letters, digits, "_" and "-" only, starting with a letter, up to 32: the prompt keeps <login> for now.';
    text = login ? D.md.replace(PH, () => login) : D.md;
    raw.innerHTML = esc(D.md).replace(/&lt;login&gt;/g,
      () => login ? `<span class="fill">${esc(login)}</span>` : '<span class="ph">&lt;login&gt;</span>');
    const n = (D.md.match(PH) || []).length;
    meta.textContent = `${CK.fmt.num(D.words, 0)} words · version of ${D.version} · `
      + (login ? `your username filled in ${n} places` : 'your username goes where <login> is highlighted')
      + ' · scroll to read it';
  }
  inp.addEventListener('input', update);
  update();

  /* ---- copy. Clipboard first; inside a frame that forbids it, a selected textarea and execCommand; failing both,
     the prompt's text is selected for Ctrl-C. */
  const stat = q('[data-role=stat]');
  function copyText(t, filled) {
    const done = ok => {
      stat.textContent = !ok ? 'Selected: press Ctrl-C (⌘C) to copy'
        : filled ? 'Copied: paste it into your agent' : 'Copied, without your username (see above)';
      stat.style.color = ok && filled ? 'var(--ok)' : 'var(--ink)';
      if (!ok) { raw.focus(); const r = document.createRange(); r.selectNodeContents(raw); const s = getSelection(); s.removeAllRanges(); s.addRange(r); }
      clearTimeout(copyText.t); copyText.t = setTimeout(() => { stat.textContent = ''; }, 5000);
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
  q('[data-role=copy]').addEventListener('click', () => copyText(text, ok));
})();
