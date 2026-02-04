from flask import Flask, render_template, request,Response,redirect,url_for,make_response
import os,time
from flask.globals import session
import random
from datos_activos.funciones_user_sqlite import User, Sqlite_create
import json


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

app = Flask(__name__)
app.secret_key = "3d16a60b798846cce41b578605ab9786e5b6da13e01e6f9d95c653e7512517bc"

app.config.update(
    SESSION_COOKIE_SAMESITE="None",
    SESSION_COOKIE_SECURE=True
)

def render(path, context = None):
    if context is None:
        context = {}
    return render_template(path, **context)

@app.route("/", methods=["POST","GET"])
def index(context = {}):

    name = session.get("name") or request.cookies.get("name")
    
    if not name:
        return redirect(url_for("login"))

    session["name"] = name
    
    
    return redirect(url_for("home"))

@app.route("/home", methods=["POST","GET"])
def home(context = {}):
    
    name = session.get("name") or request.cookies.get("name")
    
    if not name:
        return redirect(url_for("login"))

    session["name"] = name

    
    with open(r"C:\Users\Joaquin\Desktop\Matos Hub\static\uploads\opens.json","r") as read:
        datos = dict(json.load(read))
        
        foto, visitas = max(datos.items(), key=lambda item: item[1])
    
    nombre = session["name"]
    nombre = nombre.replace(" ","")
    user = User(nombre)

    context = {
        "imagenes": obtener_imagenes(r"C:\Users\Joaquin\Desktop\Matos Hub\static\uploads"),
        "vista" : foto
    }
    
    return render("home.html", context=context)


@app.route("/imagen-abierta", methods=["POST", "GET"])
def imagen_abierta():
    
    if request.method != "POST":
        return redirect(url_for("home"))
    
    data = request.get_json()
    img = data["imagen"]
    
    with open(r"C:\Users\Joaquin\Desktop\Matos Hub\static\uploads\opens.json","r") as read:
        datos = dict(json.load(read))
        if str(img) in datos.keys():
            datos[str(img)] += 1
        else:
            datos.update({str(img) : 1})
       
    with open(r"C:\Users\Joaquin\Desktop\Matos Hub\static\uploads\opens.json","w") as write:
        json.dump(datos,write, indent=1)

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

@app.route("/add", methods=["POST"])
def photo():
    name = request.form.get("name_photo", "")
    foto = request.files.get("foto", "")
    
    if foto and name and "name" in list(session.keys()) and foto.mimetype.startswith("image/"): # type: ignore
        extension = foto.filename.rsplit(".", 1)[1].lower() # type: ignore
        us = User(session["name"])
        us.upload_photo(foto,name,extension)
    
    return redirect(url_for("home"))


def run_flask():
    app.run(port=40)

if __name__ == "__main__":
    run_flask()
    
