# Validación de la integración local

Fecha de comprobación: 2026-10-28. Base Macfly `3295bba51b4719e947b501e7dbb809b8e3708572`. Paquete instalado: `0.5.0+accountbound.2`, Python `3.12.16` x64; dependencias de ejecución fijadas en requirements.lock (30 paquetes).

## Pruebas simuladas

`python -m pytest -q`: **122 passed**. No se utilizó Outlook real para esa suite. Cubre las funciones del proyecto base y las garantías añadidas de SMTP/PROPERTYPUTREF, cuenta cambiada por Save, borradores válidos, edición por EntryID, respuestas/reenvíos nativos simulados, aprobación invalidada por ediciones, hashes de adjuntos incorporados al borrador, caducidad antes y después de la verificación, revocación, consumo concurrente, un solo intento ante fallo incierto, catálogo MCP por stdio y preservación de configuración Codex.

No se afirma que se hayan realizado pruebas de entrega de correo, integración de borradores o formatos con Outlook real. El CI conserva pruebas unitarias Windows/Linux y no configura cuentas reales.

## Comprobación real autorizada

Se instaló un wheel en un entorno de ejecución por usuario separado del checkout editable. Se confirmó la importación desde ese entorno. El cliente MCP realizó únicamente initialize, tools/list, resources/list y outlook_whoami: catálogo exacto de doce herramientas, ningún recurso UI y enumeración de cuentas satisfactoria. Los datos obtenidos no se almacenan en este repositorio.

Codex reconoce outlook_classic por stdio, sus doce herramientas y la ruta del entorno instalado. La entrada ms365 permanece conservada pero deshabilitada. La configuración anterior tiene una copia fuera del repositorio. Es necesario iniciar una sesión nueva de Codex para cargar el servidor en el cliente; no se afirma que las herramientas hayan aparecido en la conversación que hizo la instalación.

No se han leído mensajes, creado borradores de prueba, enviado correos, movido/eliminado mensajes ni añadido tareas o servicios. No se desactivaron protecciones de Outlook.

## Revisión previa al push

Se revisaron los archivos añadidos y el historial alcanzable de la rama, manteniendo el original público. Antes del último hito de documentación, el escaneo comprendió 50 commits y 254 blobs únicos; no encontró los patrones de secretos o datos personales buscados. Las imágenes actuales heredadas se revisaron como ilustraciones del proyecto original. Es un escaneo por patrones, no una certificación de ausencia de cualquier secreto posible; no se importa historia privada del rescate.

Solo se publica la rama de implementación revisada, sin `--all`, `--mirror`, tags ni force-push. El remoto upstream no se modifica. Véase DEVELOPMENT_LOG.md para commits y resultado de los intentos de publicación.

## Pendiente

- Diseñar en otra tarea la autorización humana final. Actualmente el agente puede conocer la frase/id y el registro local está bajo el mismo usuario: el mecanismo no es una barrera independiente.
- Verificar lectura, creación/edición de borradores, hilo, remitente y adjuntos con Outlook real cuando el usuario solicite esas acciones concretas. Ningún envío de prueba queda autorizado por este informe.
- Acordar licencia abierta uniforme para las adaptaciones antes de una propuesta upstream. No se abre PR al proyecto original en esta fase.
