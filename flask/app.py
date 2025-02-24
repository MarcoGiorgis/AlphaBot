import sqlite3
import hashlib
import datetime
import jwt
import alphabot
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, make_response

app = Flask(__name__)
app.config["SECRET_KEY"] = "chiave_super_segreta"
alpha = alphabot.AlphaBot()
alpha.stop()
mov = {"w":False, "a":False, "d":False, "s":False}
# Funzione per la connessione al database
def connectionDB():
    conn = sqlite3.connect('./mio_database.db', check_same_thread=False)
    cur = conn.cursor()
    return conn, cur

# Funzione per l'hashing delle password
def hash(psw):
    return hashlib.sha256(psw.encode()).hexdigest()

# Funzione per generare il token JWT
def generate_token(username):
    payload = {
        "user": username,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }
    token = jwt.encode(payload, app.config["SECRET_KEY"], algorithm="HS256")
    return token

# Funzione per impostare il token nei cookie
def generate_and_set_token(response, username):
    token = generate_token(username)
    response.set_cookie("token", token, max_age=3600, httponly=True)
    return response

# Decoratore per richiedere il token JWT
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get("token")
        if not token:
            return redirect(url_for("login"))
        try:
            decoded = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            current_user = decoded["user"]
        except jwt.ExpiredSignatureError:
            return redirect(url_for("login"))
        except jwt.InvalidTokenError:
            return redirect(url_for("login"))
        return f(current_user, *args, **kwargs)
    return decorated

# Funzione per il login
@app.route("/login", methods=["GET", "POST"])
def login():
    error = ""
    if request.method == "POST":
        username = request.form["e-mail"]
        password = request.form["password"]
        psw = hash(password)
        conn, cur = connectionDB()
        try:
            cur.execute("SELECT psw FROM utenti WHERE email = ?", (username,))
            p_user = cur.fetchone()
        finally:
            conn.close()
        if p_user and p_user[0] == psw:
            response = make_response(redirect(url_for("home")))
            return generate_and_set_token(response, username)
        else:
            error = "Nome utente o password errati."
    return render_template("login.html", error=error)

# Funzione per la creazione di un nuovo account
@app.route("/create_account", methods=["GET", "POST"])
def create_account():
    error = ""
    if request.method == "POST":
        username = request.form["e-mail"]
        password = request.form["password"]
        conn, cur = connectionDB()
        try:
            cur.execute("SELECT psw FROM utenti WHERE email = ?", (username,))
            if cur.fetchone():
                error = "Utente già registrato."
            else:
                psw = hash(password)
                cur.execute("INSERT INTO utenti (email, psw) VALUES (?, ?)", (username, psw))
                conn.commit()
        finally:
            conn.close()
        if not error:
            return redirect(url_for("login"))
    return render_template("create_account.html", error=error)

# Funzione della home con i comandi per l'alphabot, il logout e il controllo di autenticazione degli utenti con i token
@app.route("/", methods=["GET", "POST"])
@token_required
def home(current_user):
    global mov
    if request.method == "POST":
        if request.form.get("log-out") == "logout":
            alpha.stop()
            response = make_response(redirect(url_for("login")))
            response.delete_cookie("token")
            return response

        for key in mov.keys():
            if request.form.get(key):
                mov = {"w":False, "a":False, "d":False, "s":False}
                mov[key] = True
        if request.form.get("stop") == "stop":
            print("stop")
            mov = {"w":False, "a":False, "d":False, "s":False}

        if mov["w"]:
            print("avanti")
            alpha.setMotor(-100, 100)
        elif mov["s"]:
            print("indietro")
            alpha.setMotor(100, -100)
        elif mov["a"]:
            print("sinistra")
            alpha.setMotor(100, 100)
        elif mov["d"]:
            print("destra")
            alpha.setMotor(-100, -100)
        else:
            alpha.stop()

    return render_template("home.html", username=current_user)

if __name__ == "__main__":
    app.run(debug=True, host="192.168.1.132", port="5001")