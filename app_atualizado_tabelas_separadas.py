
from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

try:
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='biblioteca'
    )
    print("✅ Conectado ao MySQL com sucesso!")
    conn.close()
except mysql.connector.Error as err:
    print("❌ Erro de conexão:", err)

app = Flask(__name__)

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'biblioteca'
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

@app.route('/')
def menu_redirect():
    return redirect('/menu')

@app.route('/menu')
def menu():
    return render_template('menu.html')

@app.route('/cadastrar_autor', methods=['GET', 'POST'])
def cadastrar_autor():
    if request.method == 'POST':
        nome = request.form['nome']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO autor (nome) VALUES (%s)", (nome,))
        conn.commit()
        conn.close()
        return redirect('/menu')
    return render_template('cadastrar_autor.html')

@app.route('/cadastrar_genero', methods=['GET', 'POST'])
def cadastrar_genero():
    if request.method == 'POST':
        nome = request.form['nome']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO genero (nome) VALUES (%s)", (nome,))
        conn.commit()
        conn.close()
        return redirect('/menu')
    return render_template('cadastrar_genero.html')

@app.route('/cadastrar_editora', methods=['GET', 'POST'])
def cadastrar_editora():
    if request.method == 'POST':
        nome = request.form['nome']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO editora (nome) VALUES (%s)", (nome,))
        conn.commit()
        conn.close()
        return redirect('/menu')
    return render_template('cadastrar_editora.html')


@app.route('/cadastrar')
def form():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT idautor, nome FROM autor")
    autores = cursor.fetchall()
    cursor.execute("SELECT idgenero, nome FROM genero")
    generos = cursor.fetchall()
    cursor.execute("SELECT ideditora, nome FROM editora")
    editoras = cursor.fetchall()
    conn.close()
    return render_template('form.html', autores=autores, generos=generos, editoras=editoras)

@app.route('/cadastrar', methods=['POST'])
def cadastrar():
    titulo = request.form['titulo']
    idautor = request.form['autor']
    idgenero = request.form['genero']
    ideditora = request.form['editora']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO livros (titulo, idautor, idgenero, ideditora) VALUES (%s, %s, %s, %s)",
        (titulo, idautor, idgenero, ideditora)
    )
    conn.commit()
    conn.close()

    return redirect('/livros')

@app.route('/livros')
def listar():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = '''
        SELECT l.id, l.titulo, a.nome AS autor, g.nome AS genero, e.nome AS editora
        FROM livros l
        JOIN autor a ON l.idautor = a.idautor
        JOIN genero g ON l.idgenero = g.idgenero
        JOIN editora e ON l.ideditora = e.ideditora
        WHERE 1=1
    '''

    filters = []
    params = []

    if request.args.get('titulo'):
        filters.append("LOWER(l.titulo) LIKE %s")
        params.append(f"%{request.args['titulo'].lower()}%")
    if request.args.get('autor'):
        filters.append("LOWER(a.nome) LIKE %s")
        params.append(f"%{request.args['autor'].lower()}%")
    if request.args.get('genero'):
        filters.append("LOWER(g.nome) LIKE %s")
        params.append(f"%{request.args['genero'].lower()}%")
    if request.args.get('editora'):
        filters.append("LOWER(e.nome) LIKE %s")
        params.append(f"%{request.args['editora'].lower()}%")

    if filters:
        query += " AND " + " AND ".join(filters)

    cursor.execute(query, tuple(params))
    livros = cursor.fetchall()
    conn.close()

    return render_template('lista.html', livros=livros)

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        titulo = request.form['titulo']
        idautor = request.form['autor']
        idgenero = request.form['genero']
        ideditora = request.form['editora']

        cursor.execute("""
            UPDATE livros
            SET titulo = %s, idautor = %s, idgenero = %s, ideditora = %s
            WHERE id = %s
        """, (titulo, idautor, idgenero, ideditora, id))
        conn.commit()
        conn.close()
        return redirect('/livros')

    # Buscar dados do livro
    cursor.execute("SELECT * FROM livros WHERE id = %s", (id,))
    livro_raw = cursor.fetchone()
    livro = {
        'id': livro_raw[0],
        'titulo': livro_raw[1],
        'idautor': livro_raw[2],
        'idgenero': livro_raw[3],
        'ideditora': livro_raw[4]
    }

    # Buscar autores, gêneros e editoras
    cursor.execute("SELECT idautor, nome FROM autor")
    autores = cursor.fetchall()

    cursor.execute("SELECT idgenero, nome FROM genero")
    generos = cursor.fetchall()

    cursor.execute("SELECT ideditora, nome FROM editora")
    editoras = cursor.fetchall()

    conn.close()

    return render_template('editar.html', livro=livro, autores=autores, generos=generos, editoras=editoras)


@app.route('/deletar/<int:id>')
def deletar(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM livros WHERE id = %s", (id,))
    conn.commit()
    conn.close()
    return redirect('/livros')

if __name__ == '__main__':
    app.run(debug=True)
