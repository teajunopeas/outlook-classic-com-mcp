# Procedencia y licencias

Se conserva íntegro el historial público de Macfly hasta `3295bba51b4719e947b501e7dbb809b8e3708572`, junto a LICENSE (MIT, Anas Ahmed Shaikh) y sus avisos. Las modificaciones locales se mantienen separadas de las fuentes del rescate. No se importó el historial privado, documentos, cuentas, configuraciones ni código académico del usuario.

El usuario autorizó portar piezas seleccionadas de su rescate para su instalación local:

- `secure_dispatch.py`: selección SMTP exacta, PROPERTYPUTREF, verificación de cuenta/delegación y clasificación del fallo antes/después de Send. SHA-256 de la copia examinada: `b745d298b24337c9f89853dc130f32da3afe2350928480138fabcf4dd2ba7377`.
- `secure_drafts.py`: serialización/hash canónico, caducidad e invalidación de aprobación. SHA-256: `96ffb25ae2c410cbddf575d758ec0db15dc72ca335595d8d1456a3e47ffe225c`.
- Sus pruebas de remitente sirvieron para adaptar las pruebas con fixtures nuevos `example.test`.

No se copian sus imports de exportación, procesador, cola JSON, tareas, HMAC local, claves ni duplicación del plugin. Tampoco se copió código de las otras variantes citadas como referencia.

El material de rescate no incluía una licencia raíz. La autorización de uso local no se presenta como permiso de publicación bajo MIT. **Antes de publicar o proponer una PR que incluya esas adaptaciones, el propietario debe confirmar autoría y licencia compatible.** La licencia original de la base se conserva sin atribuirle la autoría del rescate. Ningún workflow debe publicar este desarrollo automáticamente; el de PyPI requiere una habilitación expresa adicional y la revisión de licencias.

Para un fork propio basta el código público base y este diff revisado: no añadir el ZIP, el inventario privado del rescate ni su historial. La configuración generada y SQLite se guardan fuera del checkout. El bundle de ejecución no contiene el entorno de desarrollo ni resultados de cuentas.
