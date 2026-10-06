# TaskChecker

TaskChecker registra las entregas de tareas estudiantiles, las evidencias, las
observaciones privadas y el seguimiento. No es un sistema de calificaciones.

## Desarrollo

```bash
python -m venv .venv
source .venv/bin/activate
make install
cp .env.example .env
make migrate
make seed
make test
make lint
make run
```

El servicio utiliza de forma predeterminada una base de datos SQLite local para
desarrollo. PostgreSQL es el destino de almacenamiento para producción y se
selecciona mediante `TASKCHECKER_DATABASE_URL`.

La interfaz web local está disponible en `http://127.0.0.1:8080/`. Cree una cuenta
en `/register` y configure un año académico, una sección, una asignatura,
estudiantes y una tarea desde la navegación del espacio de trabajo.

### Datos de desarrollo

Para cargar datos reproducibles para la interfaz y los informes, ejecute:

```bash
make seed
```

La cuenta de desarrollo es `seed.teacher@taskchecker.local` y su contraseña es
`taskchecker-dev-password`. Estas credenciales son únicamente locales y no deben
usarse fuera de un entorno de desarrollo. El seed crea datos de seguimiento en
español, no calificaciones, y reutiliza sus registros al ejecutarse de nuevo.
Los archivos versionados que definen el catálogo, estudiantes, tareas, estados de
entrega y fixtures de evidencias están en `backend/app/scripts/seed_data/`. `make
seed` los valida antes de abrir la transacción y puede ejecutarse de forma segura
varias veces.

Los archivos ficticios para probar la importación masiva de estudiantes están en
`examples/imports/`; incluyen ejemplos válidos en CSV/XLSX y un CSV con errores
intencionados para validar la vista previa. Consulte su README antes de usarlos.

## Verificación

```bash
make verify
```

La suite automatizada cubre el aislamiento por tenant, las migraciones, la
autenticación, los estados de entrega, el rechazo de evidencias, las
importaciones, los informes, los contratos de páginas, los límites de tasa y la
correlación de solicitudes. También comprueba que las plantillas principales
incluyan encabezados, controles etiquetados, patrones de interacción enfocables y
superficies de estado anunciadas. Las capturas del navegador, la inspección del
árbol de accesibilidad y la generación real de PDF no forman parte actualmente
del control local.

El control local actual ejecuta Ruff y 109 pruebas:

```bash
make lint
make test
```

## Docker

Docker Compose inicia PostgreSQL y la aplicación, aplica las migraciones y
conserva los datos de base de datos y almacenamiento en volúmenes con nombre:

```bash
make docker-up
curl http://127.0.0.1:8080/health
make docker-logs
make docker-down
```

Los volúmenes `taskchecker-postgres` y `taskchecker-storage` persisten aunque se
ejecute `docker compose down`; por eso los datos de PostgreSQL y los archivos de
almacenamiento se conservan al volver a levantar los servicios. Para eliminarlos
de forma explícita use `docker compose down -v`.

Personalice la configuración de Docker con `POSTGRES_DB`, `POSTGRES_USER`,
`POSTGRES_PASSWORD`, `TASKCHECKER_SESSION_SECRET` y `TASKCHECKER_PORT`.
