# Clase 16 · Hallazgos de StudyMatch

| Principio | Problema original | Mejora | Estado |
| --- | --- | --- | --- |
| Fitts | Los enlaces del panel tienen poca área clicable. | Usar botones más grandes. | Pendiente |
| Hick | Sin filtros, había que revisar todas las tarjetas. | Filtrar por materia, modalidad y fecha. | Resuelto en el trabajo anterior |
| Carga cognitiva | Las tarjetas no mostraban si las inscripciones estaban abiertas o cerradas. | Ahora muestran ese estado. | Corregido |

**Elegido:** carga cognitiva. Ahora se puede saber si una sesión admite inscripciones leyendo su tarjeta.

**Evidencia original:** [Antes](evidencias/clase-16/antes.png). La imagen corresponde al listado anterior a los filtros.

**Después:** [Ver captura](evidencias/clase-16/despues.png).

**Archivo modificado:** [SesionsPage.jsx](../frontend/src/SesionsPage.jsx), estado de inscripciones en las tarjetas.
