---
term_id: demo-iiif-tiles
title: "Teselas IIIF"
related_terms: demo-iiif, demo-iiif-manifest
---

Las teselas IIIF son segmentos pequeños y cuadrados de una imagen, es decir, teselas (*tiles*), que por lo general miden 256 px × 256 px o 512 px × 512 px y se organizan en una estructura de pirámide multirresolución. Esto permite paneo y zoom fluidos en imágenes grandes y de alta resolución en la web. Este enfoque, conocido como "[deep zoom](https://en.wikipedia.org/wiki/Deep_Zoom)" o "pirámides teseladas", resuelve un reto clave: las fotografías o escaneos en alta resolución pueden ser demasiado pesados para descargarse y mostrarse de una sola vez.

El sistema de teselado crea varias versiones de la imagen original en diferentes resoluciones (una pirámide) y divide cada nivel en una cuadrícula de teselas. Cuando un visor muestra la imagen, solo solicita las teselas necesarias para la vista y el nivel de zoom actuales.

Es la misma tecnología que usa [Google Maps](https://en.wikipedia.org/wiki/Google_Maps): no descargas todo el mapa del mundo para ver tu barrio. El estándar [Image API](https://iiif.io/api/image/) de IIIF normaliza cómo solicitar esas teselas.

Cuando Telar genera teselas IIIF a partir de tus imágenes locales, crea esa pirámide de manera automática y produce miles de teselas individuales desde una sola fotografía o escaneo.

**Más información:**

- [Especificación de la IIIF Image API](https://iiif.io/api/image/3.0/)
- [Deep Zoom en Wikipedia](https://en.wikipedia.org/wiki/Deep_Zoom)
