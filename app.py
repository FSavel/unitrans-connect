from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd

app = Flask(__name__)
app.secret_key = "unitrans_secret_key"

# =========================
# CONFIGURAÇÃO DO FICHEIRO
# =========================
# ALTERA AQUI SE USARES .csv ou .xlsx
FICHEIRO_DADOS = "unitrans.csv"

# =========================
# CARREGAR DADOS COM SEGURANÇA
# =========================
def carregar_dados():
    # Detecta automaticamente CSV ou Excel
    if FICHEIRO_DADOS.endswith(".csv"):
        df = pd.read_csv(FICHEIRO_DADOS)
    else:
        df = pd.read_excel(FICHEIRO_DADOS)

    # Evita erro com float64 ao preencher NaN
    obj_cols = df.select_dtypes(include=["object"]).columns
    df[obj_cols] = df[obj_cols].fillna("")

    return df

# =========================
# BUSCAR TRABALHADOR
# =========================
def buscar(codigo):
    df = carregar_dados()

    # normalizar código como string
    df["CODIGO"] = df["CODIGO"].astype(str)
    codigo = str(codigo)

    resultado = df[df["CODIGO"] == codigo]

    if resultado.empty:
        return None

    return resultado.iloc[0].to_dict()

# =========================
# ROTAS
# =========================

@app.route("/")
def home():
    return redirect(url_for("idioma"))

@app.route("/idioma/pt")
def idioma_pt():
    return render_template("idioma.html", lang="pt")

@app.route("/idioma/en")
def idioma_en():
    return render_template("idioma.html", lang="en")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        numero = request.form.get("codigo")

        user = buscar(numero)

        if user:
            session["user"] = user
            return redirect(url_for("menu"))
        else:
            return render_template("login.html", erro="Código inválido")

    return render_template("login.html")

@app.route("/menu")
def menu():
    if "user" not in session:
        return redirect(url_for("login"))

    return render_template("menu.html", user=session["user"])

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# =========================
# ERRO HANDLER (IMPORTANTE)
# =========================
@app.errorhandler(500)
def erro_interno(e):
    return "Erro interno no servidor. Verifique os logs.", 500

# =========================
# RUN LOCAL (IGNORADO NO RENDER)
# =========================
if __name__ == "__main__":
    app.run(debug=True)
