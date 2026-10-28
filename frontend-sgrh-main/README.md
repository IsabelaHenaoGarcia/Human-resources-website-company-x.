# Frontend SGRH

Aplicación de gestión de recursos humanos construida con Next.js, React y TypeScript.

## Requisitos

- Node.js 18 o superior
- npm
- Una instancia accesible del backend FastAPI

## Instalación y desarrollo local

```bash
npm ci
```

Copia `.env.example` a `.env.local` y define la dirección del backend local:

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

Inicia el servidor:

```bash
npm run dev
```

La aplicación estará disponible en `http://localhost:3000`.

## Despliegue en Vercel

Al importar el repositorio en Vercel, configura **Root Directory** como `frontend-sgrh-main`. Vercel detectará Next.js y usará `npm run build` automáticamente.

Agrega esta variable en **Settings → Environment Variables**:

| Variable | Descripción |
| --- | --- |
| `NEXT_PUBLIC_API_BASE_URL` | URL HTTPS pública del backend, sin barra final. Ejemplo: `https://api.tu-dominio.com` |

Guarda la variable para Production y los entornos adicionales que utilices, y vuelve a desplegar. El backend FastAPI debe desplegarse por separado y permitir en CORS el origen de este frontend.

## Comandos

```bash
npm run dev
npm run lint
npm run typecheck
npm run build
```

## Rutas

- `/login`
- `/dashboard`
- `/employees`
- `/recruitment/candidates`
- `/affiliations`
- `/payroll/periods`
- `/offboarding`
- `/training/activities`
- `/evaluations`
- `/certificates`
- `/reports`
- `/audit`
- `/admin/users`
