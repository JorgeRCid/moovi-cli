# Recetas

Todas las recetas usan la CLI `moovi` en modo de solo lectura.

## Verificar la sesión

```bash
moovi whoami --json
```

Si falla con código 2, pide al usuario que ejecute `moovi login` en su terminal. No pidas la contraseña por chat.

## Buscar el ID de un curso

```bash
moovi courses --json \
  | jq -r '.[] | select(.short_name == "M1") | "\(.id)\t\(.full_name)"'
```

También se puede buscar por nombre:

```bash
moovi courses --json \
  | jq -r '.[] | select(.full_name | test("Matemáticas"; "i")) | "\(.id)\t\(.full_name)"'
```

## Ver el contenido de un curso

```bash
moovi contents 12345 --json
```

Para un resumen legible:

```bash
moovi contents 12345
```

Cada sección trae `name`, `summary` y `modules`; cada módulo trae `mod_name`, `name`, `visible` y `url`.

## Listar alumnado sin correos

```bash
moovi participants 12345 --json
```

Con correos, solo si el usuario lo pide:

```bash
moovi participants 12345 --emails --json
```

Cada persona incluye `groups` (grupos del curso creados por el profesorado) y `roles`.

## Leer el foro de noticias de Moovi

Moovi crea automáticamente un foro de noticias por materia. No lo busques por nombre: el comando lo localiza por tipo.

```bash
moovi announcements 12345 --json
```

Si hay varios foros de noticias, el comando muestra los ids y pide elegir:

```bash
moovi announcements 12345 --forum-id 2217 --json
```

Para leer un anuncio concreto, usa el id de la columna `ID`:

```bash
moovi announcement-content 63251 --json
```

En JSON, `message` es el HTML original y `message_text` el texto limpio. En tabla/CSV se usa el texto limpio.

## Alumnado de un grupo

```bash
moovi participants 12345 --format raw | grep ',PROII_1 (Laboratorio),'
```

En `--format raw`, los grupos van en la columna `groups` separados por `;`.

## Ver tareas y fechas de entrega

```bash
moovi assignments 12345 --json
```

Ordenar por fecha de entrega:

```bash
moovi assignments 12345 --json \
  | jq 'sort_by(.due_date // "9999")'
```

## Descargar todas las notas de un curso

```bash
moovi grades 12345 --format raw > notas.csv
```

Por defecto solo incluye calificaciones con al menos una nota. Para incluir todas las columnas del libro:

```bash
moovi grades 12345 --all-items --format raw > notas.csv
```

Las primeras columnas son `id`, `id_number`, `last_name`, `first_name`, `groups`; después, una por calificación. Requiere permisos de profesorado.

## Filtrar las notas de un grupo

```bash
moovi grades 6912 --json \
  | jq '.[] | select(any(.groups[]; .name == "DAGSS_2"))'
```

En CSV, la columna `groups` va separada por `;`. Para un filtro rápido:

```bash
moovi grades 6912 --format raw \
  | awk -F, 'NR==1 || $5 ~ /(^|;)DAGSS_2(;|$)/'
```

Si los nombres de grupo pueden contener comas, usa `--json` + `jq`.

## Mostrar un resumen al usuario

1. Ejecuta el comando con `--json`.
2. Extrae solo los campos relevantes.
3. Responde en texto, sin pegar el JSON completo si no aporta.
