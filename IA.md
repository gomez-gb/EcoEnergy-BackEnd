# Registro de uso de IA — EcoEnergy Fase 1

**Herramienta:** Claude Code (dos sesiones: una de guía/análisis sobre el vault
académico, otra con acceso directo al repositorio del proyecto).

## 1. Limpieza y configuración base (sesión con acceso al repo)
- **Prompt:** instrucción acotada para eliminar código de laboratorio ajeno
  al caso EcoEnergy, corregir un bug de sintaxis preexistente en `base.html`,
  crear los archivos `data/*.json` con contenido ya definido, e instalar y
  registrar `django-bootstrap5`. Se le prohibió explícitamente escribir
  lógica de negocio.
- **Qué se usó:** los 4 commits resultantes (limpieza, fix, data, dependencia).
- **Verificación propia:** revisé cada commit, corrí `python manage.py check`
  después de cada paso, y confirmé en el navegador que las rutas seguían
  respondiendo.

## 2. Diseño de datos de prueba (zonas.json, categorias.json, dispositivos.json)
- **Prompt:** pedí una propuesta de datos coherentes con el caso (zonas con
  distintos límites, dispositivos que produjeran al menos un caso ALERTA y
  uno NORMAL, y una zona sin dispositivos para el caso vacío).
- **Qué se usó:** el contenido exacto de los 3 archivos JSON.
- **Verificación propia:** calculé a mano el consumo total esperado por zona
  y confirmé que la app mostraba los mismos resultados (zona 1 en ALERTA,
  zonas 2 y 3 en NORMAL, zona 4 vacía).

## 3. Lógica de negocio (services.py, views.py)
- **Uso de IA:** limitado a explicación conceptual, esqueletos con TODOs, y
  revisión de código ya escrito por mí — nunca autoría directa de esta parte,
  por ser la lógica evaluada (F1-2/F1-4).
- **Bugs que la IA detectó en mi código y yo corregí:** uso de un campo
  (`estado`) que no existía en mis datos (copiado sin adaptar de un ejemplo
  del material); `consumo_total` sumando la lista incorrecta (todos los
  dispositivos en vez de solo los de la zona); operador de comparación
  (`>=` en vez de `>`) que clasificaba mal el caso límite exacto; mutación
  de diccionarios originales en `listado_zonas`.
- **Verificación propia:** escribí y probé cada función en `manage.py shell`
  y en el navegador antes de darla por cerrada.

## 4. Templates (Bootstrap)
- **Uso de IA:** aquí sí se usaron propuestas completas de HTML/Bootstrap
  (explícitamente permitido por el enunciado), para `catalogo.html`
  (práctica de Clase 5), `listado_zonas.html` y `detalle_zona.html`.
- **Adaptación propia:** integré las plantillas al proyecto real, verifiqué
  que las variables coincidieran con el contexto de mis Views, y las probé
  visualmente en el navegador (tarjetas, tabla con scroll, badge de estado).

## 5. Diagnóstico de errores
- Se usó IA (sesión con acceso al repo, en modo solo lectura/análisis, sin
  permiso para modificar nada) para diagnosticar un `ModuleNotFoundError`
  por un nombre de app mal escrito en `config/urls.py`, y para investigar
  un `NoReverseMatch` transitorio que resultó ser una página de error vieja
  en caché del navegador. Verifiqué ambos diagnósticos reproduciendo el
  problema y confirmando la corrección.
