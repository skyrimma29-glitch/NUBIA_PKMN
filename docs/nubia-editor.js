/* =====================================================================
   EDITOR DE TEXTOS DE NUBIA
   Reescribe cualquier texto del códice, el atlas, los planos y las tablas
   de encuentro. Lo que cambies es tuyo: los demás siguen viendo el texto
   original.

   Con cuenta iniciada se guarda en Supabase y te sigue en cualquier
   dispositivo. Sin cuenta se guarda en este navegador, para que puedas
   trabajar igual mientras tanto.
   ===================================================================== */
(function(){
  const CFG = window.NUBIA || {};
  const LLAVE = 'nubia-textos';
  let sb = null, cuenta = null, editando = false, enNube = false;
  const overrides = new Map();     // clave -> texto propio
  const marcados  = new Map();     // clave -> {nodo, original}

  /* ---------------- estilos ---------------- */
  const css = document.createElement('style');
  css.textContent = `
    #nbBar{position:fixed;right:16px;bottom:16px;z-index:300;display:flex;gap:8px;
      align-items:flex-end;flex-direction:column}
    #nbBar .fila{display:flex;gap:8px;align-items:center}
    #nbBar button{font-family:'Silkscreen',monospace;font-size:10px;padding:11px 13px;
      border:3px solid #12283f;background:#fdf6e6;color:#12283f;cursor:pointer;
      box-shadow:4px 4px 0 rgba(0,0,0,.28)}
    #nbBar button:hover{background:#fff}
    #nbBar button:active{transform:translate(2px,2px);box-shadow:2px 2px 0 rgba(0,0,0,.28)}
    #nbBar button.on{background:#c6386b;color:#fff}
    #nbEstado{font-family:'Alegreya Sans',sans-serif;font-size:11px;background:#12283f;
      color:#cfe0e6;padding:7px 10px;max-width:280px;line-height:1.35}
    body.nb-edit [data-nbedit]{outline:2px dashed #c6386b;outline-offset:3px;cursor:text}
    body.nb-edit [data-nbedit]:hover{background:#fff1f5}
    body.nb-edit [data-nbedit]:focus{outline:3px solid #c6386b;background:#fff}
    [data-nbedit].nb-mio{box-shadow:inset 4px 0 0 #e0951c;background:#fffaee}
    #nbToast{position:fixed;left:50%;bottom:22px;transform:translateX(-50%) translateY(18px);
      z-index:310;background:#2e7d4f;color:#fff;font-family:'Silkscreen',monospace;font-size:10px;
      padding:11px 16px;border:3px solid #12283f;opacity:0;pointer-events:none;
      transition:opacity .2s,transform .2s}
    #nbToast.ver{opacity:1;transform:translateX(-50%)}
    @media (prefers-reduced-motion:reduce){#nbToast{transition:none}}`;
  (document.head || document.documentElement).appendChild(css);

  /* ---------------- barra ---------------- */
  const barra = document.createElement('div');
  barra.id = 'nbBar';
  barra.innerHTML = `<div id="nbEstado">Cargando…</div>
    <div class="fila">
      <button id="nbRestaurar" style="display:none">RESTAURAR</button>
      <button id="nbEditar">EDITAR TEXTOS</button>
    </div>`;
  const toast = document.createElement('div');
  toast.id = 'nbToast';

  function montar(){
    if(document.body && !document.getElementById('nbBar')){
      document.body.appendChild(barra);
      document.body.appendChild(toast);
      estado();
    }
  }
  if(document.body) montar(); else addEventListener('DOMContentLoaded', montar);

  let tT = null;
  function avisar(txt){
    toast.textContent = txt; toast.classList.add('ver');
    clearTimeout(tT); tT = setTimeout(()=>toast.classList.remove('ver'), 2200);
  }
  function estado(){
    const n = document.getElementById('nbEstado'); if(!n) return;
    const propios = [...marcados.keys()].filter(k=>overrides.has(k)).length;
    n.textContent = (enNube
      ? 'Tus textos se guardan en tu cuenta.'
      : 'Sin cuenta: tus textos se guardan solo en este navegador.')
      + (propios ? ' ' + propios + ' cambiados aquí.' : '');
    const r = document.getElementById('nbRestaurar');
    if(r){ r.style.display = propios ? '' : 'none'; r.textContent = 'RESTAURAR ' + propios; }
  }

  /* ---------------- almacenamiento ---------------- */
  function local(){
    try{ return JSON.parse(localStorage.getItem(LLAVE) || '{}'); }catch{ return {}; }
  }
  function guardarLocal(){
    try{ localStorage.setItem(LLAVE, JSON.stringify(Object.fromEntries(overrides))); }catch{}
  }
  async function cargar(){
    Object.entries(local()).forEach(([k,v])=>overrides.set(k,v));
    if(sb && cuenta){
      try{
        const { data, error } = await sb.from('textos').select('clave,valor').eq('jugador', cuenta.id);
        if(!error){
          enNube = true;
          (data||[]).forEach(r=>overrides.set(r.clave, r.valor));
        }
      }catch{}
    }
    marcados.forEach((_,k)=>aplicar(k));
    estado();
  }
  async function guardar(clave, valor){
    overrides.set(clave, valor);
    guardarLocal();
    if(enNube){
      try{
        const { error } = await sb.from('textos')
          .upsert({ jugador: cuenta.id, clave, valor }, { onConflict:'jugador,clave' });
        if(error) return 'Guardado solo en este navegador';
      }catch{ return 'Guardado solo en este navegador'; }
      return 'Guardado en tu cuenta';
    }
    return 'Guardado en este navegador';
  }
  async function quitar(clave){
    overrides.delete(clave);
    guardarLocal();
    if(enNube){
      try{ await sb.from('textos').delete().eq('jugador', cuenta.id).eq('clave', clave); }catch{}
    }
  }

  async function iniciar(){
    if(CFG.SUPABASE_URL && CFG.SUPABASE_KEY && window.supabase){
      try{
        sb = window.supabase.createClient(CFG.SUPABASE_URL, CFG.SUPABASE_KEY);
        const ses = await sb.auth.getSession();
        cuenta = (ses && ses.data && ses.data.session && ses.data.session.user) || null;
        sb.auth.onAuthStateChange(function(_e, s){
          if(s && s.user && !cuenta){ cuenta = s.user; cargar(); }
        });
      }catch{}
    }
    await cargar();
  }

  /* ---------------- marcado ---------------- */
  function aplicar(clave){
    const m = marcados.get(clave); if(!m || !m.nodo.isConnected) return;
    if(overrides.has(clave)){
      m.nodo.innerHTML = overrides.get(clave);
      m.nodo.classList.add('nb-mio');
    } else {
      m.nodo.innerHTML = m.original;
      m.nodo.classList.remove('nb-mio');
    }
  }

  const SELECTOR = 'p, li, blockquote, h1, h2, h3, h4, h5, td, th, summary, '
                 + 'dd, dt, figcaption, .desc, .act, .dial, .sub, .nota, .cl, .lead';
  /* Marca los textos de un contenedor. El prefijo debe ser estable entre
     repintados para que el mismo párrafo conserve su clave. `excluir` deja
     fuera las zonas que se repintan con su propio prefijo. */
  function marcar(contenedor, prefijo, excluir){
    if(!contenedor) return 0;
    let i = 0, n = 0;
    contenedor.querySelectorAll(SELECTOR).forEach(function(nodo){
      if(nodo.closest('#nbBar')) return;
      if(excluir && nodo.closest(excluir)) return;
      if(nodo.querySelector(SELECTOR)) return;             // solo las hojas
      const txt = (nodo.textContent||'').trim();
      if(txt.length < 3) return;
      const clave = prefijo + ':' + (i++);
      nodo.setAttribute('data-nbedit', clave);
      nodo.setAttribute('spellcheck','false');
      if(!marcados.has(clave) || marcados.get(clave).nodo !== nodo)
        marcados.set(clave, { nodo: nodo, original: nodo.innerHTML });
      if(editando) nodo.setAttribute('contenteditable','true');
      aplicar(clave);
      n++;
    });
    estado();
    return n;
  }

  /* ---------------- modo edición ---------------- */
  function alternar(){
    editando = !editando;
    document.body.classList.toggle('nb-edit', editando);
    const b = document.getElementById('nbEditar');
    b.classList.toggle('on', editando);
    b.textContent = editando ? 'TERMINAR' : 'EDITAR TEXTOS';
    marcados.forEach(function(m){
      if(!m.nodo.isConnected) return;
      if(editando) m.nodo.setAttribute('contenteditable','true');
      else m.nodo.removeAttribute('contenteditable');
    });
    avisar(editando ? 'Toca cualquier texto y escribe' : 'Edición terminada');
  }

  document.addEventListener('click', async function(e){
    if(e.target.closest('#nbEditar')){ alternar(); return; }
    if(e.target.closest('#nbRestaurar')){
      const propios = [...marcados.keys()].filter(k=>overrides.has(k));
      if(!propios.length) return;
      if(!confirm('¿Devolver '+propios.length+' textos de esta pantalla a su versión original?')) return;
      for(const k of propios){ await quitar(k); aplicar(k); }
      estado(); avisar('Textos restaurados');
    }
  });

  document.addEventListener('focusout', async function(e){
    if(!editando) return;
    const nodo = e.target && e.target.closest && e.target.closest('[data-nbedit]');
    if(!nodo) return;
    const clave = nodo.getAttribute('data-nbedit');
    const m = marcados.get(clave); if(!m) return;
    const valor = nodo.innerHTML.trim();
    if(valor === m.original.trim()){
      if(overrides.has(clave)){ await quitar(clave); nodo.classList.remove('nb-mio'); }
    } else {
      nodo.classList.add('nb-mio');
      avisar(await guardar(clave, valor));
    }
    estado();
  });

  window.NubiaEditor = { marcar: marcar, get activo(){ return editando; } };
  iniciar();
})();
