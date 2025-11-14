"""
Script de test simple pour vérifier que Marker fonctionne correctement
"""

import sys
from marker.models import load_all_models

def test_marker_installation():
    """Test si Marker est correctement installé et peut charger les modèles."""
    try:
        print("=" * 60)
        print("TEST D'INSTALLATION DE MARKER")
        print("=" * 60)

        print("\n1. Import du module marker...")
        import marker
        print("   ✓ Module marker importé avec succès")

        print("\n2. Import des sous-modules...")
        from marker.convert import convert_single_pdf
        from marker.models import load_all_models
        print("   ✓ Sous-modules importés avec succès")

        print("\n3. Vérification des dépendances...")
        import torch
        import transformers
        import surya
        print(f"   ✓ PyTorch version: {torch.__version__}")
        print(f"   ✓ Transformers version: {transformers.__version__}")
        print(f"   ✓ Surya OCR importé avec succès")

        print("\n4. Test de chargement des modèles...")
        print("   Note: Le premier chargement téléchargera ~2-3 GB de modèles.")
        print("   Cela peut prendre plusieurs minutes...")

        response = input("\n   Voulez-vous tester le chargement des modèles? (o/n): ")

        if response.lower() in ['o', 'oui', 'y', 'yes']:
            print("\n   Chargement des modèles en cours...")
            models = load_all_models()
            print("   ✓ Modèles chargés avec succès!")
            print(f"   ✓ Nombre de modèles: {len(models)}")
        else:
            print("   → Test de chargement des modèles ignoré")

        print("\n" + "=" * 60)
        print("✓ INSTALLATION RÉUSSIE!")
        print("=" * 60)
        print("\nMarker est prêt à convertir des PDFs en Markdown!")
        print("Utilisez 'python pdf_to_markdown.py --help' pour plus d'infos.")

        return True

    except Exception as e:
        print(f"\n✗ ERREUR: {str(e)}")
        print("\nVeuillez vérifier que:")
        print("1. L'environnement virtuel est activé (source venv/bin/activate)")
        print("2. Marker est installé (pip list | grep marker)")
        return False

if __name__ == "__main__":
    success = test_marker_installation()
    sys.exit(0 if success else 1)
