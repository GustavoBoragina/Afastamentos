from flask import Flask, request, redirect, render_template_string
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)

# Inicializa o banco
def init_db():
    conn = sqlite3.connect('banco.db')
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS afastamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            tipo TEXT,
            motivo TEXT,
            data_inicio TEXT,
            data_fim TEXT,
            dias INTEGER
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Página principal
@app.route('/')
def index():
    conn = sqlite3.connect('banco.db')
    afastamentos = conn.execute('SELECT * FROM afastamentos ORDER BY data_inicio DESC').fetchall()
    totais = conn.execute('SELECT nome, SUM(dias) FROM afastamentos GROUP BY nome').fetchall()
    conn.close()
    
    # HTML embutido
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Afastamentos</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body { font-size: 12px; }
            table { font-size: 11px; }
            input, select { font-size: 11px !important; padding: 2px 4px; }
            td, th { white-space: nowrap; vertical-align: middle; }
            .form-control { height: 28px; }
        </style>
    </head>
    <body class="p-4">
        <h4 class="mb-3">Registrar Afastamento</h4>
        <form method="POST" action="/registrar_afastamento" class="mb-4">
            <div class="row">
                <div class="col"><input name="nome" class="form-control" placeholder="Nome" required></div>
                <div class="col"><input name="tipo" class="form-control" placeholder="Tipo" required></div>
                <div class="col"><input name="motivo" class="form-control" placeholder="Motivo" required></div>
                <div class="col"><input name="data_inicio" type="date" class="form-control" required></div>
                <div class="col"><input name="dias" type="number" class="form-control" placeholder="Dias" required></div>
                <div class="col"><button class="btn btn-success w-100">Registrar</button></div>
            </div>
        </form>

        <h4 class="mb-2">Lista de Afastamentos</h4>
        <table class="table table-bordered table-sm">
            <thead class="table-light">
                <tr>
                    <th>Nome</th>
                    <th>Tipo</th>
                    <th>Motivo</th>
                    <th>Início</th>
                    <th>Fim</th>
                    <th>Dias</th>
                    <th>Ação</th>
                </tr>
            </thead>
            <tbody>
                {% for a in afastamentos %}
                <tr>
                    <form method="POST" action="/editar_afastamento/{{ a[0] }}">
                        <td><input name="nome" value="{{ a[1] }}" class="form-control" required></td>
                        <td><input name="tipo" value="{{ a[2] }}" class="form-control" required></td>
                        <td><input name="motivo" value="{{ a[3] }}" class="form-control" required></td>
                        <td><input name="data_inicio" value="{{ a[4] }}" type="date" class="form-control" required></td>
                        <td><input name="dias" value="{{ a[6] }}" type="number" class="form-control" required></td>
                        <td>{{ a[6] }}</td>
                        <td><button class="btn btn-warning btn-sm">Salvar</button></td>
                    </form>
                </tr>
                {% endfor %}
            </tbody>
        </table>

        <h4 class="mt-4">Total de Dias Afastados por Colaborador</h4>
        <table class="table table-striped table-sm">
            <tr>
                <th>Colaborador</th>
                <th>Dias Afastados</th>
            </tr>
            {% for t in totais %}
                <tr>
                    <td>{{ t[0] }}</td>
                    <td>{{ t[1] }}</td>
                </tr>
            {% endfor %}
        </table>
    </body>
    </html>
    '''
    return render_template_string(html, afastamentos=afastamentos, totais=totais)

# Registrar novo afastamento
@app.route('/registrar_afastamento', methods=['POST'])
def registrar_afastamento():
    nome = request.form['nome']
    tipo = request.form['tipo']
    motivo = request.form['motivo']
    data_inicio = request.form['data_inicio']
    dias = int(request.form['dias'])
    data_fim = (datetime.strptime(data_inicio, "%Y-%m-%d") + timedelta(days=dias - 1)).strftime("%Y-%m-%d")

    conn = sqlite3.connect('banco.db')
    conn.execute('''
        INSERT INTO afastamentos (nome, tipo, motivo, data_inicio, data_fim, dias)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (nome, tipo, motivo, data_inicio, data_fim, dias))
    conn.commit()
    conn.close()
    return redirect('/')

# Editar afastamento
@app.route('/editar_afastamento/<int:id>', methods=['POST'])
def editar_afastamento(id):
    nome = request.form['nome']
    tipo = request.form['tipo']
    motivo = request.form['motivo']
    data_inicio = request.form['data_inicio']
    dias = int(request.form['dias'])
    data_fim = (datetime.strptime(data_inicio, "%Y-%m-%d") + timedelta(days=dias - 1)).strftime("%Y-%m-%d")

    conn = sqlite3.connect('banco.db')
    conn.execute('''
        UPDATE afastamentos
        SET nome = ?, tipo = ?, motivo = ?, data_inicio = ?, data_fim = ?, dias = ?
        WHERE id = ?
    ''', (nome, tipo, motivo, data_inicio, data_fim, dias, id))
    conn.commit()
    conn.close()
    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=81)
