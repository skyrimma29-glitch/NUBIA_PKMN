/* =====================================================================
   EDITOR DE TEXTOS DE NUBIA
   Permite reescribir cualquier texto del códice, el atlas, los planos y
   las tablas de encuentro. Los cambios se guardan en la cuenta de quien
   los hace: los demás siguen viendo el texto original.

   Requiere nubia-config.js y la librería de Supabase cargados antes,
   y la tabla `textos` del archivo esquema.sql.
   ===================================================================== */
(function(){
  const CFG = window.NUBIA || {};
  let sb = null, cuenta = null, editando = false;
  const overrides = new Map();          // clave -> texto propio
  const marcados  = new Map();          // clave -> {nodo, original}

  /* ---------- estilos ---------- */
  const css = document.createElement('style');
  css.textContent = `
    #nbEditBar{position:fixed;right:16px;bottom:16px;z-index:200;display:flex;gap:8px;align-items:center}
    #nbEditBar button{font-family:'Silkscreen',monospace;font-size:10px;padding:11px 13px;
      border:3px solid #12283f;background:#fdf6e6;color:#12283f;cursor:pointer;
      box-shadow:4px 4px 0 rgba(0,0,0,.28);transition:background .14s,transform .08s}
    #nbEditBar button:hover{background:#fff}
    #nbEditBar button:active{transform:translate(2px,2px);box-shadow:2px 2px 0 rgba(0,0,0,.28)}
    #nbEditBar button.on{background:#c6386b;color:#fff;border-color:#12283f}
    #nbEditBar .aviso{font-family:'Alegreya Sans',sans-serif;font-size:12px;background:#12283f;
      color:#cfe0e6;padding:9px 12px;max-width:260px;line-height:1.4}
    body.nb-editando [data-nbedit]{outline:2px dashed #c6386b;outline-offset:2px;
      cursor:text;transition:background .12s}
    body.nb-editando [data-nbedit]:hover{background:#fff3f7}
    body.nb-editando [data-nbedit]:focus{outline:3px solid #c6386b;background:#fff}
    [data-nbedit].nb-propio{background:#fff8e2;box-shadow:inset 3px 0 0 #e0951c}
    #nbToast{position:fixed;left:50%;bottom:22px;transform:translateX(-50%) translateY(18px);
      z-index:210;background:#2e7d4f;color:#fff;font-family:'Silkscreen',monospace;font-size:10px;
      padding:11px 16px;border:3px solid #12283f;opacity:0;pointer-events:none;
      transition:opacity .2s,transform .2s}
    #nbToast.ver{opacity:1;transform:translateX(-50%)}
    @media (prefers-reduced-motion:reduce){#nbEditBar button,#nbToast{transition:none}}`;
  document.head.appendChild(css);

  const barra = document.createElement('div');
  barra.id = 'nbEditBar';
  barra.innerHTML = `<span class="aviso" id="nbAviso" style="display:none"></span>
    <button id="nbRestaurar" style="display:none">RESTAURAR</button>
    <button id="nbEditar">EDITAR TEXTOS</button>`;
  const toast = document.createElement('div');
  toast.id = 'nbToast';
  addEventListener('DOMContentLoaded', ()=>{
    document.body.appendChild(barra);
    document.body.appendChild(toast);
  });

  let toastT = null;
  function avisar(txt){
    toast.textContent = txt; toast.classList.add('ver');
    clearTimeout(toastT); toastT = setTimeout(()=>toast.classList.remove('ver'), 2200);
  }

  /* ---------- conexión ---------- */
  async function iniciar(){
    if(!CFG.SUPABASE_URL || !CFG.SUPABASE_KEY || !window.supabase) return;
    sb = window.supabase.createClient(CFG.SUPABASE_URL, CFG.SUPABASE_KEY);
    const { data:{ session } } = await sb.auth.getSession();
    cuenta = session?.user || null;
    sb.auth.onAuthStateChange((_e, s)=>{ if(s?.user && !cuenta){ cuenta = s.user; cargar(); } });
    if(cuenta) await cargar();
  }
  async function cargar(){
    if(!sb || !cuenta) return;
    const { data } = await sb.from('textos').select('clave,valor').eq('jugador', cuenta.id);
    (data||[]).forEach(r => overrides.set(r.clave, r.valor));
    // se aplica a lo que ya esté marcado en pantalla
    marcados.forEach((m, clave)=>{ if(overrides.has(clave)) aplicar(clave); });
  }
  async function guardar(clave, valor){
    if(!sb || !cuenta) return false;
    const { error } = await sb.from('textos')
      .upsert({ jugador: cuenta.id, clave, valor }, { onConflict:'jugador,clave' });
    return !error;
  }
  async function borrar(clave){
    if(!sb || !cuenta) return false;
    const { error } = await sb.from('textos').delete().eq('jugador', cuenta.id).eq('clave', clave);
    return !error;
  }

  function aplicar(clave){
    const m = marcados.get(clave); if(!m) return;
    if(overrides.has(clave)){
      m.nodo.innerHTML = overrides.get(clave);
      m.nodo.classList.add('nb-propio');
    } else {
      m.nodo.innerHTML = m.original;
      m.nodo.classList.remove('nb-propio');
    }
  }

  /* ---------- marcar lo editable ---------- */
  const SELECTOR = 'p, li, blockquote, h2, h3, h4, h5, .desc, .act, .sub, .notas, .nom, td, summary, .cl';
  /* Marca todos los textos de un contenedor. El prefijo debe ser estable
     entre repintados: así el mismo párrafo conserva su clave. */
  function marcar(contenedor, prefijo){
    if(!contenedor) return;
    let i = 0;
    contenedor.querySelectorAll(SELECTOR).forEach(n=>{
      if(n.querySelector(SELECTOR)) return;           // solo las hojas del árbol
      const txt = (n.textContent||'').trim();
      if(txt.length < 3) return;
      const clave = prefijo + ':' + (i++);
      n.setAttribute('data-nbedit', clave);
      n.setAttribute('spellcheck', 'false');
      marcados.set(clave, { nodo:n, original:n.innerHTML });
      if(editando) n.setAttribute('contenteditable', 'true');
      aplicar(clave);
    });
    refrescarBarra();
  }

  function refrescarBarra(){
    const b = document.getElementById('nbRestaurar');
    if(!b) return;
    const propios = [...marcados.keys()].filter(k=>overrides.has(k)).length;
    b.style.display = propios ? '' : 'none';
    b.textContent = 'RESTAURAR ' + propios;
  }

  /* ---------- modo edición ---------- */
  function alternar(){
    if(!cuenta){
      const a = document.getElementById('nbAviso');
      a.style.display = '';
      a.textContent = 'Entra con tu cuenta desde el menú para guardar tus propios textos. '
                    + 'Los cambios sin cuenta no se guardan.';
      setTimeout(()=>{ a.style.display='none'; }, 6000);
      return;
    }
    editando = !editando;
    document.body.classList.toggle('nb-editando', editando);
    const b = document.getElementById('nbEditar');
    b.classList.toggle('on', editando);
    b.textContent = editando ? 'TERMINAR EDICIÓN' : 'EDITAR TEXTOS';
    marcados.forEach(m=>{
      if(editando) m.nodo.setAttribute('contenteditable','true');
      else m.nodo.removeAttribute('contenteditable');
    });
    if(editando) avisar('Toca cualquier texto y escribe');
  }

  document.addEventListener('focusout', async e=>{
    if(!editando) return;
    const n = e.target.closest?.('[data-nbedit]'); if(!n) return;
    const clave = n.getAttribute('data-nbedit');
    const m = marcados.get(clave); if(!m) return;
    const valor = n.innerHTML.trim();
    if(valor === m.original.trim()){
      if(overrides.has(clave)){ overrides.delete(clave); await borrar(clave); }
      n.classList.remove('nb-propio');
    } else {
      overrides.set(clave, valor);
      n.classList.add('nb-propio');
      avisar(await guardar(clave, valor) ? 'Guardado en tu cuenta' : 'No se pudo guardar');
    }
    refrescarBarra();
  });

  document.addEventListener('click', async e=>{
    if(e.target.id === 'nbEditar'){ alternar(); return; }
    if(e.target.id === 'nbRestaurar'){
      const propios = [...marcados.keys()].filter(k=>overrides.has(k));
      if(!propios.length) return;
      if(!confirm('¿Devolver '+propios.length+' textos de esta pantalla a su versión original?')) return;
      for(const k of propios){ overrides.delete(k); await borrar(k); aplicar(k); }
      refrescarBarra(); avisar('Textos restaurados');
    }
  });

  window.NubiaEditor = { marcar, get activo(){ return editando; } };
  iniciar();
})();
