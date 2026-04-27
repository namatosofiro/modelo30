#!/usr/bin/env python3
"""
Modelo 30 — Web Interface
Flask app para gestão de fornecedores não residentes (AT Portugal)
"""

import io
import csv
from datetime import datetime
from flask import (Flask, render_template, request, redirect,
                   url_for, flash, send_file, jsonify)
from modelo30 import (
    init_db, seed_fornecedores, get_db,
    adicionar_fornecedor, atualizar_fornecedor, desativar_fornecedor,
    registar_pagamento, TIPOS_RENDIMENTO, PAISES
)

app = Flask(__name__)
app.secret_key = "m30-eter-2026"

# Países com CDT em vigor com Portugal (lista actualizada OCDE)
CDT_PAISES = {
    "AT","BE","BG","CA","CY","CZ","CN","HR","DK","EE","FI","FR","DE",
    "GR","HU","IE","IL","IT","JP","KR","LV","LT","LU","MT","MX","MU",
    "NL","NO","PL","RO","RU","SG","SK","SI","ES","SE","CH","TR","GB",
    "US","AE","AU","BR","IN","ZA","CL","CO","AR","NZ","HK",
}

MESES = [
    (1,"Janeiro"),(2,"Fevereiro"),(3,"Março"),(4,"Abril"),
    (5,"Maio"),(6,"Junho"),(7,"Julho"),(8,"Agosto"),
    (9,"Setembro"),(10,"Outubro"),(11,"Novembro"),(12,"Dezembro"),
]


def _stats():
    conn = get_db()
    ano = datetime.now().year
    total_forn = conn.execute("SELECT COUNT(*) FROM fornecedores WHERE ativo=1").fetchone()[0]
    total_pag  = conn.execute("SELECT COUNT(*) FROM pagamentos").fetchone()[0]
    r = conn.execute("SELECT SUM(valor_bruto), SUM(retencao) FROM pagamentos WHERE ano=?", (ano,)).fetchone()
    total_bruto = r[0] or 0
    total_ret   = r[1] or 0

    por_cat = conn.execute(
        "SELECT categoria, COUNT(*) n FROM fornecedores WHERE ativo=1 "
        "GROUP BY categoria ORDER BY n DESC LIMIT 12"
    ).fetchall()

    por_pais_raw = conn.execute(
        "SELECT pais_codigo, COUNT(*) n FROM fornecedores WHERE ativo=1 "
        "GROUP BY pais_codigo ORDER BY n DESC LIMIT 10"
    ).fetchall()
    por_pais = [(r["pais_codigo"], PAISES.get(r["pais_codigo"], r["pais_codigo"]), r["n"])
                for r in por_pais_raw]
    conn.close()
    return dict(total_forn=total_forn, total_pag=total_pag,
                total_bruto=total_bruto, total_ret=total_ret,
                por_categoria=por_cat, por_pais=por_pais)


# ─────────────────────────────────────────────────────────────────────────────
# ROTAS
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html", stats=_stats(), ano_atual=datetime.now().year)


@app.route("/fornecedores")
def fornecedores():
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM fornecedores WHERE ativo=1 ORDER BY nome"
    ).fetchall()
    cats = [r[0] for r in conn.execute(
        "SELECT DISTINCT categoria FROM fornecedores WHERE ativo=1 AND categoria IS NOT NULL ORDER BY categoria"
    ).fetchall()]
    paises_usados = [r[0] for r in conn.execute(
        "SELECT DISTINCT pais_codigo FROM fornecedores WHERE ativo=1 ORDER BY pais_codigo"
    ).fetchall()]
    conn.close()
    return render_template("fornecedores.html", fornecedores=rows,
                           categorias=cats, paises_usados=paises_usados,
                           paises=PAISES, tipos=TIPOS_RENDIMENTO)


@app.route("/fornecedor/novo", methods=["GET", "POST"])
def novo_fornecedor():
    conn = get_db()
    cats = [r[0] for r in conn.execute(
        "SELECT DISTINCT categoria FROM fornecedores WHERE ativo=1 AND categoria IS NOT NULL ORDER BY categoria"
    ).fetchall()]
    conn.close()
    if request.method == "POST":
        dados = {
            "nome": request.form["nome"].strip(),
            "nome_comercial": request.form.get("nome_comercial", "").strip() or None,
            "nif_pt": request.form.get("nif_pt", "").strip() or None,
            "nif_pais": request.form.get("nif_pais", "").strip() or None,
            "pais_codigo": request.form["pais_codigo"].upper(),
            "tipo_rendimento": request.form["tipo_rendimento"].upper(),
            "taxa_cdt": float(request.form.get("taxa_cdt") or 0),
            "taxa_domestica": float(request.form.get("taxa_domestica") or 25),
            "percentagem_participacao": float(request.form.get("percentagem_participacao") or 0),
            "categoria": request.form.get("categoria", "").strip() or None,
            "notas": request.form.get("notas", "").strip() or None,
        }
        fid = adicionar_fornecedor(dados)
        flash(f"Fornecedor '{dados['nome']}' adicionado (ID {fid}).", "success")
        return redirect(url_for("fornecedores"))
    return render_template("fornecedor_form.html", forn=None,
                           paises=PAISES, tipos=TIPOS_RENDIMENTO, categorias=cats)


@app.route("/fornecedor/<int:fid>/editar", methods=["GET", "POST"])
def editar_fornecedor(fid):
    conn = get_db()
    forn = conn.execute("SELECT * FROM fornecedores WHERE id=?", (fid,)).fetchone()
    cats = [r[0] for r in conn.execute(
        "SELECT DISTINCT categoria FROM fornecedores WHERE ativo=1 AND categoria IS NOT NULL ORDER BY categoria"
    ).fetchall()]
    conn.close()
    if not forn:
        flash("Fornecedor não encontrado.", "error")
        return redirect(url_for("fornecedores"))
    if request.method == "POST":
        dados = {
            "nome": request.form["nome"].strip(),
            "nome_comercial": request.form.get("nome_comercial", "").strip() or None,
            "nif_pt": request.form.get("nif_pt", "").strip() or None,
            "nif_pais": request.form.get("nif_pais", "").strip() or None,
            "pais_codigo": request.form["pais_codigo"].upper(),
            "tipo_rendimento": request.form["tipo_rendimento"].upper(),
            "taxa_cdt": float(request.form.get("taxa_cdt") or 0),
            "taxa_domestica": float(request.form.get("taxa_domestica") or 25),
            "percentagem_participacao": float(request.form.get("percentagem_participacao") or 0),
            "categoria": request.form.get("categoria", "").strip() or None,
            "notas": request.form.get("notas", "").strip() or None,
        }
        atualizar_fornecedor(fid, dados)
        flash("Fornecedor actualizado.", "success")
        return redirect(url_for("fornecedores"))
    return render_template("fornecedor_form.html", forn=forn,
                           paises=PAISES, tipos=TIPOS_RENDIMENTO, categorias=cats)


@app.route("/fornecedor/<int:fid>/remover", methods=["POST"])
def remover_fornecedor(fid):
    conn = get_db()
    forn = conn.execute("SELECT nome FROM fornecedores WHERE id=?", (fid,)).fetchone()
    conn.close()
    if forn:
        desativar_fornecedor(fid)
        flash(f"'{forn['nome']}' removido.", "success")
    return redirect(url_for("fornecedores"))


@app.route("/pagamentos", methods=["GET", "POST"])
def pagamentos():
    agora = datetime.now()
    if request.method == "POST":
        dados = {
            "fornecedor_id": int(request.form["fornecedor_id"]),
            "ano":  int(request.form["ano"]),
            "mes":  int(request.form["mes"]),
            "valor_bruto": float(request.form["valor_bruto"]),
            "taxa_aplicada": float(request.form["taxa_aplicada"]),
            "retencao": 0,
            "regime": request.form.get("regime", "CDT"),
            "notas": request.form.get("notas", "").strip() or None,
        }
        pid = registar_pagamento(dados)
        flash(f"Pagamento registado (ID {pid}).", "success")
        return redirect(url_for("pagamentos"))

    ano_sel = int(request.args.get("ano", agora.year))
    mes_sel_raw = request.args.get("mes", "")
    mes_sel = int(mes_sel_raw) if mes_sel_raw else None

    conn = get_db()
    q = """SELECT p.*, f.nome, f.nome_comercial, f.pais_codigo, f.tipo_rendimento
           FROM pagamentos p JOIN fornecedores f ON p.fornecedor_id=f.id
           WHERE p.ano=?"""
    params = [ano_sel]
    if mes_sel:
        q += " AND p.mes=?"; params.append(mes_sel)
    q += " ORDER BY p.ano DESC, p.mes DESC, f.nome"
    pags = conn.execute(q, params).fetchall()

    todos = conn.execute(
        "SELECT id, nome, nome_comercial, pais_codigo, taxa_cdt, taxa_domestica "
        "FROM fornecedores WHERE ativo=1 ORDER BY nome"
    ).fetchall()
    anos = [r[0] for r in conn.execute(
        "SELECT DISTINCT ano FROM pagamentos ORDER BY ano DESC"
    ).fetchall()] or [agora.year]
    if agora.year not in anos:
        anos.insert(0, agora.year)
    conn.close()

    total_bruto = sum(p["valor_bruto"] for p in pags)
    total_ret   = sum(p["retencao"] for p in pags)

    return render_template("pagamentos.html",
                           pagamentos=pags, todos_fornecedores=todos,
                           anos=anos, meses=MESES,
                           ano_sel=ano_sel, mes_sel=mes_sel,
                           ano_atual=agora.year, mes_atual=agora.month,
                           total_bruto=total_bruto, total_ret=total_ret)


@app.route("/exportar", methods=["GET", "POST"])
def exportar():
    agora = datetime.now()
    if request.method == "POST":
        ano = int(request.form["ano"])
        mes_raw = request.form.get("mes", "")
        mes = int(mes_raw) if mes_raw else None
        return _gerar_csv(ano, mes)
    return render_template("exportar.html", meses=MESES, ano_atual=agora.year)


@app.route("/exportar/direto")
def exportar_direto():
    ano = int(request.args.get("ano", datetime.now().year))
    mes_raw = request.args.get("mes", "")
    mes = int(mes_raw) if mes_raw else None
    return _gerar_csv(ano, mes)


def _gerar_csv(ano: int, mes: int | None):
    conn = get_db()
    q = """SELECT p.*, f.nif_pt, f.nif_pais, f.pais_codigo, f.tipo_rendimento,
                  f.percentagem_participacao, f.nome, f.nome_comercial
           FROM pagamentos p JOIN fornecedores f ON p.fornecedor_id=f.id
           WHERE p.ano=?"""
    params = [ano]
    if mes:
        q += " AND p.mes=?"; params.append(mes)
    rows = conn.execute(q, params).fetchall()
    conn.close()

    buf = io.StringIO()
    w = csv.writer(buf, delimiter=";")
    w.writerow(["Campo31_NIF_PT","Campo32_NIF_Pais","Campo33_Pais",
                "Campo34_Participacao_%","Campo35_Tipo_Rendimento",
                "Campo35_Valor_Bruto_EUR","Campo36_Taxa_%",
                "Campo37_Retencao_EUR","Regime","Ano","Mes",
                "Fornecedor","Notas"])
    for r in rows:
        w.writerow([
            r["nif_pt"] or "",
            r["nif_pais"] or "",
            r["pais_codigo"],
            str(r["percentagem_participacao"]).replace(".", ","),
            r["tipo_rendimento"],
            str(r["valor_bruto"]).replace(".", ","),
            str(r["taxa_aplicada"]).replace(".", ","),
            str(r["retencao"]).replace(".", ","),
            r["regime"],
            r["ano"], r["mes"],
            r["nome"],
            r["notas"] or "",
        ])

    buf.seek(0)
    fname = f"modelo30_{ano}_{mes:02d}.csv" if mes else f"modelo30_{ano}.csv"
    return send_file(
        io.BytesIO(("﻿" + buf.read()).encode("utf-8")),
        mimetype="text/csv",
        as_attachment=True,
        download_name=fname,
    )


@app.route("/exportar/json")
def exportar_json():
    import json
    conn = get_db()
    rows = conn.execute("SELECT * FROM fornecedores WHERE ativo=1 ORDER BY nome").fetchall()
    conn.close()
    data = json.dumps([dict(r) for r in rows], ensure_ascii=False, indent=2)
    return send_file(
        io.BytesIO(data.encode("utf-8")),
        mimetype="application/json",
        as_attachment=True,
        download_name="fornecedores_modelo30.json",
    )


@app.route("/paises")
def paises():
    conn = get_db()
    contagem = {r["pais_codigo"]: r["n"] for r in conn.execute(
        "SELECT pais_codigo, COUNT(*) n FROM fornecedores WHERE ativo=1 GROUP BY pais_codigo"
    ).fetchall()}
    conn.close()
    info = sorted([
        (cod, nome, cod in CDT_PAISES, contagem.get(cod, 0))
        for cod, nome in PAISES.items()
    ], key=lambda x: x[1])
    return render_template("paises.html", paises_info=info)


# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    init_db()
    seed_fornecedores()
    print("\n  Modelo 30 a correr em → http://localhost:5050\n")
    app.run(debug=True, port=5050)
