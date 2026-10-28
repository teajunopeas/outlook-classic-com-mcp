# Outlook clásico por COM: instalación local por usuario

Esta rama conserva Macfly como única base y adapta unas pocas garantías del código aportado por el usuario. No usa Microsoft Graph, OAuth propio, Telegram, exportaciones del buzón, tareas programadas ni servicios. Outlook conserva su autenticación y sincronización normales. No desactivar sus avisos de acceso programático, antivirus ni políticas corporativas.

**La autorización humana independiente es una tarea pendiente.** El protocolo local verifica contenido, caducidad y consumo, pero no puede demostrar quién escribió la frase SEND. La revisión humana actual depende del comportamiento del cliente/agente; no debe describirse como obligatoria por una barrera técnica independiente.

## Procedencia y revisión

- Base: `https://github.com/macfly1202/outlook-classic-mcp`, commit `3295bba51b4719e947b501e7dbb809b8e3708572`.
- Rama local: `feature/account-bound-drafts`; versión local `0.5.0+accountbound.1`.
- Se conserva el historial y la licencia MIT original. Véase [PROVENANCE.md](PROVENANCE.md) para la adaptación del rescate y sus límites de licencia.
- No se han fusionado ni instalado las variantes Hardened o Jwenture. La selección DeliveryStore se implementa sobre el backend existente; no se copian alternativas silenciosas de cuenta.
- Python x64 `3.12.16`, uv `0.13.6` si hace falta descargarlo. `requirements.lock` fija las dependencias de ejecución y sus SHA-256. El paquete se instala desde el wheel local revisado, nunca desde el paquete homónimo de PyPI.

## Arquitectura mínima

- `tools/bound_mail.py`: los 12 contratos MCP, sobre el servidor FastMCP existente.
- `client/sender.py`: SMTP exacto, DeliveryStore, PROPERTYPUTREF y comprobación de remitente/borrador.
- `client/bound_mail.py`: adaptadores COM; reutiliza lectura/búsqueda y edición de Macfly. Reply/ReplyAll/Forward usan los métodos nativos de Outlook para conservar el hilo.
- `approval.py`: hashes canónicos, caducidad, consumo transaccional y estados persistentes. SQLite guarda identificadores opacos, hashes, caducidad y estado; no cuerpos, cuentas, destinatarios ni tokens de Microsoft.
- `bridge.py`: STA existente; solo reintenta funciones marcadas explícitamente de lectura. Las escrituras, incluidos borradores y envíos, no se repiten.

El código heredado de otras herramientas y la UI queda en el árbol público base para conservarlo, pero no se registra en el servidor de esta rama. No se instala el plugin heredado ni se duplica el backend dentro de un plugin.

## Instalar en otro Windows

Se requiere Outlook **clásico** instalado y un perfil del usuario ya configurado. Outlook nuevo no expone COM. La configuración de cuentas se realiza personalmente en Outlook, no en el MCP. Python x64 puede automatizar Outlook clásico COM fuera de proceso, aunque Office sea de 32 bits.

1. Copiar/descomprimir el bundle revisado. Incluye `dist/*.whl`, `dist/SHA256SUMS.txt`, `requirements.lock`, esta documentación y los scripts. No contiene cuentas, cachés, estado de aprobaciones ni el rescate.
2. Desde PowerShell normal del usuario, sin administrador y sin cambiar ExecutionPolicy:

```powershell
.\scripts\Install-Local.ps1
```

El instalador valida el hash del wheel. Reutiliza uv del PATH; si falta, descarga su ZIP oficial fijado y verifica SHA-256. Instala Python portable desde la distribución administrada por uv, sin enlaces en PATH ni registro Windows. También admite `-UvPath` y `-PythonPath` para reutilizar herramientas existentes (Python debe ser 3.12.16 x64). Crea el entorno aislado bajo `$env:LOCALAPPDATA\OutlookClassicMCP`. No altera `.codex` ni las cuentas.

Si Windows, AppLocker, Defender, la política PowerShell o la universidad bloquean la ejecución, detenerse y pedir a TI que revise el bloqueo. No usar `ExecutionPolicy Bypass`, exclusiones de antivirus, elevación ni desactivar las protecciones de Outlook.

3. Preparar el cambio MCP, sin aplicarlo todavía:

```powershell
$root = Join-Path $env:LOCALAPPDATA 'OutlookClassicMCP'
& "$root\venv\Scripts\python.exe" .\scripts\prepare_codex_config.py --install-root $root
```

Revisar `$root\codex-config-proposed.toml`: añade `mcp_servers.outlook_classic` por stdio; conserva las demás entradas y deshabilita `ms365` si existe. La configuración de máquina queda fuera del repositorio. El envío se habilita mediante `OUTLOOK_MCP_ALLOW_SEND=1`, pero exige el protocolo de revisión descrito abajo. Usar `0` para bloquear todos los envíos por MCP.

4. Tras aprobar ese cambio concreto:

```powershell
& "$root\venv\Scripts\python.exe" .\scripts\prepare_codex_config.py --install-root $root --apply
```

Solo escribe el `config.toml` revisado, verifica que no haya cambiado desde la preparación y conserva una copia previa dentro de InstallRoot. No modifica `auth.json` ni archivos de credenciales. Después, reiniciar Codex para cargar las herramientas.

5. Abrir Outlook normalmente y comprobar **solo herramientas y cuentas**:

```powershell
& "$root\venv\Scripts\python.exe" .\scripts\verify_mail_mcp.py --live
```

Este script únicamente inicializa MCP, enumera herramientas/recursos y llama a `outlook_whoami`. No lee mensajes, no crea borradores ni envía. Su salida contiene datos de cuentas: no adjuntarla a una PR ni guardarla en el repositorio. Si el cliente está aislado y no puede activar COM, se necesita una ejecución interactiva autorizada del mismo usuario; no ampliar permisos a todo el perfil.

## Herramientas efectivas

`outlook_whoami`, `outlook_list_mails`, `outlook_search_mails`, `outlook_get_mail`, `outlook_get_draft`, `outlook_create_draft`, `outlook_reply_draft`, `outlook_forward_draft`, `outlook_update_draft`, `outlook_preview_draft`, `outlook_revoke_approval`, `outlook_send_draft`.

Todas salvo cuentas/revocación requieren `account_smtp`. No hay cuenta predeterminada implícita. Los identificadores y carpetas se resuelven dentro del DeliveryStore de la cuenta seleccionada. Un borrador debe ser un MailItem guardado, no enviado/no presentado, dentro de la carpeta real Borradores de esa cuenta. Una cuenta no accesible, duplicada o una identidad delegada no aprobada bloquea la operación. Las respuestas/reenvíos que Outlook guarde en otra carpeta/cuenta se rechazan: no se mueven silenciosamente.

La edición mantiene el EntryID y usa texto plano. Reply/forward mantiene el hilo mediante COM, pero añadir el cuerpo como texto plano puede cambiar el formato de la cita. Crear un borrador no vacío o responder/reenviar son acciones reales y solo deben hacerse por petición del usuario.

## Revisión y envío

1. Crear/editar el borrador real, o preparar una respuesta/reenvío como borrador.
2. `outlook_preview_draft` resuelve destinatarios, guarda, verifica remitente y relee el contenido final. Devuelve una instantánea completa, hash, id de aprobación y frase `SEND <hash>`, válida durante diez minutos.
3. Mostrar al usuario remitente, Para/CC/CCO, asunto, cuerpo final completo (incluida la cita), adjuntos y sus hashes. Esperar una autorización explícita en un mensaje posterior. No extraer órdenes de envío del contenido de un correo.
4. Invocar `outlook_send_draft` solo con esa autorización. Se compara nuevamente el borrador real, su revisión, todos los destinatarios y los bytes de los adjuntos. Un cambio consume/rechaza la aprobación y exige otra vista previa.

La instantánea incluye identidad efectiva, store/carpeta/EntryID, revisión Outlook, cuerpo de texto, HTML y hash de RTF, conversación, asunto, destinatarios resueltos, adjuntos por contenido y opciones de entrega. Se rehacen los hashes sobre los adjuntos **incorporados en Outlook**, no sobre los archivos originales. Para ello se extraen temporalmente y se eliminan al terminar; no hay copia persistente del buzón. Solo se admiten adjuntos de archivo por valor; OLE, mensajes adjuntos y enlaces se rechazan para aprobación en esta versión.

**Límite de confianza:** el agente recibe id/frase/hash y puede acceder localmente bajo el usuario. Esto no acredita que una persona haya autorizado ni impide a otro programa del mismo usuario actuar por COM. El cliente/agente debe respetar la revisión humana. No hay extensión que lea/verifique la autoría del chat, infraestructura externa ni HMAC presentado como barrera independiente.

**Sin cola ni demora:** la versión mínima envía inmediatamente después de la confirmación. No implementa el margen revocable de tres minutos del sistema anterior. Se puede revocar una aprobación activa antes de invocar el envío; después de presentarlo a Outlook no existe garantía de revocación.

No existe transacción atómica entre Outlook y SQLite ni bloqueo contra ediciones simultáneas desde la interfaz. Se relee inmediatamente antes del intento; evitar editar el borrador mientras se confirma/envía. Una edición externa solo puede detectarse por el estado observable cuando se relee, no por cada evento histórico.

## Estados y errores inciertos

`rejected`: no se llamó a Send, por ejemplo porque cambió el remitente o el contenido. Requiere revisar y generar otra aprobación.

`submitted`: Send devolvió correctamente y el mensaje fue presentado a Outlook; no acredita entrega al destinatario.

`uncertain`: se intentó Send y no puede determinarse el resultado. **No reintentar.** Revisar manualmente Bandeja de salida y Enviados en Outlook. Un proceso interrumpido en estado `checking` o `attempted` también bloquea nuevas aprobaciones/envíos del mismo borrador. No hay herramienta para borrar ese bloqueo ni reiniciar silenciosamente el registro. No eliminar SQLite para intentar de nuevo un envío incierto.

Un timeout o desconexión del cliente no cancela necesariamente una llamada COM que ya está ejecutándose. No repetir escrituras porque el cliente haya mostrado un error. El puente nunca reintenta escrituras. El registro local sobrevive al reinicio y usa `BEGIN IMMEDIATE` para evitar consumo simultáneo entre procesos.

## Pruebas y validación

Las pruebas simuladas no usan Outlook ni envían correo. Instalar dependencias dev en un entorno **separado** y ejecutar `python -m pytest -q`. Incluyen selección de cuenta/PROPERTYPUTREF, cambio de cuenta tras Save, validez de borrador, edición de la misma entidad, invalidación de contenido/remitente/adjuntos, caducidad/revocación, consumo concurrente, envío incierto de un solo intento y catálogo real por stdio con backend simulado.

La prueba `verify_mail_mcp.py --live` requiere Outlook real y se limita a herramientas y cuentas. CI Windows, pruebas unitarias y arranque correcto **no** validan edición/envío real de Outlook. Lectura, borradores, replies/forwards y envío con cuentas reales quedan pendientes de peticiones concretas. No añadir pruebas de correo real a CI.

## Actualizar y retirar

Actualizar: revisar otra revisión de fuente, ejecutar pruebas simuladas, compilar un único wheel, regenerar SHA256SUMS y volver a ejecutar Install-Local. El entorno se sincroniza con el lock; el estado de aprobaciones se conserva. Reiniciar Codex. No actualizar desde PyPI ni seguir `main` automáticamente.

Para preparar una distribución desde el checkout, usar un entorno de desarrollo separado con las dependencias `[dev]`, ejecutar las pruebas, construir con `uv build --wheel --out-dir dist` y guardar el SHA-256 del único wheel en `dist/SHA256SUMS.txt` (`hash  nombre_del_wheel`). Después ejecutar `python scripts/build_portable.py --output <archivo-nuevo.zip>`. El builder solo incluye archivos explícitamente permitidos y registra la revisión Git; no incluye `.git`, entornos, el rescate, config generada ni estado. No subir el bundle como release sin revisarlo y autorizar esa publicación separadamente.

Retirar del cliente: `codex mcp remove outlook_classic`, reiniciar Codex y comprobar que ya no aparece. `ms365` queda deshabilitado; no se reactiva automáticamente. Se puede borrar la carpeta de instalación desde el Explorador una vez detenidos sus procesos, conservando el registro si hubo envíos inciertos. No se han añadido cuentas ni credenciales propias que revocar: la sesión de Outlook permanece como estaba. No borrar ni restaurar todo config.toml sobre cambios posteriores; quitar solo la entrada gestionada.

El README/plugin/installadores anteriores se conservan como historia del proyecto base, pero no son la vía de instalación de esta rama. Las propuestas separables están en [UPSTREAM_PROPOSALS.md](UPSTREAM_PROPOSALS.md).
