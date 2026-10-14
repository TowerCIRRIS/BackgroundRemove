"""Application web de suppression d'arrière-plan basée sur withoutbg.

Lancer :  python app.py   puis ouvrir http://127.0.0.1:5000
"""

import io
import os
import tempfile
import threading
from pathlib import Path

from flask import Flask, jsonify, request, send_file, send_from_directory
from PIL import Image, ImageOps

from withoutbg import APIError, WithoutBG, WithoutBGError

BASE_DIR = Path(__file__).parent
MAX_UPLOAD_MB = 25
ALLOWED_EXT = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff"}

app = Flask(__name__, static_folder=None)
app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_MB * 1024 * 1024

# Le modèle local (~1,5 Go) n'est chargé qu'une seule fois, à la première requête.
_local_model = None
_local_lock = threading.Lock()


def get_local_model():
    global _local_model
    with _local_lock:
        if _local_model is None:
            _local_model = WithoutBG.open_weights()
        return _local_model


def get_api_model(api_key: str | None):
    key = api_key or os.environ.get("WITHOUTBG_API_KEY")
    if not key:
        raise WithoutBGError(
            "Aucune clé API fournie (champ de l'interface ou variable WITHOUTBG_API_KEY)."
        )
    return WithoutBG.api(api_key=key)


@app.get("/")
def index():
    return send_from_directory(BASE_DIR, "index.html")


@app.get("/api/status")
def status():
    return jsonify(
        local_model_loaded=_local_model is not None,
        api_key_in_env=bool(os.environ.get("WITHOUTBG_API_KEY")),
        max_upload_mb=MAX_UPLOAD_MB,
    )


@app.post("/api/remove")
def remove():
    upload = request.files.get("image")
    if upload is None or not upload.filename:
        return jsonify(error="Aucune image reçue."), 400

    ext = Path(upload.filename).suffix.lower()
    if ext not in ALLOWED_EXT:
        return jsonify(error=f"Format non supporté : {ext or 'inconnu'}."), 400

    mode = request.form.get("mode", "local")
    api_key = request.form.get("api_key", "").strip() or None

    tmp_path = None
    try:
        # Normalise l'orientation EXIF puis enregistre dans un fichier temporaire
        img = ImageOps.exif_transpose(Image.open(upload.stream))
        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGBA" if "A" in img.getbands() else "RGB")
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            tmp_path = tmp.name
        img.save(tmp_path, format="PNG")

        model = get_api_model(api_key) if mode == "api" else get_local_model()
        result = model.remove_background(tmp_path)

        buf = io.BytesIO()
        result.save(buf, format="PNG")
        buf.seek(0)
        return send_file(buf, mimetype="image/png")

    except APIError as e:
        return jsonify(error=f"Erreur de l'API withoutBG : {e}"), 502
    except WithoutBGError as e:
        return jsonify(error=f"Erreur de traitement : {e}"), 500
    except OSError:
        return jsonify(error="Fichier image illisible ou corrompu."), 400
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)


@app.errorhandler(413)
def too_large(_):
    return jsonify(error=f"Image trop lourde (maximum {MAX_UPLOAD_MB} Mo)."), 413


if __name__ == "__main__":
    # Hôte local uniquement : l'appli n'est pas exposée sur le réseau.
    app.run(host="127.0.0.1", port=5000, debug=False)
