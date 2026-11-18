# Lucas Marques Barros

**Geologist**

I am a geologist trained at Universidade Federal de Goiás (UFG) and a PhD candidate in Geophysics at Universidade de São Paulo (IAG-USP). My background includes research, fieldwork, laboratories, geotechnics, data engineering, software, teaching and outreach. At USPMAG, my doctoral research investigates magnetic records in geological materials.

My background also includes **Big Data and data engineering**, with professional experience building cloud-based data pipelines, analytical workflows and computational solutions. I develop tools for scientific research, digital petrography and geoscience education.

### Selected projects

| Project | Description | Links |
|---|---|---|
| **RIIMA** | Digital petrography and affinity-based image classification with user-controlled group review. | [Repository](https://github.com/marquesbarros/riima) |
| **Petrodle** | A learning reinforcement prototype for anyone seeking to practise identifying minerals quickly, connecting chemical properties, photomicrographs and optical descriptions. | [Play](https://marquesbarros.github.io/petrodle/) · [Code](https://github.com/marquesbarros/petrodle) |
| **Mineralchemy** | A learning reinforcement prototype for anyone seeking to practise identifying minerals quickly, exploring relationships in mineral composition, formation and transformation. | [Play](https://marquesbarros.github.io/mineralchemy/) · [Code](https://github.com/marquesbarros/mineralchemy) |

### Research and technical interests

`Rock Magnetism` · `Paleomagnetism` · `Paleointensity` · `Magnetic Microscopy` · `Scientific Python` · `Digital Petrography` · `Geospatial Analysis` · `Machine Learning`

### Academic and professional profile

- PhD in Geophysics (in progress, since 2025) — IAG-USP, FAPESP fellow (Processo nº 2026/22988-8)
- BSc in Geology — Federal University of Goiás, 2024
- Degree in Big Data and Analytical Intelligence — UNIASSELVI, 2022
- Previous experience in data engineering — Accenture Brasil, 2021–2025

**[Personal website and CV](https://marquesbarros.github.io/marquesbarros/)** · [Lattes](https://lattes.cnpq.br/6262685341923739) · [ORCID](https://orcid.org/0000-0002-1475-3834) · [LinkedIn](https://www.linkedin.com/in/lucasmarquesbarros/) · [USPMAG](https://paleomagnetismo.iag.usp.br/)

Contact: **marquesbarros@usp.br**

### Local website

The site uses static HTML, CSS and JavaScript. No framework, build step or runtime package installation is required. The Portuguese pages are `index.html` and `curriculo.html`; the English pages are `en/index.html` and `en/cv.html`. Keep equivalent content and publication references in sync when editing either language. Institutional names and published titles retain their original wording.

```sh
python -m http.server 8765 --bind 127.0.0.1
```

Open `http://127.0.0.1:8765/`. All images and fonts are local. Original JPEGs, the PDF and historical base64 chunks are preserved; the site loads conventional WebP files instead of reconstructing images in JavaScript. The three scientific/interface WebPs are byte-identical to their chunk sources. Font licenses are in `assets/fonts/`.

Browser checks, using Python with Playwright installed separately from the site:

```sh
python tests/check_site.py
```

The checks cover keyboard navigation, mobile menu state, JavaScript-disabled pages, image integrity and layouts from 320 to 1440 px. Figure placeholders mark material still to be added to the selected publications.
