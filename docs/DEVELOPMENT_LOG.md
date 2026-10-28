# Desarrollo y publicación de esta rama

## Estado inicial inspeccionado

El checkout ya era un repositorio Git, clonado directamente del repositorio público Macfly. Conservaba 38 commits hasta `3295bba51b4719e947b501e7dbb809b8e3708572`, con `origin` apuntando a Macfly. No había un desarrollo Outlook posterior en el espacio de trabajo inspeccionado. El rescate se examinó fuera de este checkout; no se importó su Git ni otros componentes.

No se reinició el proyecto ni se cambió de base. La rama de implementación es `feature/account-bound-drafts`. Se conserva la autoría histórica de upstream; los commits locales nuevos usan la identidad GitHub del propietario y dirección noreply, configurada solo en este repositorio.

## Commits locales guardados

- `a616b30`: selección SMTP exacta, PROPERTYPUTREF y validez estricta de borradores/DeliveryStore; procedencia del código.
- `91fe218`: solo reintentar operaciones declaradas de lectura, con pruebas del puente.
- `d3db792`: adaptadores de borradores reales, política local de contenido, catálogo de correo y pruebas simuladas/stdio.
- `9e5c746`: compatibilidad de instantánea con ConversationIndex devuelto como cadena COM.
- `564ec3b`: instalación por usuario desde wheel, dependencias fijadas, preparación revisable de config, pruebas y CI.
- `3081956`: guía de instalación, portabilidad, límites y propuestas upstream.
- `0fc70ea`: usar exactamente los mismos bytes para guardar y verificar el hash de config en Windows; la prueba detectó la diferencia CRLF/LF antes de aplicar nada al usuario.

Los siguientes commits documentan la revisión de publicación y cualquier resultado final. `git log --oneline feature/account-bound-drafts` es el registro completo; no se hacen squash, force-push ni reescrituras del historial remoto.

## Validación realizada antes de publicar mejoras

La suite de pruebas es simulada: incluye COM con dobles, ledger local, contratos, stdio y preservación de config. La prueba real autorizada solo arrancó MCP y enumeró herramientas y cuentas de Outlook; no leyó mensajes, creó borradores ni envió correo. Los resultados de cuentas y rutas locales no se guardan aquí. No se equipara CI Windows con integración real de Outlook.

`scripts/review_git_history.py` revisa los blobs alcanzables desde HEAD, nombres de archivos y patrones de secretos antes de cada push. Se revisan también los archivos seleccionados mediante Git. No se suben otras ramas, tags ni reflogs. El historial público conserva los metadatos de sus autores y las ilustraciones originales; no se añade historial privado del rescate.

## Remoto autorizado

El propietario autorizó expresamente un fork **público**, tras aclarar que GitHub no permite hacer privado un fork de ese upstream público. Fork: `https://github.com/teajunopeas/outlook-classic-com-mcp`, padre `macfly1202/outlook-classic-mcp`.

Macfly se conserva como remoto `upstream`; `origin` se destina al fork. Solo se sube la rama `feature/account-bound-drafts`. No se abre una PR al original ni se publican paquetes en PyPI. Las protecciones actuales son comprobaciones locales; la autorización humana independiente queda pendiente.

La creación del fork copia el historial público base en GitHub. Los pushes de mejoras se registran por commit y referencia remota comprobada. Si el SHA de la rama remota coincide con el HEAD local, ese avance está publicado; una etiqueta narrativa no sustituye esa comprobación.
