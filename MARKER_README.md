# Marker PDF to Markdown Converter

Ce projet utilise [Marker](https://github.com/VikParuchuri/marker) pour convertir des fichiers PDF en Markdown de haute qualité avec OCR et détection de layout.

## Installation

Marker a été installé dans un environnement virtuel Python pour éviter les conflits de dépendances.

### Activation de l'environnement virtuel

```bash
# Activer l'environnement virtuel
source venv/bin/activate

# Pour désactiver (quand vous avez terminé)
deactivate
```

## Utilisation

### 1. Utilisation du script Python personnalisé

Le script `pdf_to_markdown.py` offre une interface simple pour convertir des PDFs:

#### Convertir un seul PDF

```bash
# Activer l'environnement virtuel
source venv/bin/activate

# Convertir un PDF (le markdown sera sauvegardé dans le même dossier)
python pdf_to_markdown.py chemin/vers/votre/fichier.pdf

# Spécifier un dossier de sortie
python pdf_to_markdown.py chemin/vers/fichier.pdf -o dossier_sortie/
```

#### Conversion par lot (batch)

```bash
# Convertir tous les PDFs d'un dossier
python pdf_to_markdown.py dossier_pdfs/ --batch

# Avec un dossier de sortie spécifique
python pdf_to_markdown.py dossier_pdfs/ --batch -o markdown_output/
```

### 2. Utilisation en tant que bibliothèque Python

```python
from pdf_to_markdown import convert_pdf_to_markdown

# Convertir un PDF
result = convert_pdf_to_markdown("document.pdf")

# Accéder au contenu markdown
markdown_text = result["markdown"]
metadata = result["metadata"]
output_path = result["output_path"]

print(f"Conversion terminée: {output_path}")
print(f"Nombre de pages: {metadata.get('pages')}")
```

### 3. Utilisation directe de Marker (CLI)

```bash
# Activer l'environnement virtuel
source venv/bin/activate

# Convertir un seul PDF
marker_single fichier.pdf output_folder/

# Convertir plusieurs PDFs
marker fichier1.pdf fichier2.pdf -o output_folder/

# Avec GPU (si disponible)
marker_single fichier.pdf output_folder/ --gpu
```

## Fonctionnalités

Marker offre plusieurs avantages par rapport aux autres outils de conversion PDF:

- **OCR Avancé**: Utilise des modèles d'IA pour une reconnaissance de texte précise
- **Détection de Layout**: Préserve la structure du document (titres, listes, tableaux)
- **Support Multilingue**: Fonctionne avec plusieurs langues
- **Extraction d'Images**: Extrait et référence les images du PDF
- **Qualité Supérieure**: Meilleurs résultats que pypdf, pdfminer, ou pdf2text

## Exemple d'intégration avec Qdrant

Vous pouvez combiner Marker avec votre système Qdrant existant:

```python
from pdf_to_markdown import convert_pdf_to_markdown
from qdrant_store import QdrantVectorStore

# Convertir le PDF en markdown
result = convert_pdf_to_markdown("document.pdf")
markdown_text = result["markdown"]

# Découper le texte en chunks (exemple simple)
chunks = markdown_text.split('\n\n')  # Découper par paragraphe
chunks = [c.strip() for c in chunks if c.strip()]

# Stocker dans Qdrant
store = QdrantVectorStore(
    collection_name="pdf_documents",
    host="localhost",
    port=6333
)

metadatas = [{
    "source": "document.pdf",
    "page": i // 10,  # Approximatif
    "type": "pdf"
} for i in range(len(chunks))]

store.add_documents(chunks, metadatas=metadatas)
```

## Configuration

### Variables d'environnement (optionnel)

Créez un fichier `.env` pour configurer Marker:

```env
# Utiliser le GPU si disponible
TORCH_DEVICE=cuda  # ou 'cpu' ou 'mps' (pour Mac M1/M2)

# Chemin vers les modèles (cache)
MARKER_MODEL_PATH=~/.cache/marker
```

## Dépendances

Les principales dépendances installées:

- `marker-pdf`: Le package principal
- `torch`: Pour les modèles d'IA
- `transformers`: Modèles de langage Hugging Face
- `surya-ocr`: OCR de haute qualité
- `pdftext`: Extraction de texte PDF
- `opencv-python`: Traitement d'image
- `scikit-learn`: Machine learning utilities

## Performance

La première utilisation téléchargera les modèles d'IA (~2-3 GB). Les conversions suivantes seront beaucoup plus rapides car les modèles sont mis en cache.

**Temps de conversion approximatifs:**
- Document de 10 pages: ~30-60 secondes (CPU)
- Document de 10 pages: ~10-20 secondes (GPU)

## Troubleshooting

### Erreur de mémoire
Si vous rencontrez des erreurs de mémoire avec de gros PDFs:

```python
# Traiter le PDF page par page au lieu de tout en une fois
# (fonctionnalité à implémenter si nécessaire)
```

### Modèles non téléchargés
Si les modèles ne se téléchargent pas automatiquement:

```bash
# Forcer le téléchargement
python -c "from marker.models import load_all_models; load_all_models()"
```

## Ressources

- [Documentation Marker](https://github.com/VikParuchuri/marker)
- [Surya OCR](https://github.com/VikParuchuri/surya)
