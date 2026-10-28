# Sistema de Gestión de Recursos Humanos (SGRH)

Proyecto compuesto por una aplicación web Next.js y una API FastAPI. El frontend se puede desplegar en Vercel. La API y la base de datos se despliegan por separado.

## Estructura

```text
talento-humano-vercel/
├── frontend-sgrh-main/   # Aplicación Next.js para Vercel
└── backend-sgrh-main/    # API FastAPI y migraciones Alembic
```

## Requisitos

- Node.js 18 o superior y npm.
- Python 3.10 o superior.
- Una base de datos PostgreSQL para producción.
- Un servicio para alojar la API FastAPI. Vercel publica el frontend; no se recomienda usar el almacenamiento local del backend en funciones serverless.

## Desarrollo local

### 1. Preparar el backend

Abre una terminal en `backend-sgrh-main` y ejecuta:

```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux:
# source .venv/bin/activate
python -m pip install -r requirements.txt
```

Copia `.env.example` a `.env`, configura `DATABASE_URL` y `JWT_SECRET_KEY` y aplica las migraciones:

```bash
python -m alembic upgrade head
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

La documentación de la API queda en `http://localhost:8000/docs`.

### 2. Preparar el frontend

En otra terminal, abre `frontend-sgrh-main` y ejecuta:

```bash
npm ci
```

Copia `.env.example` a `.env.local` y deja la URL local de la API:

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

Después inicia Next.js:

```bash
npm run dev
```

Abre `http://localhost:3000`.

## Despliegue del frontend en Vercel

1. Sube esta carpeta a un repositorio Git y selecciónalo al crear un proyecto en Vercel.
2. En **Root Directory**, selecciona `frontend-sgrh-main`.
3. Vercel detectará Next.js. Los comandos predeterminados son `npm run build` y la salida `.next`; no hace falta configurar una salida estática.
4. En **Settings → Environment Variables**, agrega:

   | Variable | Valor |
   | --- | --- |
   | `NEXT_PUBLIC_API_BASE_URL` | URL HTTPS pública de la API desplegada, sin barra final. Ejemplo: `https://api.tu-dominio.com` |

5. Aplica la variable a los entornos que usarás (Production, Preview y Development), según corresponda, y vuelve a desplegar.

## Despliegue de la API

Despliega `backend-sgrh-main` en un servicio compatible con aplicaciones ASGI. Configura allí las variables del archivo `backend-sgrh-main/.env.example` como variables del servicio, ejecuta `python -m alembic upgrade head` como paso de despliegue y usa este comando de inicio:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

En Windows local, el comando puede ejecutarse con `python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`.

En producción:

- Usa PostgreSQL administrado y una `DATABASE_URL` con el formato esperado por SQLAlchemy, por ejemplo `postgresql+psycopg://usuario:clave@host:5432/base`.
- Define `JWT_SECRET_KEY` con un secreto aleatorio largo. No uses el valor de desarrollo ni lo subas al repositorio.
- Define `FRONTEND_ORIGINS` con el origen exacto del frontend, por ejemplo `https://tu-proyecto.vercel.app`. Para permitir previews, agrega explícitamente sus orígenes; el backend no debe aceptar cualquier origen.
- Si habilitas `INITIAL_ADMIN_PASSWORD`, úsala solo para la inicialización, cambia la contraseña después y evita guardar credenciales reales en Git.
- El almacenamiento configurado por `STORAGE_PATH` es local. En un despliegue serverless o con instancias efímeras, los archivos pueden perderse; configura almacenamiento persistente/externo antes de usar cargas de documentos en producción.

## Comandos del frontend

Desde `frontend-sgrh-main`:

```bash
npm run dev
npm run lint
npm run typecheck
npm run build
```

## Notas

- La aplicación necesita una API disponible para iniciar sesión y consultar o guardar datos; desplegar solo el frontend publica la interfaz, no el backend.
- Nunca subas `.env`, `.env.local`, contraseñas, tokens ni claves privadas al repositorio.
- La ruta `/` redirige al panel. Si no hay sesión activa, inicia sesión desde `/login`.
