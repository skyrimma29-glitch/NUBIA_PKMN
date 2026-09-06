/* =====================================================================
   CONFIGURACIÓN DE NUBIA — rellena esto UNA sola vez.
   Todos los archivos del proyecto leen de aquí.

   1. Crea un proyecto gratis en supabase.com
   2. Panel → Project Settings → API
   3. Copia "Project URL" y la clave "anon public" abajo
   4. Corre el archivo esquema.sql en el editor SQL de Supabase
   5. Authentication → Providers → Google → actívalo
   ===================================================================== */
window.NUBIA = {
  SUPABASE_URL: 'https://hqfdppcjubuewmhipmtt.supabase.co',
  SUPABASE_KEY: 'sb_publishable_c-XHwyGoMy-DUQcft3Q8ng_TKD1EyzH',

  // Cuántas especies cuenta la Pokédex de Nubia como total.
  POKEDEX_TOTAL: 151,

  // Metas que desbloquean recompensa. Ajusta a tu gusto.
  METAS: [
    [10,  'Insignia de Observador',  'Un encuentro único te espera en la Ruta 3.'],
    [25,  'Insignia de Rastreador',  'Ventaja en la primera tirada de captura de cada sesión.'],
    [50,  'Insignia de Naturalista', 'Un encuentro único te espera en la Ciénaga Grande.'],
    [90,  'Insignia de Cronista',    'La Profesora Ceiba te abre su archivo privado.'],
    [151, 'Pokédex Completa',        'Acceso a la cumbre sin las ocho medallas.']
  ]
};
