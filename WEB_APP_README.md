# Application Web Marker - PDF to Markdown

Interface web interactive pour convertir des PDFs en Markdown en utilisant Marker AI.

## Fonctionnalités

- **Interface visuelle moderne** avec drag & drop
- **Upload de PDFs** jusqu'à 100 MB
- **Conversion en temps réel** avec barre de progression
- **Téléchargement direct** du markdown
- **Support de n'importe quelle taille** de PDF
- **Traitement asynchrone** (non-bloquant)

## Démarrage rapide

### 1. Activer l'environnement virtuel

```bash
source venv/bin/activate
```

### 2. Lancer l'application

```bash
python app.py
```

### 3. Ouvrir dans le navigateur

Ouvrez votre navigateur à l'adresse:
```
http://localhost:5000
```

## Utilisation

1. **Glissez-déposez** ou **cliquez** pour sélectionner un fichier PDF
2. Cliquez sur **"Convertir en Markdown"**
3. Attendez la fin de la conversion (barre de progression)
4. **Téléchargez** le fichier markdown généré

## Architecture

```
Tao Bite/
├── app.py                  # Application Flask principale
├── templates/
│   └── index.html         # Interface web
├── uploads/               # PDFs uploadés (temporaire)
├── outputs/               # Markdowns générés
├── static/
│   ├── css/              # Styles CSS (optionnel)
│   └── js/               # Scripts JS (optionnel)
└── venv/                 # Environnement virtuel
```

## Configuration

### Taille maximum des fichiers

Par défaut, la limite est 100 MB. Pour la modifier, éditez `app.py`:

```python
app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024  # 200 MB
```

### Port et hôte

Par défaut, l'application écoute sur `0.0.0.0:5000`. Pour changer:

```python
app.run(debug=True, host='localhost', port=8080)
```

### Clé secrète

En production, changez la clé secrète dans `app.py`:

```python
app.secret_key = 'votre-cle-secrete-aleatoire-longue'
```

## API Endpoints

### `POST /upload`
Upload un fichier PDF et démarre la conversion.

**Request:**
```
Content-Type: multipart/form-data
file: <PDF file>
```

**Response:**
```json
{
  "job_id": "uuid",
  "message": "Conversion démarrée",
  "filename": "document.pdf"
}
```

### `GET /status/<job_id>`
Obtenir le statut d'une conversion en cours.

**Response:**
```json
{
  "status": "processing",
  "message": "Traitement du PDF...",
  "filename": "document.pdf"
}
```

États possibles: `queued`, `processing`, `completed`, `error`

### `GET /download/<job_id>`
Télécharger le fichier markdown converti.

### `GET /models/status`
Vérifier si les modèles IA sont chargés.

**Response:**
```json
{
  "loaded": true,
  "loading": false
}
```

### `POST /models/load`
Charger les modèles IA manuellement.

## Intégration avec d'autres systèmes

### Utilisation avec cURL

```bash
# Upload et conversion
curl -X POST -F "file=@document.pdf" http://localhost:5000/upload

# Vérifier le statut
curl http://localhost:5000/status/JOB_ID

# Télécharger le résultat
curl -O http://localhost:5000/download/JOB_ID
```

### Utilisation avec Python requests

```python
import requests
import time

# Upload
with open('document.pdf', 'rb') as f:
    response = requests.post('http://localhost:5000/upload', files={'file': f})
    job_id = response.json()['job_id']

# Attendre la fin
while True:
    status = requests.get(f'http://localhost:5000/status/{job_id}').json()
    print(f"Status: {status['status']} - {status['message']}")

    if status['status'] == 'completed':
        break
    elif status['status'] == 'error':
        print("Erreur:", status['message'])
        break

    time.sleep(2)

# Télécharger
response = requests.get(f'http://localhost:5000/download/{job_id}')
with open('output.md', 'wb') as f:
    f.write(response.content)
```

## Performance

### Premier lancement
- **Temps de démarrage**: 1-2 minutes (chargement des modèles IA)
- **Téléchargement initial**: 2-3 GB de modèles

### Conversions suivantes
- **Document de 10 pages**: ~30-60 secondes (CPU)
- **Document de 10 pages**: ~10-20 secondes (GPU)

Les modèles restent chargés en mémoire entre les conversions.

## Déploiement en production

### Avec Gunicorn

```bash
pip install gunicorn

gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Avec Docker

Créez un `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
```

Build et run:

```bash
docker build -t marker-app .
docker run -p 5000:5000 marker-app
```

### Variables d'environnement

```bash
export FLASK_ENV=production
export SECRET_KEY=votre-cle-secrete
export MAX_CONTENT_LENGTH=104857600  # 100 MB
```

## Sécurité

### Recommandations pour la production:

1. **Changez la clé secrète** (`app.secret_key`)
2. **Désactivez le mode debug** (`app.run(debug=False)`)
3. **Limitez les uploads** (taille et type de fichier)
4. **Ajoutez une authentification** si nécessaire
5. **Utilisez HTTPS** avec un reverse proxy (nginx)
6. **Nettoyez les fichiers temporaires** régulièrement

### Nettoyage automatique

Ajoutez un cron job pour nettoyer les fichiers anciens:

```bash
# Nettoyer les fichiers de plus de 24h
find uploads/ -type f -mtime +1 -delete
find outputs/ -type f -mtime +1 -delete
```

## Troubleshooting

### Erreur "Models not loaded"
Les modèles n'ont pas été téléchargés. Lancez:
```bash
python test_marker.py
```

### Erreur de mémoire
Réduisez `MAX_CONTENT_LENGTH` ou augmentez la RAM disponible.

### Conversion très lente
- Utilisez un GPU si disponible
- Réduisez la taille du PDF
- Convertissez en batch pendant la nuit

## Support

Pour plus d'informations:
- Documentation Marker: https://github.com/VikParuchuri/marker
- Flask Documentation: https://flask.palletsprojects.com/
