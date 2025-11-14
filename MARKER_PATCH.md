# Patch Marker PDF 0.2.5

## Problème identifié

marker-pdf version 0.2.5 contient un bug dans l'interaction entre `marker/convert.py` et `marker/pdf/extract_text.py` avec la bibliothèque `pdftext`.

### Bug
- `convert.py` crée un objet `PdfDocument` et le passe à `get_text_blocks()`
- `get_text_blocks()` passe cet objet à `pdftext.extraction.dictionary_output()`
- **Problème**: `dictionary_output()` attend un chemin de fichier STRING, pas un objet PdfDocument
- **Résultat**: `TypeError: Invalid input type 'PdfDocument'`

## Solution appliquée

### Fichiers modifiés

1. **`venv/lib/python3.9/site-packages/marker/pdf/extract_text.py`**
   - Modifié la signature de `get_text_blocks()` pour accepter un paramètre optionnel `fname`
   - Ajouté une logique pour extraire le chemin du fichier depuis l'objet `doc._input` ou utiliser le paramètre `fname`
   - Passe maintenant le chemin STRING à `dictionary_output()` au lieu de l'objet

2. **`venv/lib/python3.9/site-packages/marker/convert.py`**
   - Modifié l'appel à `get_text_blocks()` pour passer le paramètre `fname=fname`

### Code patch

**extract_text.py** (lignes 77-97):
```python
def get_text_blocks(doc, max_pages: Optional[int] = None, fname: Optional[str] = None) -> (List[Page], Dict):
    toc = get_toc(doc)

    page_range = range(len(doc))
    if max_pages:
        range_end = min(max_pages, len(doc))
        page_range = range(range_end)

    # Get the filename - if doc has _input attribute use it, otherwise use fname parameter
    if hasattr(doc, '_input'):
        pdf_path = doc._input
    elif fname:
        pdf_path = fname
    else:
        # Fallback - pass doc and hope pdftext can handle it
        pdf_path = doc

    char_blocks = dictionary_output(pdf_path, page_range=page_range, keep_chars=True)
    marker_blocks = [pdftext_format_to_blocks(page, pnum) for pnum, page in enumerate(char_blocks)]

    return marker_blocks, toc
```

**convert.py** (lignes 63-69):
```python
# Get initial text blocks from the pdf
doc = pdfium.PdfDocument(fname)
pages, toc = get_text_blocks(
    doc,
    max_pages=max_pages,
    fname=fname,
)
```

## Maintenance

**IMPORTANT**: Ce patch est appliqué directement dans le venv. Si vous réinstallez marker-pdf ou recréez le venv, vous devrez réappliquer ce patch.

### Pour réappliquer le patch:

1. Éditer `venv/lib/python3.9/site-packages/marker/pdf/extract_text.py`
2. Éditer `venv/lib/python3.9/site-packages/marker/convert.py`
3. Appliquer les modifications ci-dessus

### Alternative: Fork marker-pdf

Pour une solution plus permanente, envisagez de:
1. Fork le repo marker-pdf sur GitHub
2. Appliquer ce patch
3. Installer depuis votre fork: `pip install git+https://github.com/votre-username/marker.git@branche-patch`

## Statut

✅ Patch appliqué et testé
✅ Serveur Flask fonctionnel sur http://localhost:8080
✅ Conversions PDF opérationnelles
