---
term_id: demo-iiif-manifest
title: "Manifiesto IIIF"
related_terms: demo-iiif, demo-iiif-tiles
---

Un manifiesto IIIF es un archivo [JSON-LD](https://json-ld.org/) que describe una o más imágenes y sus metadatos según la especificación de la [IIIF Presentation API](https://iiif.io/api/presentation/). El manifiesto funciona como una "receta" que le indica a visores y herramientas compatibles con IIIF, como Telar, qué imágenes están disponibles, cómo están organizadas y cómo mostrarlas.

En términos técnicos, un manifiesto incluye varios componentes clave: metadatos del objeto (título, descripción, atribución, derechos, licencia), una secuencia de "lienzos" (cada uno representa una página, vista o superficie) y anotaciones que vinculan esos lienzos con recursos de imagen entregados por un servidor que use la Image API de IIIF.

Cuando proporcionas a Telar (o a cualquier visor IIIF) la URL de un manifiesto, la aplicación obtiene este archivo JSON, lee sus datos estructurados para entender qué imágenes hay disponibles y luego solicita teselas de imagen en los tamaños apropiados a medida que la persona lectora hace paneo y zoom.

Como los manifiestos siguen un formato estandarizado, cualquier visor IIIF puede usarlos sin importar qué institución los creó; ese es el valor central de IIIF.

**Más información:**
- [Especificación de la IIIF Presentation API 3.0](https://iiif.io/api/presentation/3.0/)
- [IIIF Cookbook: recetas y ejemplos de manifiestos](https://iiif.io/api/cookbook/)
