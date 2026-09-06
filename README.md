# Nubia Pokemon

Sitio web estatico para la region Nubia, una mesa de Pokemon 5E.

## Estructura

- `docs/`: paginas publicas y configuracion que publica GitHub Pages.
- `database/`: esquema SQL para Supabase.
- `tools/`: herramientas de desarrollo, como el generador de mapas.

## Publicar en GitHub Pages

1. Crea un repositorio en GitHub.
2. Sube el contenido de este proyecto a la rama `main`.
3. En `Settings > Pages`, selecciona `Deploy from a branch`.
4. Elige la rama `main` y la carpeta `/docs`.
5. Guarda y espera a que GitHub publique el sitio.

La URL tendra esta forma:

`https://TU_USUARIO.github.io/NOMBRE_DEL_REPOSITORIO/`

Configura esa URL en Supabase en `Authentication > URL Configuration`, tanto como `Site URL` como en `Redirect URLs`.

## Base de datos

Ejecuta `database/esquema.sql` completo en el SQL Editor de Supabase.

La configuracion web esta en `docs/nubia-config.js`. La clave `sb_publishable_...` es publica y puede vivir en el frontend; nunca uses una clave `service_role` en estos archivos.

## Herramientas

Para regenerar los mapas desde `tools/generar_mapas.py`:

```powershell
cd tools
python generar_mapas.py
```

La salida generada se guarda como `mapas.json` dentro de `tools/` y no se incluye en Git.
