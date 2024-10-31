from flask import Flask, render_template, redirect, url_for, jsonify, request
import pandas as pd
import sqlite3

app = Flask(__name__)

# Conectar ao banco de dados e criar a tabela se não houver
def init_db():
    conn = sqlite3.connect('alunos.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS alunos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        nota REAL NOT NULL
    )
    ''')
    conn.commit()
    conn.close()

def get_db_connection():
    """
    Faz a conecção com o banco de dados
    """
    conn = sqlite3.connect('alunos.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    """
    Renderiza a página index.
    """
    return render_template('index.html')

# Rota para a tabela de alunos
@app.route('/table')
def table():
    """
    Renderiza a página da tabela de alunos.

    Esta função busca os dados dos alunos armazenados no banco de dados,
    converte esses dados em uma lista de dicionários usando o método
    `to_dict(orient='records')`. Cada dicionário representa uma
    linha da tabela, para melhorar a iteração no Jinja2.
    """
    # Conectar ao banco de dados
    conn = get_db_connection()

    # Consultar dados da tabela
    cursor = conn.cursor()
    cursor.execute('SELECT id, nome, nota FROM alunos')
    rows = cursor.fetchall()

    # Converter os dados para um DataFrame
    df = pd.DataFrame(rows, columns=['id', 'alunos', 'notas'])

    # Fechar a conexão
    conn.close()

    return render_template('table.html', table_data=df.to_dict(orient='records'))

@app.route('/delete/<int:id>', methods=['POST'])
def delete_aluno(id):
    """
    Deleta alunos
    :param id: Id do aluno no banco de dados
    """
    conn = get_db_connection()
    conn.execute('DELETE FROM alunos WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('table'))  # Redireciona de volta para a tabela

@app.route('/edit/<int:id>')
def get_student(id):
    """
    Retorna os dados do aluno como JSON.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT nome, nota FROM alunos WHERE id = ?', (id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return jsonify({'alunos': row[0], 'notas': row[1]})
    return jsonify({'error': 'Aluno não encontrado'}), 404

@app.route('/update/<int:id>', methods=['POST'])
def update_student(id):
    """Atualiza a nota do aluno."""
    data = request.get_json()
    new_grade = data.get('notas')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE alunos SET nota = ? WHERE id = ?', (new_grade, id))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Nota atualizada com sucesso!'}), 200

@app.route('/add', methods=['PUT'])
def add_aluno():
    """
    Adiciona alunos
    """
    data = request.get_json()
    if 'alunos' not in data or 'notas' not in data:
        return jsonify({'message': 'Nome e nota são obrigatórios.'}), 400

    nome = data['alunos']
    nota = data['notas']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO alunos (nome, nota) VALUES (?, ?)', (nome, nota))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Aluno adicionado com sucesso!'}), 201

# Parâmetro para inicialização da aplicação
if __name__ == "__main__":
    init_db()
    app.run()
