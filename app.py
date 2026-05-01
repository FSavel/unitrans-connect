from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd
import os

app = Flask(__name__)
app.secret_key = "unitrans2026"

ARQUIVO = "Unitrans.csv"

# =========================
# TRADUÇÕES
# =========================
LANG = {
    "pt": {
        "menu_profile": "Meu Perfil",
        "menu_leave": "Férias e Faltas",
        "menu_comms": "Comunicados",
        "menu_rh": "Contactar RH",
        "menu_logout": "Sair",
        "welcome": "Bem-vindo à Unitrans Connect",
        "login_title": "Entrar no Sistema",
        "login_button": "Entrar",
        "login_error": "Número não encontrado"
    },
    "en": {
        "menu_profile": "My Profile",
        "menu_leave": "Leave & Absences",
        "menu_comms": "Announcements",
        "menu_rh": "Contact HR",
        "menu_logout": "Logout",
        "welcome": "Welcome to Unitrans Connect",
        "login_title": "System Login",
        "login_button": "Login",
        "login_error": "Worker number not found"
    }
}

# =========================
# DADOS
# =========================
def carregar_dados():
    df = pd.read_csv(ARQUIVO)
    df.fillna("", inplace=True)
    return df

def buscar(numero):
    df = carregar_dados()
    user = df[df["Numero do trabalhador"].astype(str) == str(numero)]
    if user.empty:
        return None
    return user.iloc[0].to_dict()

# =========================
# HOME
# =========================
@app.route("/")
def home():
    return render_template("idioma.html")

# =========================
# SET IDIOMA
# =========================
@app.route("/idioma/<lang>")
def idioma(lang):
    session["lang"] = lang
    return redirect("/login")

# =========================
# LOGIN
# =========================
@app.route("/login", methods=["GET", "POST"])
def login():

    lang = session.get("lang", "pt")
    t = LANG[lang]

    erro = ""

    if request.method == "POST":
        numero = request.form["numero"]
        user = buscar(numero)

        if user:
            session["numero"] = numero
            return redirect("/menu")
        else:
            erro = t["login_error"]

    return render_template("login.html", erro=erro, t=t)

# =========================
# MENU
# =========================
@app.route("/menu")
def menu():

    if "numero" not in session:
        return redirect("/login")

    lang = session.get("lang", "pt")
    t = LANG[lang]

    user = buscar(session["numero"])

    return render_template("menu.html", user=user, t=t)

# =========================
# PERFIL
# =========================
@app.route("/perfil")
def perfil():
    if "numero" not in session:
        return redirect("/login")

    user = buscar(session["numero"])
    return render_template("perfil.html", user=user)

# =========================
# FÉRIAS
# =========================
@app.route("/ferias")
def ferias():
    if "numero" not in session:
        return redirect("/login")

    user = buscar(session["numero"])
    return render_template("ferias.html", user=user)

# =========================
# COMUNICADOS
# =========================
@app.route("/comunicados")
def comunicados():
    return render_template("comunicados.html")

# =========================
# RH
# =========================
@app.route("/rh")
def rh():
    return render_template("rh.html")

# =========================
# LOGOUT
# =========================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# =========================
# RUN
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
