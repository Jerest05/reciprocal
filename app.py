from flask import (
    Flask, render_template, request,
    redirect, url_for, session, make_response
)
import secrets
from utils.parser import extraer_json_desde_zip, no_te_siguen

app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/static"
)

# clave fija (32 bytes hex) → NO cambies en cada deploy
app.secret_key = "c9b1d4939a2cf477ee0aa0ef2b1042151a5ae62996ede0bb"

# seguridad y límite de tamaño
app.config.update(
    MAX_CONTENT_LENGTH=10 * 1024 * 1024,   # 10 MB
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=True,            # True porque el sitio ya corre en HTTPS
    SESSION_COOKIE_HTTPONLY=True,
    PERMANENT_SESSION_LIFETIME=3600        # 1 hora
)

# ---- util: evitar caché del navegador ----
@app.after_request
def add_no_store_header(resp):
    resp.headers["Cache-Control"] = "no-store"
    return resp
# -----------------------------------------

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        archivo = request.files["archivo"]
        if archivo and archivo.filename.endswith(".zip"):
            followers, following = extraer_json_desde_zip(archivo.read())
            resultado = no_te_siguen(followers, following)
            return render_template("resultado.html", resultado=resultado)
        else:
            return render_template("index.html", error="Archivo inválido. Subí un ZIP.")
    return render_template("index.html")

@app.route('/privacidad')
def privacidad():
    return render_template('privacidad.html')

@app.route('/ads.txt')
def ads():
    return send_from_directory('static', 'ads.txt')

# ---------- Gunicorn entry ----------
# ExecStart debe apuntar a "app:app"
# gunicorn --workers 3 --bind unix:/run/reciprocal.sock app:app
# ------------------------------------
from datetime import datetime

@app.context_processor
def inject_current_year():
    return {"current_year": datetime.utcnow().year}

if __name__ == "__main__":
    # solo para debug local
    app.run(debug=True)