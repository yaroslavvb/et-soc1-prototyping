/* New user? Start here. D is brief.json (docs/lab-start/make_page_data.py): D.md is START.md word for word (the brief
   the Claude on the lab machine reads). Since 8 October 2026 the page is the raw steps only, with no machine diagram.
   The username and machine fields fill the commands of steps 1 and 2, step 4's claim line, the line to come back and
   the no-Claude login; nothing is stored or sent anywhere. */
(function () {
  const q = sel => document.querySelector(sel);
  const esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

  /* ---- the commands. \u0001 marks the username and \u0002 the machine, so that they can be highlighted. The root
     block validates the name again on the machine, refuses nothing silently, and gives no sudo. */
  const RAW = 'https://raw.githubusercontent.com/yaroslavvb/et-soc1-prototyping/main/docs/lab-start/START.md';
  const L = '\u0001', H = '\u0002';
  const TPL = {
    root: [
      `ssh -o StrictHostKeyChecking=accept-new root@${H} 'bash -s' <<'EOF'`,
      `u=${L}`,
      `if ! [[ $u =~ ^[a-z][a-z0-9_-]{0,31}$ ]]; then echo "bad username: lowercase letters, digits, - and _"; exit 1; fi`,
      `if id "$u" >/dev/null 2>&1; then echo "$u already exists on $(hostname): go on if it is yours, else choose another username"; exit 0; fi`,
      `adduser --quiet --disabled-password --comment "" --shell /bin/bash "$u" </dev/null || { echo "adduser failed: no account made"; exit 1; }`,
      `loginctl enable-linger "$u"`,
      `echo "created $u on $(hostname): now step 2"`,
      `EOF`].join('\n'),
    user: [
      `ssh -o StrictHostKeyChecking=accept-new ${L}@${H} 'bash -s' <<'EOF'`,
      `[ -x ~/.local/bin/claude ] || curl -fsSL https://claude.ai/install.sh | bash`,
      `grep -qs '\\.local/bin' ~/.bashrc || echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc`,
      `curl -fsSL ${RAW} -o ~/lab-start.md`,
      `tmux has-session -t =claude 2>/dev/null || { tmux new-session -d -s claude -c ~ && tmux send-keys -t claude '~/.local/bin/claude' Enter; }`,
      `EOF`,
      `ssh -t ${L}@${H} tmux attach -t claude`].join('\n'),
    prompt: 'Read ~/lab-start.md and follow it.',
    attach: `ssh -t ${L}@${H} tmux attach -t claude`,
    login: `ssh ${L}@${H}`,
    host: H,
  };
  const NEEDS_LOGIN = {root: true, user: true, prompt: false, attach: true, login: true, host: false};

  const inp = q('#f-login'), sel = q('#f-host'), hint = q('[data-role=hint]');
  const LOGIN = /^[a-z][a-z0-9_-]{0,31}$/;
  const SYSTEM = /^(root|toor|daemon|bin|sys|sync|games|man|lp|mail|news|uucp|proxy|www-data|backup|list|irc|nobody|sshd|syslog|messagebus|admin|sudo|adm|users|staff|systemd-.*)$/;
  const HINT = hint.textContent;
  let login = null;
  const text = (k, l, h) => TPL[k].split(L).join(l).split(H).join(h);
  function render() {
    const v = inp.value.trim(), sys = SYSTEM.test(v), ok = !v || (LOGIN.test(v) && !sys);
    login = v && ok ? v : null;
    inp.setAttribute('aria-invalid', ok ? 'false' : 'true');
    hint.classList.toggle('bad', !ok);
    hint.textContent = ok ? HINT : sys ? 'Choose your own username, not a system name such as root.'
      : 'Lowercase letters, digits, - and _ only, starting with a letter, up to 32 characters.';
    const h = sel.value;
    document.querySelectorAll('[data-tpl]').forEach(el => {
      const k = el.dataset.tpl;
      el.innerHTML = esc(TPL[k]).split(L).join(login ? `<span class="fill">${esc(login)}</span>` : '<span class="ph">&lt;username&gt;</span>')
        .split(H).join(`<span class="fill">${esc(h)}</span>`);
    });
  }
  inp.addEventListener('input', render);
  sel.addEventListener('change', render);
  render();

  /* ---- copy. Clipboard first; inside a frame that forbids it, a selected textarea and execCommand; failing both,
     the block's text is selected for Ctrl-C. A command that needs the username is not copied without one. */
  const stat = q('[data-role=stat]');
  function say(msg, good) {
    stat.textContent = msg; stat.style.color = good ? 'var(--ok)' : 'var(--ink)';
    clearTimeout(say.t); say.t = setTimeout(() => { stat.textContent = ''; }, 5000);
  }
  function copyText(t, el, what) {
    const done = ok => {
      if (ok) say(`Copied ${what}.`, true);
      else { say('Selected: press Ctrl-C (⌘C) to copy.', false); el.focus(); const r = document.createRange(); r.selectNodeContents(el); const s = getSelection(); s.removeAllRanges(); s.addRange(r); }
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
  document.querySelectorAll('[data-copy]').forEach(b => b.addEventListener('click', () => {
    const k = b.dataset.copy, el = q(`[data-tpl="${k}"]`);
    if (NEEDS_LOGIN[k] && !login) { say('Type your username first (above).', false); inp.focus(); return; }
    copyText(text(k, login || '', sel.value), el, k === 'prompt' ? 'the line for Claude' : 'the commands for your terminal');
  }));

  /* ---- the brief, as Claude reads it */
  q('[data-role=raw]').textContent = D.md;
  q('[data-role=meta]').textContent = `${CK.fmt.num(D.words, 0)} words · version of ${D.version}`;
})();
