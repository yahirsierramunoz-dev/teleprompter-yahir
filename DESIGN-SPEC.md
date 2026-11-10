# DESIGN-SPEC · Sistema visual "Orvex" (Teleprompter Yahir / Nexa IA Studio)

> Guía de diseño + prompt maestro reutilizable. Todo lo que está aquí fue extraído del código real de la app (`index.html`), no inventado. Los valores son exactos y se pueden copiar tal cual.

## 0. Referencias (dónde mirar)

| Qué | Enlace |
|---|---|
| App en vivo (abrir en celular o en ventana de 390×844) | https://yahirsierramunoz-dev.github.io/teleprompter-yahir/ |
| Código fuente completo (todo el CSS está en un solo `<style>`) | https://github.com/yahirsierramunoz-dev/teleprompter-yahir/blob/main/index.html |
| Código fuente en texto plano (mejor para que una IA lo lea) | https://raw.githubusercontent.com/yahirsierramunoz-dev/teleprompter-yahir/main/index.html |
| Este documento | https://github.com/yahirsierramunoz-dev/teleprompter-yahir/blob/main/DESIGN-SPEC.md |
| Generador del ícono de galaxia | `tools/galaxy-icon/generate_icon.py` (mismo repo) |

**Cómo leer el código:** las secciones del CSS se localizan por sus comentarios, no por número de línea (cambian). Busca estos marcadores en `index.html`:
`:root{`, `/* ===== ORVEX: botones estilo iPhone (iOS) ===== */`, `/* ===== ORVEX: botones redondos tipo cristal 3D`, `/* los botones conservan el color metálico del tema */`, `/* acabado metálico facetado`, `/* ===== MODO BUSINESS`, `/* modo lectura fluida`. Los temas de color están en `const THEMES`, y las gemas de selección de color en `window.renderThemes`.

**Nota para IAs que no ejecutan JavaScript:** la app es una PWA hecha con JS; si no puedes renderizarla, lee el código fuente (enlace raw) y reproduce los valores de este documento. Si sí puedes abrirla, usa viewport móvil 390×844 y abre Ajustes (icono de sliders arriba a la derecha) para ver botones, interruptores, selector segmentado y gemas.

---

## 1. La receta en un párrafo

Fondo casi negro con un tinte del color del tema → texto blanco-azulado con degradado metálico → controles de **cristal teñido con bisel metálico** (tres capas de degradado + luz interna arriba + sombra interna abajo + resplandor de color debajo) → todo con curvas de animación tipo iOS (`cubic-bezier(.32,.72,0,1)`) y feedback al tocar (escala .93–.97). El 90 % del look "premium/futurista" sale de **un solo color de acento por tema** del que se derivan los demás (claro, oscuro, fondo, resplandor, línea).

Principios que se repiten en cada componente:
1. **Un color de acento + uno claro (`hi`) + uno oscuro (`accent2`)**: con esos tres se pinta todo el metal.
2. **Luz arriba, sombra abajo**: borde superior blanco brillante (inset 1.5px) y sombra interna oscura abajo (inset −2.5px). Esa asimetría es lo que da el volumen 3D.
3. **Resplandor de color, no sombra negra**: debajo de los botones primarios va `0 10px 22px -8px var(--accent)` (el negativo de spread mantiene el glow pegado al botón).
4. **Vidrio**: `backdrop-filter: blur(14–30px) saturate(1.5–1.7)` sobre superficies translúcidas, con borde de 1px blanco al 10–28 %.
5. **Texto con degradado** para títulos y guion (blanco → color metálico), nunca texto plano en los elementos protagonistas.

---

## 2. Tokens de diseño (variables CSS reales)

```css
:root{
  --bg:#05060b; --fg:#f2f5fb; --muted:#8b93a7;
  --accent:#6ee7ff; --accent2:#8b7bff; --soft:rgba(110,231,255,.10); --on:#04121a;
  --glass:rgba(255,255,255,.055); --glass2:rgba(255,255,255,.09); --line:rgba(255,255,255,.10);
  --glow1:rgba(94,110,255,.20); --glow2:rgba(0,229,255,.11);
  --hi:#d7faff; --metal:#9fb0cf;
  --grad:linear-gradient(135deg,var(--hi) 0%,var(--accent) 44%,var(--accent2) 100%);
  --mbg:linear-gradient(180deg,rgba(255,255,255,.38),rgba(255,255,255,0) 52%,rgba(0,0,0,.18)),linear-gradient(135deg,var(--hi) 0%,var(--accent) 44%,var(--accent2) 100%);
  --edge:inset 0 1px 0 rgba(255,255,255,.55),inset 0 -2px 4px rgba(0,0,0,.28);
  --font:-apple-system,BlinkMacSystemFont,"SF Pro Display","Segoe UI",Roboto,"Helvetica Neue",sans-serif;
  --wght:700; --lh:1.28; --ls:-.02em;
  --panel:#12141c;
  --ease:cubic-bezier(.32,.72,0,1);      /* curva "iOS": arranque rápido, frenado suave */
  --spring:cubic-bezier(.34,1.45,.64,1); /* rebote ligero (interruptores, gemas) */
}
```

Significado de cada token:

| Token | Rol |
|---|---|
| `--bg` | Fondo. Casi negro con tinte del color del tema (ej. `#05060b` azulado, `#0c0801` dorado). |
| `--fg` | Texto principal (blanco ligeramente frío `#f2f5fb`). |
| `--muted` | Texto secundario/etiquetas. |
| `--accent` | Color protagonista del tema. |
| `--hi` | Versión muy clara del acento: brillo especular, inicio de degradados. |
| `--accent2` | Versión oscura/profunda del acento: final de degradados. |
| `--on` | Color del texto **sobre** el acento (oscuro si el acento es claro, blanco si es oscuro). |
| `--soft` | Acento al 10–15 % de opacidad: fondos suaves, resaltados. |
| `--line` | Bordes finos. En temas de color = acento al 20 %; en la base = blanco al 10 %. |
| `--glass` / `--glass2` | Blanco al 5 % / 9 %: superficies de vidrio. |
| `--glow1` / `--glow2` | Dos resplandores de ambiente (acento al 22 % y 10 %) que van en la esquina superior del fondo. |
| `--metal` | Color final del degradado del texto del guion (en temas de color = `hi`). |

### 2.1 Fondo ambiental

```css
body::before{content:"";position:fixed;inset:0;pointer-events:none;z-index:0;
  background:radial-gradient(120% 55% at 12% -8%,var(--glow1),transparent 62%),
             radial-gradient(90% 45% at 112% 2%,var(--glow2),transparent 58%)}
```
Dos manchas de luz de color que entran por las esquinas superiores sobre el negro. Es lo que evita que el fondo se vea plano.

---

## 3. Colores y temas

### 3.1 Anatomía de un tema

Un tema se define con **7 valores**: `[nombre, acento, brillo(hi), sombra(accent2), fondo(bg), texto-sobre-acento(on)]`. Todo lo demás se calcula:

```js
const c = acento→"r,g,b";
soft  = rgba(c,.13)   line = rgba(c,.20)   glow1 = rgba(c,.22)   glow2 = rgba(c,.10)
glass = rgba(255,255,255,.05)   glass2 = rgba(255,255,255,.085)
fg = #f4f7fb   muted = #8d96a8   metal = hi
```

### 3.2 Paleta completa (valores reales)

| Tema | Acento | Brillo `hi` | Sombra `accent2` | Fondo `bg` | `on` |
|---|---|---|---|---|---|
| Obsidiana (base) | `#6ee7ff` | `#d7faff` | `#7a6bff` | `#05060b` | `#04121a` |
| Guinda | `#d3144a` | `#ff9fb6` | `#6e0b28` | `#0c0308` | `#fff0f4` |
| Dorado | `#d4a43c` | `#fff1c2` | `#7a5212` | `#0c0801` | `#1a1200` |
| Verde | `#19e06a` | `#c9ffd9` | `#067a35` | `#020c06` | `#02150a` |
| Azul | `#3a74ff` | `#c3d6ff` | `#0b2fa8` | `#030612` | `#ffffff` |
| Morado | `#8a2be2` | `#dcb8ff` | `#38087a` | `#06020d` | `#ffffff` |
| Rosa | `#ff4fa8` | `#ffc2e0` | `#9c1664` | `#0d0309` | `#ffffff` |
| Rojo | `#ff2f43` | `#ffb8bf` | `#8a0716` | `#0d0306` | `#ffffff` |
| Amarillo | `#ffd21f` | `#fff5b8` | `#b57a00` | `#0a0800` | `#1a1200` |
| Naranja | `#ff8a1f` | `#ffd9ad` | `#a64a00` | `#0c0602` | `#1a0c00` |
| Café | `#b5763a` | `#f2d3a8` | `#4a2a12` | `#0c0704` | `#ffffff` |
| Blanco | `#eef2f8` | `#ffffff` | `#9aa6ba` | `#07080b` | `#0a0d14` |
| Gris | `#9aa4b6` | `#e6ebf3` | `#4a5365` | `#060708` | `#0a0d14` |

Texto y glass de Obsidiana: `fg #f2f5fb`, `muted #8b93a7`, `metal #9fb0cf`, `glow1 rgba(94,110,255,.20)`, `glow2 rgba(0,229,255,.11)`.

### 3.3 Cómo crear un tema nuevo a partir de un solo color (patrón observado en la tabla)

1. **accent**: el color de marca, saturado y luminoso.
2. **hi**: el mismo tono mezclado ~70–80 % hacia blanco (ej. `#19e06a` → `#c9ffd9`).
3. **accent2**: el mismo tono oscurecido a ~35–50 % de luminosidad, saturación alta (ej. `#19e06a` → `#067a35`). Excepción: en Obsidiana es un violeta (`#7a6bff`) para dar un degradado cian→violeta; úsalo si quieres un degradado de dos tonos.
4. **bg**: el mismo tono a ~3–5 % de luminosidad (casi negro con tinte).
5. **on**: si el acento es claro/brillante (dorado, verde, amarillo, naranja, blanco, gris) → casi negro con tinte (`#1a1200`); si es oscuro/saturado (azul, morado, rosa, rojo, café) → `#ffffff`.

### 3.4 Combinación de colores (reglas de uso)

- El degradado de marca es siempre `135deg: hi 0% → accent 44% → accent2 100%`.
- Texto del guion y títulos: `linear-gradient(180deg, var(--fg) 0%, var(--fg) 34%, var(--metal) 100%)` recortado al texto.
- Nunca más de **un** color de acento visible a la vez; los demás son neutros (blanco al 5–28 %, negro).
- Verde de estado ok `#4ade80` (con glow) y ámbar `#fbbf24` (aviso) son los únicos colores fijos fuera del tema; el interruptor encendido usa verde iOS `#34c759`.
- Oro "Nexa IA Studio" (créditos y logotipos de productos) es independiente del tema: `#8a6420 · #e9c46a · #fff1c2 · #d4a43c · #fbe7a1 · #a47a24` (ver §6.10).

### 3.5 Modo Business (alternativa sobria, mismo código)

Misma estructura pero **plano**: sin glow, sin metal, sin blur; `--mbg`/`--grad` pasan a ser el color sólido del acento y `--edge:none`. Temas: grafito, marfil, marino, pizarra, bosque, burdeos (cada uno `[bg, fg, muted, acento, on, line, panel, glass, glass2]`). Úsalo cuando el entregable deba verse corporativo/serio en vez de futurista.

---

## 4. Botones 3D metálicos estilo Apple (la receta exacta)

El botón se construye con **tres degradados apilados + borde claro + luz interna + sombra interna + glow de color**. Estas son las variables reales (versión final, la que sobreescribe a las anteriores):

```css
/* PRIMARIO (teñido): play, "Listo", botón de acción, botón de tarjeta, pulgar del segmentado, chip/idioma/video seleccionado */
--lg-tint:
  linear-gradient(115deg,transparent 36%,rgba(255,255,255,.42) 45%,rgba(255,255,255,.1) 55%,transparent 64%),   /* 1. franja especular diagonal */
  linear-gradient(180deg,rgba(255,255,255,.62) 0%,rgba(255,255,255,.16) 47%,rgba(255,255,255,0) 50%,rgba(0,0,0,.16) 100%), /* 2. horizonte cromado: mitad superior clara, corte duro en 50 %, mitad inferior oscura */
  linear-gradient(160deg,var(--hi) 0%,var(--accent) 34%,var(--accent2) 66%,color-mix(in srgb,var(--accent) 78%,var(--hi)) 100%); /* 3. cuerpo de color */
--lg-tedge:
  inset 0 1.5px 0 rgba(255,255,255,.9),        /* luz en el borde superior */
  inset 0 -2.5px 3px rgba(0,0,0,.32),          /* sombra interna inferior = volumen */
  inset 1px 0 1px rgba(255,255,255,.35),       /* bisel izquierdo claro */
  inset -1px 0 1px rgba(0,0,0,.18),            /* bisel derecho oscuro */
  0 10px 22px -8px var(--accent);              /* glow de color debajo */

/* SECUNDARIO (cristal teñido, translúcido): atrás, ajustes, − y +, botones de modo línea, pantalla completa */
--lg-bg:
  linear-gradient(115deg,transparent 36%,rgba(255,255,255,.3) 45%,rgba(255,255,255,.06) 55%,transparent 64%),
  linear-gradient(180deg,rgba(255,255,255,.38) 0%,rgba(255,255,255,.08) 47%,rgba(255,255,255,0) 50%,rgba(0,0,0,.14) 100%),
  linear-gradient(160deg,color-mix(in srgb,var(--hi) 72%,transparent) 0%,color-mix(in srgb,var(--accent) 46%,transparent) 34%,color-mix(in srgb,var(--accent2) 68%,transparent) 66%,color-mix(in srgb,var(--accent) 52%,transparent) 100%);
--lg-edge:
  inset 0 1.5px 0 rgba(255,255,255,.85),inset 0 -2.5px 3px rgba(0,0,0,.34),
  inset 1px 0 1px rgba(255,255,255,.3),inset -1px 0 1px rgba(0,0,0,.16),
  0 10px 20px -8px color-mix(in srgb,var(--accent) 70%,#000);
```

### 4.1 Aplicación

```css
/* secundario */
.btn-glass{
  background:var(--lg-bg);
  border:1px solid rgba(255,255,255,.28);
  box-shadow:var(--lg-edge);
  backdrop-filter:blur(14px) saturate(1.6);-webkit-backdrop-filter:blur(14px) saturate(1.6);
  color:var(--fg); text-shadow:0 1px 2px rgba(0,0,0,.4);
  border-radius:999px;                /* píldora; 50 % si es circular */
  transition:transform .4s var(--ease),filter .2s;
}
/* primario */
.btn-tint{
  background:var(--lg-tint);
  border:1px solid rgba(255,255,255,.28);
  box-shadow:var(--lg-tedge);
  color:var(--on); text-shadow:0 1px 0 rgba(255,255,255,.28);   /* grabado: luz 1px debajo del texto */
  border-radius:999px;
}
.btn-glass:active,.btn-tint:active{ filter:brightness(1.12–1.25); transform:scale(.93–.94); transition-duration:.12s }
```

### 4.2 Por qué se ve 3D y premium (qué hace cada capa)

| Capa | Efecto visual |
|---|---|
| Franja diagonal 115° (blanco .42 entre 36 % y 64 %, pico en 45 %) | Reflejo especular de metal pulido: una "raya de luz" que cruza el botón. |
| Degradado vertical con **corte duro en 47 %→50 %** | "Horizonte cromado": la mitad superior es clara, la inferior oscura, como cromo o vidrio curvo. El corte brusco (de .16 a 0 en 3 %) es la clave: sin él se ve plástico. |
| Degradado 160° `hi → accent → accent2 → mezcla` (4 paradas) | Cuerpo metálico con un último reflejo de rebote (la parada final vuelve hacia el acento claro). |
| `inset 0 1.5px 0 blanco .9` | Filo de luz arriba: el borde "atrapa" la luz. |
| `inset 0 -2.5px 3px negro .32` | Grosor inferior: da altura al botón. |
| `inset 1px / -1px` laterales (claro izq., oscuro der.) | Bisel tipo moneda; luz viene de arriba-izquierda. |
| `0 10px 22px -8px accent` | Resplandor de color: el botón "emite" su color; el spread negativo lo mantiene debajo. |
| `text-shadow 0 1px 0 rgba(255,255,255,.28)` | Texto "grabado" sobre el metal. |
| `backdrop-filter` en el secundario | Es cristal: se ve lo de atrás desenfocado (solo cuando no hay scroll automático; ver §9). |

### 4.3 Formas y tamaños reales

| Componente | Forma | Tamaño |
|---|---|---|
| Botón Play | círculo (`50%`) | 76 × 76 px, ícono triángulo SVG |
| Botones − / + | círculo | 58 × 58 px, símbolo 28 px peso 300 |
| Atrás | píldora (`999px`) | altura 38–40 px, padding `0 14px 0 8px` |
| Ajustes (engranaje) / hgear | círculo | 38–42 px |
| Listo / acción primaria | píldora | altura 50 px, texto 16 px peso 700 |
| Botones modo línea | píldora | altura 54–58 px |
| Pantalla completa | píldora | padding 14 px |
| Botón de tarjeta (▶) | círculo | 38 × 38 px, solo color/teñido |

Contenedor de controles (barra inferior): `border-radius:36px; background:var(--glass); backdrop-filter:blur(26px) saturate(1.5); box-shadow:inset 0 1px 0 rgba(255,255,255,.06),0 20px 44px -18px rgba(0,0,0,.75)`.

### 4.4 Modo "botones iOS planos" (capa base previa)

Antes del cristal 3D, la base define botones al estilo iPhone: fondo `rgba(120,120,128,.24–.26)` (gris sistema iOS), sin borde, radio 14 px; primario sólido `var(--accent)` sin sombra. El cristal 3D de §4 **sobreescribe** esto en Orvex, pero este nivel es una buena variante "sobria" intermedia.

---

## 5. Acabado metálico (texto y superficies)

| Elemento | CSS real |
|---|---|
| Texto del guion (acabado "Metálico") | `background:linear-gradient(180deg,var(--fg) 0%,var(--fg) 34%,var(--metal) 100%); -webkit-background-clip:text; background-clip:text; color:transparent` |
| Título "Teleprompter" | `background:linear-gradient(180deg,var(--fg) 25%,var(--metal)); background-clip:text; color:transparent; font-size:30px; weight 700; letter-spacing:-.9px` |
| Títulos grandes de video (divisores) | `background:linear-gradient(180deg,#fff 0%,var(--hi) 22%,var(--accent) 58%,var(--accent2) 100%); background-clip:text; filter:drop-shadow(0 0 26px var(--accent)); font-weight:900; letter-spacing:.08em; text-transform:uppercase; font-size:min(calc(var(--size)*1.7),16vw)` |
| Contador de cuenta regresiva | `background:var(--grad); background-clip:text; font-size:38vw; weight 200; filter:drop-shadow(0 0 40px var(--accent))` |
| Oro de créditos (Nexa IA Studio) | `linear-gradient(100deg,#8a6420 0%,#e9c46a 22%,#fff1c2 38%,#d4a43c 52%,#fbe7a1 68%,#a47a24 84%,#e9c46a 100%)`, `background-size:220% 100%`, animación `goldSheen 7s` (mueve `background-position` 0 %↔100 %), fuente Playfair Display itálica 700 |
| Pulgar de sliders | `radial-gradient(circle at 35% 28%,#fff,#d9deea 60%,#aeb6c8)` + `box-shadow:0 3px 12px rgba(0,0,0,.6), inset 0 -2px 3px rgba(0,0,0,.2)` (esfera de aluminio) |

Reglas del metal: (1) el degradado siempre va **de claro arriba a oscuro/color abajo**; (2) un resplandor de color (`drop-shadow` o `box-shadow` con spread negativo) acompaña a lo que es protagonista; (3) usar `-webkit-text-fill-color` además de `color:transparent` donde hay `<small>`/spans dentro.

---

## 6. Componentes (especificación)

### 6.1 Tarjeta (listas de guiones)
```css
.card{ border-radius:22px; border:1px solid var(--line); padding:17px 16px 17px 20px; margin-bottom:11px;
  background:linear-gradient(160deg,var(--glass2),var(--glass));
  box-shadow:inset 0 1px 0 rgba(255,255,255,.07),0 14px 32px -14px rgba(0,0,0,.65);
  transition:transform .45s var(--ease),border-color .3s;
  animation:rise .7s var(--ease) both; animation-delay:calc(var(--i,0)*60ms) }   /* entrada escalonada 60 ms */
.card:active{ transform:scale(.968); border-color:var(--accent) }
```
Título 17 px / 600 / −.25px; subtítulo 13 px `--muted`.

### 6.2 Control segmentado con pulgar deslizante
Contenedor: `padding:3px; border-radius:15px; background:rgba(255,255,255,.07); border:1px solid rgba(255,255,255,.08)`. En Orvex: `padding:2px; border-radius:11px; background:rgba(118,118,128,.24)`. El **pulgar** (`.thumb`) es un elemento absoluto que se desliza con `transition: transform .5s var(--ease), width .5s var(--ease)` y lleva el metal teñido (`--lg-tint` + `--lg-tedge`). Texto seleccionado `#fff` peso 600; no seleccionado `#d8dbe6` peso 500.

### 6.3 Interruptor iOS
```css
.ios-sw{ width:51px; height:31px; border-radius:16px; background:rgba(120,120,128,.36); transition:background .3s var(--ease) }
.ios-sw::after{ content:''; position:absolute; top:2px; left:2px; width:27px; height:27px; border-radius:50%; background:#fff;
  box-shadow:0 3px 8px rgba(0,0,0,.3),0 1px 1px rgba(0,0,0,.2),inset 0 -1px 2px rgba(0,0,0,.12);
  transition:transform .35s var(--spring) }
.ios-sw.on{ background:#34c759 }  .ios-sw.on::after{ transform:translateX(20px) }
.ios-sw:active::after{ width:32px }  .ios-sw.on:active::after{ transform:translateX(15px) }   /* la perilla se estira al presionar */
```

### 6.4 Sliders
Pista 6 px con `linear-gradient(90deg,var(--accent2),var(--accent) var(--p),rgba(255,255,255,.16) var(--p))` (`--p` = % de avance, se actualiza por JS). Pulgar 28 px esfera de aluminio (ver §5), escala 1.2 al presionar.

### 6.5 Chips / idiomas / lista de videos
Normal: `background: var(--lg-bg)` atenuado (`color-mix(...hi 22%… accent 12%… accent2 26%)`), borde `rgba(255,255,255,.14)`, `box-shadow:inset 0 1px 1px rgba(255,255,255,.4),inset 0 -1px 2px rgba(255,255,255,.08)`. Seleccionado: `--lg-tint` + `--lg-tedge`. Radio 14–16 px (chips 62 px de alto, mínimo 96 px de ancho).

### 6.6 Gemas selectoras de color (esmeraldas facetadas, SVG)
Cada color del tema se muestra como una gema hexagonal de 46 px (`viewBox 0 0 48 48`), generada por JS con los colores del tema. Estructura (de atrás hacia adelante):
1. `polygon 12,4 36,4 46,24 36,44 12,44 2,24` con degradado diagonal `hi → accent (45 %) → accent2`.
2. Facetas claras: `12,4 36,4 31,14 17,14` (blanco .5), `36,4 46,24 37,24 31,14` (blanco .16), `12,4 17,14 11,24 2,24` (blanco .28).
3. Facetas oscuras: `2,24 11,24 17,34 12,44` (negro .16), `11,24 37,24 31,34 17,34` (negro .08), `37,24 46,24 36,44 31,34` (negro .34), `17,34 31,34 36,44 12,44` (negro .28).
4. Mesa central: `17,14 31,14 37,24 31,34 17,34 11,24` sin relleno, trazo blanco .55, 0.8 px.
5. Destello: línea `M18 9 L27 9`, trazo blanco 2 px, redondeada, opacidad .9.
6. Contorno exterior con degradado vertical blanco→`hi`→blanco, 1.6 px.

Estados: seleccionada `scale(1.18)` + `drop-shadow(0 0 9px var(--c))`; no seleccionada `opacity:.78`. Al tocarla: animación `gemSpin` .95 s (salta 17 px, gira 360° en Y con `perspective(240px)`, brillo hasta 1.9×) + halo `gemGlow` (círculo radial con `mix-blend-mode:screen`). Respeta `prefers-reduced-motion`.

### 6.7 Hoja de ajustes (bottom sheet de vidrio)
```css
#panel{ border-radius:30px 30px 0 0; color:#f2f5fb; border:1px solid rgba(255,255,255,.14); border-bottom:none;
  background:linear-gradient(180deg,rgba(30,34,52,.78),rgba(10,12,20,.90));
  backdrop-filter:blur(30px) saturate(1.7);
  box-shadow:0 -24px 70px -24px rgba(0,0,0,.85),inset 0 1px 0 rgba(255,255,255,.1);
  transform:translateY(105%); transition:transform .55s var(--ease) }   /* entra desde abajo */
```
Altura `56vh` (350–520 px). Asa de arrastre 42×5 px `rgba(255,255,255,.26)`. Modo "fantasma": al arrastrar un slider el panel se vuelve casi invisible (`opacity .08`, fondo `rgba(8,10,18,.05)`, sin blur) para ver el cambio en vivo detrás.

### 6.8 Barra superior y estado
Barra: `border-bottom:1px solid var(--line); background:linear-gradient(180deg,rgba(255,255,255,.045),rgba(255,255,255,0)); backdrop-filter:blur(20px) saturate(1.5)`. Pastilla de estado: `border-radius:999px; background:var(--glass); border:1px solid var(--line); backdrop-filter:blur(14px)`, punto de 7 px con `box-shadow:0 0 10px` y pulso `2.6s`.

### 6.9 Divisores de video y barra guía
- Banda: `linear-gradient(180deg,transparent,var(--soft) 22%,var(--soft) 78%,transparent)`, ancho 100vw, `isolation:isolate; overflow:hidden; contain:paint`.
- Línea (`.rule`): 5 px, `linear-gradient(90deg,transparent 0%,var(--accent) 30%,var(--hi) 50%,var(--accent) 70%,transparent 100%)`, `box-shadow:0 0 22px var(--accent),0 0 6px var(--hi)`.
- Píldora "FIN": borde 2 px `var(--accent)`, texto 15 px / 800 / `letter-spacing:.2em` mayúsculas, `box-shadow:0 0 20px -4px var(--accent)`, cuadrito de 12 px con glow antes del texto.
- Barra guía de lectura: 4 px a la izquierda, `background:var(--grad)`, `box-shadow:0 0 18px var(--accent)`, más un lavado horizontal `linear-gradient(90deg,var(--soft),transparent 82%)`. Se oculta (opacity 0) cuando el elemento actual es un divisor para que su brillo no parezca texto cortado.
- Desvanecidos arriba (15 %) y abajo (30 %) del visor: `linear-gradient(to bottom,var(--bg),transparent)`.

### 6.10 Oro Nexa IA Studio (créditos y productos)
Tipografía serif elegante: **Playfair Display** itálica 700, 22–27 px, `letter-spacing:.02em`; sobretítulo 11 px mayúsculas `letter-spacing:.34em` color `#b89a55`; ornamento: línea 120 px × 1 px `linear-gradient(90deg,transparent,#d4a43c,transparent)`. Iconos de producto: cuadro 50 px, fondo `#0b0b0e`, borde `rgba(212,164,60,.55)`, `box-shadow:0 8px 18px -8px rgba(233,196,106,.5)`, monograma con degradado `135deg #8a6420 → #fff1c2 (40 %) → #d4a43c (62 %) → #a47a24`.

### 6.11 Resumen de acabados y recursos usados

`backdrop-filter` (blur + saturate) · degradados apilados de 3 capas · `inset box-shadow` de bisel · `box-shadow` con spread negativo para glow · `color-mix(in srgb, …)` para derivar tonos del acento · `background-clip:text` · `drop-shadow` en texto · máscaras de desvanecido · SVG facetado para gemas · `mix-blend-mode:screen` para destellos · animaciones con `cubic-bezier` personalizadas · háptica (`tap()` vibración corta) y sonidos de interfaz (sintetizados, no archivos).

---

## 7. Tipografía

- **Predeterminada:** fuente del sistema (SF Pro en iPhone): `-apple-system,BlinkMacSystemFont,"SF Pro Display","Segoe UI",Roboto,"Helvetica Neue",sans-serif`. Se siente nativa de Apple sin cargar nada.
- **Escala:** guion 52 px (ajustable) / peso 700 / interlineado 1.28 / `letter-spacing:-.02em` / `text-wrap:balance`; títulos de video `min(1.7×size, 16vw)` peso 900 mayúsculas con `letter-spacing:.08em`; etiquetas de grupo 11 px / 600 / mayúsculas / `letter-spacing:2.2px`; contador 38vw peso 200; ajustes 13–16 px.
- **Pesos:** 200 (números grandes), 500 (UI), 600 (botones, títulos de tarjeta), 700 (guion, primarios), 800–900 (divisores, píldoras de fin).
- **Alternativas incluidas (autoalojadas en `/fonts`, `font-display:swap`):** Inter, Manrope, Space Grotesk, Sora, Orbitron (futurista), Oswald, Playfair Display, Lora, JetBrains Mono.
- La fuente elegida se aplica a **toda** la interfaz (`html,body{font-family:var(--font)}`), no solo al guion.

---

## 8. Movimiento

| Uso | Curva y duración |
|---|---|
| Presionar botón | `transform:scale(.93–.97)`, `transition-duration:.12–.14s` (rápido al bajar) y `.35–.45s var(--ease)` al soltar |
| Entrada de pantalla | `scrIn .5s var(--ease)`: de `translateY(20px) scale(.985)` a normal |
| Entrada de tarjetas | `rise .7s var(--ease)` con retraso `calc(var(--i)*60ms)` |
| Hoja de ajustes | `translateY(105%)→0`, `.55s var(--ease)` |
| Interruptor / gemas | `var(--spring)` = `cubic-bezier(.34,1.45,.64,1)` (rebote) |
| Pulso del botón Play activo | `glowPulse 2.4s`: el glow pasa de `0 12px 30px -8px` a `0 12px 46px -4px` |
| Aparición de línea (modo línea) | `lineIn .5s`: `translateY(22px) scale(.97) blur(5px)` → nítido |
| Cuenta regresiva | `cdPop .6s`: `scale(1.5)` → 1 con fade |
| Reducir movimiento | `@media (prefers-reduced-motion:reduce)` pone todas las animaciones a .01 ms |

---

## 9. Lecciones aprendidas (las ~20 correcciones, resumidas para no repetirlas)

1. **No dependas de `backdrop-filter` para que algo se lea.** En iPhone con "Modo de bajo consumo" el blur puede no renderizar. El overlay de la cuenta regresiva usa fondo casi opaco (`rgba(3,4,9,.94)`) y el blur es solo adorno.
2. **`backdrop-filter` es lo más caro de repintar.** Durante el scroll automático (`body.running`) se desactiva en barra y controles y se sustituye por `color-mix(in srgb, var(--bg) 88%, transparent)`. Se ve igual, fluye mejor.
3. **Brillos que "cortan" el texto:** una barra con glow superpuesta a una banda clara parece texto cortado. Se oculta la barra sobre los divisores y se aísla la banda con `isolation:isolate; overflow:hidden; contain:paint; transform:translateZ(0)` en sus hijos.
4. **Números de 2 dígitos:** `38vw` solo sirve para un dígito; con `10` se desborda. Clase `.wide` a `19vw` + `max-width:90vw; white-space:nowrap`.
5. **Texto con degradado + `<small>`:** añade `-webkit-text-fill-color` explícito en el hijo, si no hereda transparente.
6. **PWA + iconos:** cualquier archivo cacheado (iconos, fuentes) solo se actualiza si cambia el número de versión del caché en `sw.js` (`const V='tp-vN'`). Si cambias un icono y no subes `V`, el celular sigue mostrando el viejo. Además iOS guarda el ícono del acceso directo aparte: borrar y volver a agregar.
7. **Jerarquía en tres niveles de botón:** primario teñido (una sola acción por pantalla), secundario cristal, terciario texto/gris iOS. Si todo brilla, nada destaca.
8. **El corte duro del "horizonte cromado" (47 %→50 %) es lo que da el metal.** Un degradado suave se ve plástico.
9. **Glow con spread negativo** (`-8px`) para que el resplandor quede debajo y no forme un halo difuso alrededor.
10. **Los temas deben cambiar solo variables**, nunca reglas: todo el sistema se recolorea cambiando `--accent`, `--hi`, `--accent2`, `--bg`, `--on`.
11. **`.ln`/guion atenuado:** la opacidad .2 + escala .93 de las líneas no activas es opcional (ajuste "Ver todos los diálogos por igual" lo desactiva y deja todas iguales).

---

## 10. Ícono de la app (galaxia hiperrealista)

Diseño final: galaxia espiral **frontal** con núcleo blanco incandescente, brazos azules con salpicaduras rosa (regiones HII), polvo oscuro en los brazos y campo de estrellas denso con una estrella brillante con picos de difracción. Se genera **proceduralmente** (no es una imagen descargada): ruido de valor + fBm en un `<canvas>` ejecutado con Playwright.

- Script: `tools/galaxy-icon/generate_icon.py` → `python3 tools/galaxy-icon/generate_icon.py <carpeta_destino>` (requiere `playwright` con Chromium). Reproduce los 4 PNG exactamente (verificado byte a byte).
- Tamaños: `icon-512.png` (esquinas redondeadas), `icon-192.png`, `icon-180.png` (apple-touch-icon), `icon-512-maskable.png` (cuadrado completo con la galaxia al 74 % para zona segura).
- Parámetros de la variante elegida (`B_frontal_azul`): 2 brazos, inclinación .92, núcleo `rb=.13`, polvo 1.2, exposición con tone-mapping `1-exp(-x·ex)`.
- Para otro tema (por ejemplo dorado) se cambian los arrays de color (`bulgeCol`, `arm1`, `arm2`, `hiiCol`, `halo`, `bg`) y `warmStars`.

---

## 11. Cómo reproducirlo en otros tipos de proyecto

Regla general: **conservar la receta** (un acento + claro + oscuro, luz arriba/sombra abajo, glow de color, degradado metálico en texto, vidrio) y **adaptar los recursos gráficos al tema de cada pieza**: piezas del mismo tema pueden compartir estilo; piezas de temas distintos deben verse distintas (por ejemplo, espacio vs. tecnología) manteniendo la identidad de marca. Eso se logra cambiando la paleta (§3.3) y los elementos decorativos, no la receta.

| Proyecto | Cómo traducir |
|---|---|
| **Páginas web** | Copia `:root`, `body::before`, las variables `--lg-*` y las clases `.btn-glass`/`.btn-tint` de §4.1. Usa `color-mix` (soportado en Safari 16.2+, Chrome 111+). Prefija `-webkit-backdrop-filter` y `-webkit-background-clip`. |
| **Miniaturas / flyers / carruseles** (Photoshop, Illustrator, Canva) | Botón/etiqueta = forma redondeada con 3 capas: degradado 160° `hi→accent→accent2`; superposición vertical blanco 60 %→16 %→0 % con corte duro en 50 % y negro 16 % abajo; franja diagonal blanca a 115°. Bisel: línea interna blanca al 90 % de 1.5 px arriba; sombra interna negra al 32 % de 2.5 px abajo; **sombra exterior de color** (acento, desenfoque 22, desplazamiento 10, spread −8). Texto: degradado blanco→`metal` + brillo exterior del color de acento. Fondo: casi negro del tinte del tema + dos manchas de luz de color en las esquinas superiores. |
| **Motion graphics / automatizaciones de edición** (After Effects, Premiere, Remotion) | Usa los mismos hex (§3.2). Entradas con la curva `cubic-bezier(.32,.72,0,1)` (easing "iOS"), 0.4–0.6 s; rebotes con `cubic-bezier(.34,1.45,.64,1)`; pulsos de glow de 2.4 s; texto con degradado metálico y `drop-shadow` de color; títulos en mayúsculas peso 900 con `letter-spacing .08em`. |
| **Diseño corporativo** | Usa el **Modo Business** (§3.5): plano, un acento, sin brillo ni blur; mismas tipografías. |
| **Apps / dashboards** | Copia todo el CSS de §2–§6; los controles ya están listos (segmentado, switch, sliders, chips, hoja de vidrio, tarjetas). |

---

## 12. Prompt maestro (copia y pega junto con el enlace)

```
Eres un diseñador de producto senior. Voy a darte el enlace de una app de referencia y
este documento de especificaciones. Tu tarea es REPLICAR su estilo visual en mi proyecto.

ENLACES DE REFERENCIA
- App en vivo: https://yahirsierramunoz-dev.github.io/teleprompter-yahir/
- Código fuente (texto): https://raw.githubusercontent.com/yahirsierramunoz-dev/teleprompter-yahir/main/index.html
- Especificaciones: https://raw.githubusercontent.com/yahirsierramunoz-dev/teleprompter-yahir/main/DESIGN-SPEC.md

PASOS OBLIGATORIOS
1. Lee DESIGN-SPEC.md completo y el CSS de index.html (todo está en un solo <style>).
   Abre la app en viewport 390×844 y revisa Inicio, Lector y Ajustes si puedes renderizarla.
2. Usa los VALORES EXACTOS del documento (hex, degradados, sombras, radios, curvas).
   No los aproximes ni los "mejores" sin pedírmelo.
3. Construye todo con la receta: UN color de acento + uno claro (hi) + uno oscuro (accent2) +
   fondo casi negro con tinte + color "on" para texto sobre el acento. Deriva el resto.
4. Botones: 3 niveles. Primario teñido (--lg-tint + --lg-tedge), secundario cristal
   (--lg-bg + --lg-edge + backdrop-filter), terciario plano. Los tres degradados apilados,
   el corte duro del horizonte cromado en 47–50 %, luz arriba y sombra abajo, glow de color
   con spread negativo, texto grabado con text-shadow.
5. Texto protagonista con degradado metálico (claro arriba → color de tema abajo).
6. Movimiento con las curvas --ease y --spring del documento; feedback al tocar scale(.93–.97).
7. No dependas de backdrop-filter para la legibilidad; desactívalo en animaciones continuas.
8. Adapta los recursos gráficos (fondos, ilustraciones, decoración) al TEMA de esta pieza,
   manteniendo la identidad de marca. Piezas del mismo tema pueden compartir estilo; piezas
   de temas distintos deben verse distintas.

MI PROYECTO
- Tipo: [web / flyer / carrusel / miniatura / edición de video / diseño corporativo / otro]
- Tema o tema de color: [describe, o elige un color de acento]
- Contenido: [texto, imágenes, medidas del formato]

ENTREGA
- El resultado final listo para usar.
- Una lista de qué tokens y valores del documento usaste y dónde.
- Una verificación contra el checklist de la sección 13.
```

---

## 13. Checklist de verificación (para la IA que replica)

- [ ] Fondo casi negro con tinte del tema y dos manchas de luz de color en las esquinas superiores.
- [ ] Un solo color de acento dominante; el resto neutros.
- [ ] Botón primario: 3 degradados, corte duro del horizonte en ~50 %, filo blanco arriba (1.5 px), sombra interna abajo (2.5 px), glow de color debajo, texto grabado.
- [ ] Botón secundario: translúcido, mismo bisel, `backdrop-filter`, borde blanco ~28 %.
- [ ] Radios: píldora (999px) o círculo para botones; 22 px tarjetas; 30 px arriba en la hoja.
- [ ] Títulos con degradado metálico y brillo de color.
- [ ] Curvas de animación `--ease` / `--spring`; feedback de escala al presionar.
- [ ] Contraste del texto sobre el acento correcto (`on` oscuro en acentos claros, blanco en oscuros).
- [ ] Nada depende de blur para ser legible.
- [ ] Piezas de temas distintos se ven distintas; la identidad de marca se mantiene.
