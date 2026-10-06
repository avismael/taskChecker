# Validación de inicio rápido: MVP de seguimiento de tareas estudiantiles

## Requisitos previos

- Python 3.12 instalado.
- PostgreSQL disponible para el entorno de pruebas y desarrollo.
- Dependencias del proyecto instaladas desde el archivo de empaquetado de Python del repositorio.
- Una base de datos de pruebas configurada con una cadena de conexión aislada.

## Iniciar el servicio

1. Inicie los servicios con Docker: `make docker-up`.
2. Confirme el estado de la aplicación: `curl http://127.0.0.1:8080/health`.
3. Abra `http://127.0.0.1:8080/` en un navegador con una ventana del tamaño de un
   teléfono y en un navegador de escritorio.

Para un flujo de trabajo con SQLite únicamente en el host, cree y active un entorno
virtual con `python -m venv .venv && source .venv/bin/activate`, ejecute `make install`,
copie `.env.example` a `.env`, aplique `make migrate` e inicie con `make run`.

## Escenario de extremo a extremo

1. Registre al docente A y cree un año académico activo.
2. Cree una asignatura, una sección reutilizable y tres estudiantes.
3. Importe un CSV/XLSX que contenga una fila válida, una sin NIE y una duplicada;
   verifique los errores de la vista previa y confirme que las filas no válidas no
   se persistan silenciosamente.
4. Cree una tarea con fechas de asignación y entrega y abra su lista.
5. Registre una entrega puntual con evidencia PDF y una observación privada.
6. Avance el tiempo más allá de la fecha de entrega y verifique que la entrega
   pendiente restante se marque automáticamente como no entregada y quede auditada.
7. Registre una entrega atrasada y complete el seguimiento correspondiente.
8. Abra el perfil del estudiante, la vista del día y los cuatro tipos de informe;
   concilie los conteos y confirme que no aparezcan campos de calificación.
9. Cierre el año académico y verifique que los registros históricos sigan visibles,
   pero excluidos de los conteos del año activo.
10. Registre al docente B y verifique que el docente B y una persona administradora
    no puedan acceder a los datos pedagógicos del docente A.

## Suites de verificación requeridas

- Unit: transiciones de estado, validación de fechas, cálculos de cumplimiento,
  validación de filas de importación y filtros de informes.
- Integration: persistencia limitada por tenant, transacción más evento de auditoría,
  cierre del año académico, rechazo de evidencias y confirmación de importaciones.
- Contract: cada endpoint de [api.md](contracts/api.md), incluido el comportamiento
  no revelador ante solicitudes no autorizadas.
- Usabilidad/accesibilidad: lista de tareas en teléfono y escritorio, navegación por
  teclado, etiquetas legibles, estados vacíos y errores de validación visibles.

Ejecute el control automatizado con `make verify`. Un entorno con capacidad de
navegador también debería inspeccionar el DOM, el árbol de accesibilidad, la
consola, las llamadas de red y las capturas; el entorno actual del repositorio no
proporciona Chrome DevTools MCP.

## Resultado esperado

El escenario completo finaliza sin filtración entre tenants, pérdida de historial,
mutaciones sin atribución, errores silenciosos de importación, evidencias ZIP ni
datos de calificación.

## Estado actual de preparación para la versión

El control local automatizado está en verde: `make verify` ejecuta Ruff y 109
pruebas, incluidas las comprobaciones de accesibilidad de plantillas en
`frontend/tests/accessibility/`.
El control de migraciones está en verde: `make migrate` actualiza la base de datos
SQLite local hasta head, incluida una base existente cuyas tablas iniciales ya estaban
creadas.
El control de inicio de Docker también se validó con `make docker-up`, una comprobación
de salud de la aplicación respaldada por PostgreSQL en `/health` y `make docker-down`.
El control de inicio rápido del navegador se validó con Playwright y Chromium:
registro e inicio de sesión autenticados, creación de tareas y listas, capturas de
escritorio y de móvil de 390px, modificación de entregas, evidencia vinculada,
observación privada, historial, los cuatro informes JSON, cierre del año académico,
cero errores de consola y una instantánea del árbol de accesibilidad. Todo pasó
correctamente. Un segundo docente autenticado vio cero tareas y recibió la respuesta
no reveladora de una lista ajena.

**Preparación para la versión: APROBACIÓN CONDICIONAL.** Los controles del MVP pasan
localmente y contra la infraestructura PostgreSQL de Docker. El despliegue en
producción aún requiere una decisión operativa sobre el limitador de tasa de
autenticación local al proceso y una revisión humana con lector de pantalla.
