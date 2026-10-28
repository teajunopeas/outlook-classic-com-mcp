# Propuestas pequeñas para revisión, todavía sin publicar

Todas se prepararían contra la revisión vigente del mantenedor, conservando sus cambios posteriores. No se ha creado un fork remoto, push ni PR. Las adaptaciones del rescate requieren confirmar licencia antes de publicarlas.

## 1. Selección y verificación explícita de remitente

Problema: al crear/enviar una respuesta o un correo con varias cuentas, Outlook puede utilizar la cuenta predeterminada y no la solicitada.

Cambio propuesto: parámetro SMTP explícito, selección única, DeliveryStore y asignación SendUsingAccount por PROPERTYPUTREF. Comprobar lectura posterior y después de Save; rechazar cambio de cuenta, cuenta no disponible y delegado no aprobado. No introducir fallback.

Validación: dobles COM para PROPERTYPUTREF, cuenta ambigua/no encontrada, cuenta cambiada por Save y delegado. Pendiente comprobar composición/envío con Outlook real y permiso específico del usuario.

Límites: DeliveryStore compartidos y cuentas delegadas necesitan diseño específico; no admitirlos por heurística. Esta propuesta no incorpora el protocolo local de aprobación.

## 2. Validación estricta de borradores

Problema: comprobar solamente Sent=False también acepta elementos que no son borradores válidos.

Cambio propuesto: exigir MailItem, Saved, EntryID, no Sent/Submitted y pertenencia a la carpeta real Drafts del DeliveryStore elegido. Mantener edición por EntryID y native Reply/Forward. Invalidar aprobaciones si el cliente tiene esa función, sin exigirla a upstream.

Validación: elementos recibidos no enviados, citas, mensajes pendientes de Outbox, elementos no guardados y stores ajenos; edición del mismo borrador con mocks. Pendiente prueba real autorizada.

## 3. Reintentos según efectos de la operación

Problema: un error RPC no demuestra que Send o Save no haya ocurrido; repetirlos puede duplicar mensajes o borradores.

Cambio propuesto: permitir reconexión/reintento únicamente para operaciones marcadas explícitamente de lectura. Toda escritura y función desconocida falla sin repetición. Documentar que un timeout no cancela COM.

Validación: fallo de desconexión en lectura reintenta una vez; escritura/desconocida ejecuta una sola vez. No enviar correos reales para demostrarlo.

## Adaptación local que no propondría como requisito upstream

El catálogo de doce herramientas, el ledger SQLite de revisión de contenido y los instaladores específicos de esta distribución son política local. No obligar al mantenedor a adoptar todas esas decisiones en una PR de remitentes o reintentos.
