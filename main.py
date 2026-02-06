from flask import Flask, render_template, request,Response,redirect,url_for,make_response,send_from_directory
import os,time
from flask.globals import session
import random
from datos_activos.funciones_user_sqlite import User, Sqlite_create
import json
import uuid
import os
import re
import html
from PIL import Image, UnidentifiedImageError, ImageFile
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

def obtener_imagenes(ruta):
    extensiones = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp')
    imagenes = []

    for archivo in os.listdir(ruta):
        if archivo.lower().endswith(extensiones):
            imagenes.append(archivo)

    imagenes.sort(
        key=lambda archivo: os.path.getctime(os.path.join(ruta, archivo))
    )

    imagenes.reverse()

    return imagenes

def get_bans():
    sq = Sqlite_create("_baner_")
    return sq.get_all_data().values()

app = Flask(__name__)
app.secret_key = "3d16a60b798846cce41b578605ab9786e5b6da13e01e6f9d95c653e7512517bc"
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # límite 5MB
app.config["PROPAGATE_EXCEPTIONS"] = False
app.config["DEBUG"] = False

app.config.update(
    SESSION_COOKIE_SAMESITE="None",
    SESSION_COOKIE_SECURE=True
)

def limite_por_usuario():
    if "usuario" in session:
        return session["usuario"]  # cada cuenta separada
    return get_remote_address()    # si no está logueado usa IP

limiter = Limiter(
    key_func=limite_por_usuario,
    app=app,
    default_limits=[]
)

UPLOAD_FOLDER = "/home/Joaquin73615/Matos-Hub/uploads"

@app.route("/img/<path:filename>")
def servir_imagen(filename):
    ruta = os.path.join(UPLOAD_FOLDER, filename)

    if not os.path.exists(ruta):
        abort(404)

    return send_from_directory(UPLOAD_FOLDER, filename)

@app.before_request
def cambios():
    if get_user_ip() in get_bans():
        return render_template("error.html",error = "Estas baneado por pendejito")


def render(path, context = None):
    if context is None:
        context = {}
    return render_template(path, **context)

def get_user_ip():
    if request.headers.get("X-Forwarded-For"):
        return request.headers.get("X-Forwarded-For").split(",")[0].strip()
    return request.remote_addr


@app.route("/", methods=["POST","GET"])
def index(context = {}):

    name = session.get("name") or request.cookies.get("name")

    if not name:
        return redirect(url_for("login"))

    session["name"] = name


    return redirect(url_for("home"))


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOADS_DIR = os.path.join(BASE_DIR,"uploads")
JSON_PATH = os.path.join(UPLOADS_DIR, "opens.json")


@app.route("/home", methods=["POST","GET"])
def home(context = {}):



    name = session.get("name") or request.cookies.get("name")

    if not name:
        return redirect(url_for("login"))

    session["name"] = name

    # leer json
    with open(JSON_PATH, "r") as read:
        datos = dict(json.load(read))
        foto, visitas = max(datos.items(), key=lambda item: item[1])

    nombre = session["name"]
    nombre = nombre.replace(" ","")
    user = User(nombre, ip = get_user_ip())

    context = {
        "imagenes": obtener_imagenes(UPLOADS_DIR),
        "vista" : foto
    }

    return render("home.html", context=context)


@app.route("/imagen-abierta", methods=["POST", "GET"])
def imagen_abierta():

    if request.method != "POST":
        return redirect(url_for("home"))

    data = request.get_json()
    img = data["imagen"]

    with open(JSON_PATH, "r") as read:
        datos = dict(json.load(read))
        if str(img) in datos.keys():
            datos[str(img)] += 1
        else:
            datos.update({str(img) : 1})

    with open(JSON_PATH, "w") as write:
        json.dump(datos, write, indent=1)

    return "", 204


@app.route("/login", methods=["POST","GET"])
def login():
    return render("login.html")

@app.route("/sesion", methods=["POST", "GET"])
def sesion():

    if request.method != "POST":
        return redirect(url_for("login"))

    name = request.form.get("name", "")

    if name:
        sq = Sqlite_create(None)

        while True:
            new_name = f"{name}#{random.randint(0, 9999)}"
            if new_name.replace("#", "") + "_adm" not in sq.get_all_tables():
                session["name"] = new_name
                response = make_response(redirect(url_for("home")))
                response.set_cookie(
                    "name",
                    new_name,
                    max_age=60 * 60 * 24 * 30,
                    httponly=True,
                    samesite="Lax"
                )
                return response

    return redirect(url_for("login"))


@app.route("/add_photo", methods=["GET"])
def add():
    return render("add.html")



# evita error por imágenes truncadas (ataque común)
ImageFile.LOAD_TRUNCATED_IMAGES = False

# límites duros
MAX_PIXELS = 10_000_000        # 10 megapixeles
MAX_WIDTH = 5000
MAX_HEIGHT = 5000
ALLOWED_FORMATS = {"jpeg", "jpg", "png", "webp"}

@app.route("/add", methods=["POST"])
@limiter.limit("5 per minute")
def photo():
    # -----------------------------
    # 1. Validar sesión
    # -----------------------------
    if "name" not in session:
        return redirect(url_for("home"))

    # -----------------------------
    # 2. Obtener datos
    # -----------------------------
    name = request.form.get("name_photo", "").strip()
    foto = request.files.get("foto")

    if not foto or not name:
        return redirect(url_for("home"))

    # -----------------------------
    # 3. Sanitizar nombre (anti XSS)
    # -----------------------------
    name = html.escape(name)

    if len(name) > 80:
        return "Nombre demasiado largo", 400

    if not re.match(r'^[a-zA-Z0-9 _\-áéíóúÁÉÍÓÚñÑ]+$', name):
        return "Nombre inválido", 400

    # -----------------------------
    # 4. Límite tamaño real servidor
    # (mejor usar también MAX_CONTENT_LENGTH en config)
    # -----------------------------
    if request.content_length and request.content_length > 5 * 1024 * 1024:
        return "Archivo muy grande", 400

    # -----------------------------
    # 5. Verificar imagen real
    # -----------------------------
    try:
        img = Image.open(foto)
        img.verify()  # estructura básica
        foto.seek(0)
        img = Image.open(foto)  # reopen real
    except UnidentifiedImageError:
        return "Archivo no es imagen", 400
    except Exception:
        return "Imagen corrupta", 400

    # -----------------------------
    # 6. Anti bomba de imagen
    # -----------------------------
    if img.width > MAX_WIDTH or img.height > MAX_HEIGHT:
        return "Resolución demasiado grande", 400

    if img.width * img.height > MAX_PIXELS:
        return "Imagen demasiado pesada", 400

    # -----------------------------
    # 7. Validar formato real
    # -----------------------------
    formato = (img.format or "").lower()

    if formato == "jpeg":
        formato = "jpg"

    if formato not in ALLOWED_FORMATS:
        return "Formato no permitido", 400

    # -----------------------------
    # 8. Generar nombre seguro
    # -----------------------------
    filename = f"{uuid.uuid4()}.{formato}"

    # -----------------------------
    # 9. RE-GUARDAR imagen limpia
    # elimina payload oculto, metadata, scripts
    # -----------------------------
    try:
        img = img.convert("RGB")

        temp_path = os.path.join("temp_uploads", filename)
        os.makedirs("temp_uploads", exist_ok=True)

        img.save(temp_path, "JPEG", quality=90, optimize=True)
    except Exception:
        return "Error procesando imagen", 500

    # -----------------------------
    # 10. Guardar en sistema
    # -----------------------------
    us = User(session["name"],get_user_ip())

    with open(temp_path, "rb") as f:
        us.upload_photo(f, name, filename)

    os.remove(temp_path)

    return redirect(url_for("home"))

@app.after_request
def secure_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Content-Security-Policy"] = "default-src * data: blob: 'unsafe-inline' 'unsafe-eval'; img-src * data: blob:;"
    return response


@app.errorhandler(413)
def too_large(e):
    return "La imagen supera el límite de 5MB", 413

@app.errorhandler(500)
def error_500(e):
    return render_template("error.html",error = "Error Interno, No es tu culpa, es de Joaquin")


def run_flask():
    app.run(port=40)

if __name__ == "__main__":
    run_flask()

