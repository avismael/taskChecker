# Ejemplos de importación de estudiantes

Esta carpeta contiene archivos ficticios para probar la importación masiva de
estudiantes. No incluyen datos personales reales ni secretos.

## Archivos

- `alumnos_ejemplo.csv`: diez registros válidos, listos para una importación de
  prueba.
- `alumnos_ejemplo.xlsx`: la misma estructura en formato XLSX, para probar la
  importación desde una hoja de cálculo.
- `alumnos_mixto.csv`: combina registros válidos con un NIE ausente y un NIE
  duplicado para demostrar la validación de la vista previa. **No debe
  confirmarse mediante la importación**, porque contiene errores intencionados.

## Encabezados aceptados

Todos los archivos deben incluir el encabezado obligatorio `nie`. Para el nombre
se acepta `nombre` o `first_name`, y para el apellido se acepta `apellido` o
`last_name`. Los archivos CSV deben estar codificados en UTF-8. En los archivos
XLSX se utiliza la primera hoja.

Los valores de ejemplo son ficticios. Sustituya los datos solo en una copia
local y no incluya secretos, contraseñas, tokens ni datos personales reales en
archivos versionados.

## Uso desde la interfaz

1. Inicie sesión como docente y abra la sección de importación de estudiantes.
2. Seleccione un archivo de ejemplo y ejecute la vista previa.
3. Revise todas las filas y sus errores.
4. Confirme únicamente un archivo sin errores, como `alumnos_ejemplo.csv` o
   `alumnos_ejemplo.xlsx`.

No confirme `alumnos_mixto.csv`: está diseñado únicamente para comprobar que la
vista previa identifica un NIE ausente y un NIE duplicado.

## Uso mediante API

La vista previa se solicita con una carga multipart en
`POST /students/imports/preview` usando el campo `file`:

```bash
curl -X POST http://127.0.0.1:8080/students/imports/preview \
  -H "Authorization: Bearer <token-de-prueba>" \
  -F "file=@examples/imports/alumnos_ejemplo.csv"
```

Después de revisar la respuesta, la importación se confirma con
`POST /students/imports/commit`, enviando también `academic_year_id` y
`section_id` como parámetros y el archivo en `file`. Use autenticación válida
del entorno de desarrollo y nunca escriba tokens, cookies o credenciales en
este README, en scripts ni en archivos de ejemplo.
