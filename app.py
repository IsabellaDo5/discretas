import os
import json
from flask import Flask, session, g, request, redirect, url_for, render_template, flash
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import create_engine
from flask import send_from_directory

app = Flask(__name__)

if __name__ =='__main__':  
    app.run(debug = True)  
# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")


#Para poder poner las imagenes
picFolder = os.path.join('static', 'pics')
app.config["UPLOAD_FOLDER"] = picFolder
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["JSONIFY_PRETTYPRINT_REGULAR"] = True
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

#La ruta para mandar imagenes
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

def login_required(f):
    """
    Decorate routes to require login.
    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

#Se ingresa a la ruta solo si esta logeado, ya que no ME DIJISTE xd
@app.route("/")
@login_required
def inicio():
    try:
        a = session["user_id"]
    except:
        return render_template("index.html")
    return render_template("index.html")

@app.route("/login", methods=["GET","POST"])
def login():
    #Aqui le pasamos la dirrecion de la imagen a esta variable
    #Flask es un despelote
    pic1 = os.path.join(app.config['UPLOAD_FOLDER'], 'login.png')
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = db.execute("SELECT * FROM users WHERE username = :username", {"username":username}).fetchall()
        
        if not username or not password:
            flash('Debe rellenar todos los campos')
            return render_template("login.html",user_image=pic1)
        if len(user) == 0:
            Error = 'Invalid credentials'
            flash('Nombre de usuario o contraseña inválidos')
            return render_template("login.html",user_image=pic1)
        if not check_password_hash(user[0]["password"], password):
            Error = 'Invalid credentials'
            flash('Nombre de usuario o contraseña inválidos')
            return render_template("login.html",user_image=pic1)

        session["user_id"] = user[0]["id"]
        id_user = session["user_id"]
        return render_template("index.html", user_image=pic1)
    else:    
        return render_template("login.html",user_image=pic1)

@app.route("/register", methods=["GET","POST"])
def register():
    pic1 = os.path.join(app.config['UPLOAD_FOLDER'], 'register.svg')
    if request.method == "POST":

        username = request.form.get("username")
        name = request.form.get("nombre")
        passw = request.form.get("contra")
        confirm = request.form.get("confirm")
        curso = int(request.form.get("cursos"))

        usernamedb = db.execute("SELECT username FROM users WHERE username = :username", {"username": username}).fetchall()

        if not username or not passw or not name or not confirm or not curso:
            flash('Debe rellenar todos los campos')
            return render_template("registro.html",user_image=pic1)

        for i in range(0, len(username)): 
            if username[i] == " ": 
                return render_template("registro.html",user_image=pic1)

        if confirm != passw:
            flash('Las contraseñas no coinciden')
            return render_template("registro.html",user_image=pic1)

        if len(usernamedb) != 0:
            flash('El nombre de usuario ya está en uso')
            return render_template("registro.html",user_image=pic1)

        if len(usernamedb) == 0 and passw == confirm:
            datos = db.execute("INSERT INTO users (username, password, name, curso) VALUES (:username,:password,:name, :curso) RETURNING id", { "username": username, "password" : generate_password_hash(passw), "name": name, "curso":curso}).fetchall()
            db.commit()
        return redirect("/")
    return render_template("registro.html", user1_image=pic1)

@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect("/")