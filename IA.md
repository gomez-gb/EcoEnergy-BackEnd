# Registro de uso de IA — EcoEnergy Fase 1

**Herramienta:** Claude Code — dos sesiones: una de guía y análisis conceptual
(trabajando sobre el vault académico, sin acceso al repositorio del proyecto),
y otra con acceso directo al repositorio `EcoEnergy-BackEnd`, usada solo para
tareas de infraestructura/rutina bajo instrucciones explícitas y acotadas.

## 1. Limpieza y configuración base (sesión con acceso al repo)

**Prompt usado (textual):**
> "Vamos a dejar el proyecto EcoEnergy-BackEnd limpio y listo como base, ANTES
> de que el estudiante escriba la lógica evaluada. [...] Haz esto en commits
> separados, con mensajes claros: 1. LIMPIEZA: elimina de la app "dispositivos"
> las views catalogo, medidores, paneles, dispositivos_zona, detalle_alerta [...]
> 2. FIX de bug de sintaxis preexistente [...] 3. DATOS DE PRUEBA (contenido
> exacto, no lo cambies ni inventes valores distintos) [...] 4. CONFIGURACIÓN
> mecánica de django-bootstrap5 [...] NO hagas nada de esto — es la parte que
> se evalúa y la debo escribir yo: No crees dispositivos/services.py [...]"

**Respuesta utilizada:** los 4 commits resultantes (`9b14212`, `1bef3aa`,
`562398f`, `6e139a8`) — limpieza de vistas de laboratorio, corrección de
`</html>`, contenido de `data/*.json` (redactado previamente y entregado para
que solo lo aplicara), e instalación/registro de `django-bootstrap5`.

**Cambios propios y verificación:** revisé cada commit con `git show`, corrí
`python manage.py check` después de cada paso, y confirmé en el navegador que
las rutas seguían respondiendo antes de continuar.

## 2. Diseño de datos de prueba

**Prompt usado (resumen fiel):** pedí una propuesta de zonas/categorías/
dispositivos que produjera al menos un caso ALERTA, uno NORMAL, y una zona
sin dispositivos para probar el caso vacío.

**Respuesta utilizada:** el contenido exacto de `zonas.json`, `categorias.json`
y `dispositivos.json`.

**Verificación propia:** calculé a mano el consumo esperado por zona y
confirmé que la aplicación mostraba los mismos resultados una vez implementada
la lógica (zona 1 en ALERTA, zonas 2 y 3 en NORMAL, zona 4 vacía).

## 3. Lógica de negocio (services.py, views.py) — NO escrita por IA

El uso de IA se limitó estrictamente a explicación conceptual, esqueletos con
comentarios TODO, y revisión de código que yo mismo escribí — nunca autoría
directa, por ser la lógica evaluada (F1-2/F1-4).

**Ejemplos de mis propios prompts en esta sesión:**
> "Ayudame a implementarlo de la mejor manera, cubramos todos los procesos de
> 'logica' en esta parte para no agregar procesos de 'lógica' en el template
> que es más de vista"

> "generame un esquema de 'guía' para elaborar la función"

**Bugs que la IA detectó en revisiones de mi código, y que corregí yo mismo:**
- Uso de un campo (`estado`) copiado del material de clase sin adaptar a mis
  datos reales (no existía en mi JSON).
- `consumo_total` sumando la lista incorrecta (todos los dispositivos del
  proyecto en vez de solo los de la zona).
- Operador de comparación (`>=` en vez de `>`) que clasificaba mal el caso
  límite exacto de consumo igual al límite.
- Mutación de los diccionarios originales de `zonas` en `listado_zonas`
  (corregido usando `{**zona, ...}` para crear diccionarios nuevos).

**Verificación propia:** probé cada función en `manage.py shell` y cada
View/Template en el navegador (zona en ALERTA, zonas en NORMAL, zona vacía,
id inexistente) antes de darlas por cerradas.

## 4. Templates (HTML/Bootstrap) — uso de IA explícitamente permitido

**Mi prompt:** pedí ayuda para diseñar `catalogo.html` (práctica de Clase 5),
`listado_zonas.html` y `detalle_zona.html` en Bootstrap, dándole el contexto
real de las variables que mis Views entregan, sin pedirle que inventara
lógica ni variables.

**Respuesta utilizada:** las 3 plantillas completas propuestas, con herencia
de `base.html`, tarjetas Bootstrap, `{% for %}...{% empty %}` para listas
vacías, y badges de estado con texto+ícono.

**Adaptación propia:** integré las plantillas al proyecto real, confirmé que
cada variable coincidiera con el contexto real de mis Views, y las probé
visualmente en el navegador.

## 5. Diagnóstico de errores (sesión con acceso al repo, solo lectura)

Se usó IA en modo estrictamente de solo-lectura/diagnóstico (instrucción
explícita de no modificar nada) para:
- Investigar un `ModuleNotFoundError` causado por `include("catalogo.urls")`
  mal escrito en `config/urls.py` (confusión entre nombre de View y nombre
  de app).
- Investigar un `NoReverseMatch` transitorio, que resultó ser una página de
  error vieja cacheada en el navegador durante una edición en curso.
- Auditoría final de todo el repositorio contra la rúbrica de la Fase 1
  (matriz CA-01 a CA-13, pruebas de los escenarios de la sección 6,
  revisión de `requirements.txt`, `.gitignore`, indentación e historial de
  commits) — que detectó que `services.py` y los templates de zonas nunca se
  habían commiteado, entre otros hallazgos.

**Verificación propia:** reproduje cada diagnóstico y confirmé la corrección
correspondiente antes de continuar.
