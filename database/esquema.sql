-- =====================================================================
-- NUBIA · esquema de base de datos
-- Pégalo entero en Supabase → SQL Editor → Run. Es seguro correrlo dos veces.
-- =====================================================================

-- ------------------------------------------------------- 1. PERFILES
create table if not exists perfiles (
  id      uuid primary key references auth.users on delete cascade,
  nombre  text,
  avatar  text,
  creado  timestamptz default now()
);

-- Crea el perfil solo la primera vez que alguien entra con Google
create or replace function crear_perfil()
returns trigger language plpgsql security definer set search_path = public as $$
begin
  insert into perfiles (id, nombre, avatar)
  values (
    new.id,
    coalesce(new.raw_user_meta_data->>'full_name', split_part(new.email,'@',1)),
    new.raw_user_meta_data->>'avatar_url'
  )
  on conflict (id) do nothing;
  return new;
end $$;

drop trigger if exists al_crear_usuario on auth.users;
create trigger al_crear_usuario
  after insert on auth.users
  for each row execute function crear_perfil();

-- ------------------------------------------------------ 2. PARTIDAS
create table if not exists partidas (
  id           uuid primary key default gen_random_uuid(),
  codigo       text unique not null,
  nombre       text not null,
  director     uuid not null references auth.users on delete cascade,
  estado       jsonb not null default '{}'::jsonb,
  actualizado  timestamptz default now(),
  creado       timestamptz default now()
);
create index if not exists partidas_director_idx on partidas(director);

-- ------------------------------------------------------ 3. MIEMBROS
create table if not exists miembros (
  partida  uuid references partidas on delete cascade,
  jugador  uuid references auth.users on delete cascade,
  entro    timestamptz default now(),
  primary key (partida, jugador)
);
create index if not exists miembros_jugador_idx on miembros(jugador);

-- ------------------------------------------------------- 4. POKÉDEX
create table if not exists pokedex (
  partida   uuid references partidas on delete cascade,
  jugador   uuid references auth.users on delete cascade,
  especie   text not null,
  nombre    text,
  atrapado  boolean default false,
  visto     timestamptz default now(),
  primary key (partida, jugador, especie)
);
create index if not exists pokedex_jugador_idx on pokedex(partida, jugador);

-- ============================================ POLÍTICAS DE ACCESO
alter table perfiles  enable row level security;
alter table partidas  enable row level security;
alter table miembros  enable row level security;
alter table pokedex   enable row level security;

-- Estas funciones consultan las relaciones sin volver a evaluar sus políticas RLS.
-- Evitan la recursión partidas -> miembros -> partidas.
create or replace function public.es_director_partida(p_partida uuid)
returns boolean
language sql
stable
security definer
set search_path = public
as $$
  select exists (
    select 1 from partidas
    where id = p_partida and director = auth.uid()
  );
$$;

create or replace function public.es_miembro_partida(p_partida uuid)
returns boolean
language sql
stable
security definer
set search_path = public
as $$
  select exists (
    select 1 from miembros
    where partida = p_partida and jugador = auth.uid()
  );
$$;

revoke execute on function public.es_director_partida(uuid) from public;
revoke execute on function public.es_miembro_partida(uuid) from public;
grant execute on function public.es_director_partida(uuid) to authenticated;
grant execute on function public.es_miembro_partida(uuid) to authenticated;

-- Perfiles: todos los identificados pueden leer nombres; cada quien edita el suyo
drop policy if exists perfiles_leer on perfiles;
create policy perfiles_leer on perfiles
  for select to authenticated using (true);

drop policy if exists perfiles_editar on perfiles;
create policy perfiles_editar on perfiles
  for update to authenticated using (id = auth.uid());

-- Partidas: las ve su director y quienes se hayan unido
drop policy if exists partidas_leer on partidas;
create policy partidas_leer on partidas
  for select to authenticated using (
    director = auth.uid()
    or public.es_miembro_partida(id)
  );

drop policy if exists partidas_crear on partidas;
create policy partidas_crear on partidas
  for insert to authenticated with check (director = auth.uid());

-- Solo el director guarda el estado de la mesa
drop policy if exists partidas_guardar on partidas;
create policy partidas_guardar on partidas
  for update to authenticated using (director = auth.uid());

drop policy if exists partidas_borrar on partidas;
create policy partidas_borrar on partidas
  for delete to authenticated using (director = auth.uid());

-- Miembros: cada quien ve las filas de sus partidas
drop policy if exists miembros_leer on miembros;
create policy miembros_leer on miembros
  for select to authenticated using (
    jugador = auth.uid()
    or public.es_director_partida(partida)
  );

drop policy if exists miembros_salir on miembros;
create policy miembros_salir on miembros
  for delete to authenticated using (jugador = auth.uid());

-- Pokédex: cada jugador escribe la suya; el director lee las de su partida
drop policy if exists pokedex_leer on pokedex;
create policy pokedex_leer on pokedex
  for select to authenticated using (
    jugador = auth.uid()
    or public.es_director_partida(partida)
  );

drop policy if exists pokedex_registrar on pokedex;
create policy pokedex_registrar on pokedex
  for insert to authenticated with check (jugador = auth.uid());

drop policy if exists pokedex_actualizar on pokedex;
create policy pokedex_actualizar on pokedex
  for update to authenticated using (jugador = auth.uid());

-- ============================================ UNIRSE POR CÓDIGO
-- Deja entrar con el código sin exponer la lista de partidas de nadie.
create or replace function unirse_partida(p_codigo text)
returns table (id uuid, nombre text, codigo text)
language plpgsql security definer set search_path = public as $$
declare v_id uuid;
begin
  select p.id into v_id from partidas p where p.codigo = upper(trim(p_codigo));
  if v_id is null then
    raise exception 'No existe ninguna partida con ese código';
  end if;
  insert into miembros (partida, jugador) values (v_id, auth.uid())
    on conflict do nothing;
  return query select p.id, p.nombre, p.codigo from partidas p where p.id = v_id;
end $$;

grant execute on function unirse_partida(text) to authenticated;

-- ============================================ ALMACENAMIENTO
-- Mapas y fichas. Lectura pública, escritura solo de identificados.
insert into storage.buckets (id, name, public)
values ('nubia', 'nubia', true)
on conflict (id) do nothing;

drop policy if exists nubia_leer on storage.objects;
create policy nubia_leer on storage.objects
  for select using (bucket_id = 'nubia');

drop policy if exists nubia_subir on storage.objects;
create policy nubia_subir on storage.objects
  for insert to authenticated with check (bucket_id = 'nubia');

drop policy if exists nubia_reemplazar on storage.objects;
create policy nubia_reemplazar on storage.objects
  for update to authenticated using (bucket_id = 'nubia');

drop policy if exists nubia_borrar on storage.objects;
create policy nubia_borrar on storage.objects
  for delete to authenticated using (bucket_id = 'nubia' and owner = auth.uid());
