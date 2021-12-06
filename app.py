import sqlite3
from flask import Flask, render_template, redirect, url_for, flash, request, session
from werkzeug.exceptions import abort
from utils import *

app = Flask(__name__)
app.secret_key = b'\xf85~.("^\xee\r\xf20OF\xbaC\xff'


def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


def get_produto(produto_id):
    conn = get_db_connection()
    sql = f'SELECT * FROM estoque WHERE id = {produto_id}'
    produto = conn.execute(sql).fetchone()
    conn.close()
    if produto is None:
        abort(404)
    return produto


def carrinho_itens():
    if 'pedidos' in session:
        pedidos = session['pedidos']
        return len(pedidos)
    else:
        return 0


def is_logged_out():
    return 'email' not in session


@app.route('/')
def home():
    if is_logged_out():
        session.pop('pedidos', None)
    return render_template('home.html')


@app.route('/produtos')
def produtos():
    if is_logged_out():
        return redirect(url_for('login'))

    produtos = None
    resultado = ""
    if request.args.get('query', None):
        query = request.args['query']
        conn = get_db_connection()
        sql = "SELECT e.*, f.nome AS farmacia FROM estoque AS e INNER JOIN farmacia AS f ON e.farmacia_id = f.id WHERE produto LIKE '%"+query+"%'"
        produtos = conn.execute(sql).fetchall()
        if not produtos:
            resultado = "Nenhum produto encontrado!"
        conn.close()

    return render_template('produtos.html', produtos=produtos, resultado=resultado)


@app.route('/produto/<int:produto_id>')
def produto(produto_id):
    if is_logged_out():
        return redirect(url_for('login'))

    produto = get_produto(produto_id)
    return render_template('produto.html', produto=produto)


@app.route('/carrinho', methods=['GET', 'POST'])
def carrinho():
    if is_logged_out():
        return redirect(url_for('login'))

    if request.method == 'POST':
        task = request.form['task']
        if (task == "add"):
            produto_id = int(request.form['produto_id'])
            produto = get_produto(produto_id)
            if produto:
                if 'pedidos' in session:
                    pedidos = session['pedidos']
                else:
                    pedidos = []
                session['pedidos'] = add_pedido(pedidos, produto)
        elif (task == "mod"):
            pedido_id = int(request.form['pedido_id'])
            nitens = int(request.form[f'nitens{pedido_id}'])
            session['pedidos'] = update_pedido(
                session['pedidos'], pedido_id, nitens)

    if carrinho_itens() == 0:
        return render_template('produtos.html')
    else:
        pedidos = session['pedidos']
        return render_template('carrinho.html', pedidos=pedidos, total_geral=get_total_pedidos(pedidos))


@ app.route('/addusuario', methods=['GET', 'POST'])
def addusuario():
    if request.method == 'POST':
        nome = request.form['nome']
        endereco = request.form['endereco']
        celular = request.form['celular']
        email = request.form['email']
        senha = request.form['senha']
        if not nome:
            flash('O nome é requerido!', 'danger')
        else:
            conn = get_db_connection()
            conn.execute('INSERT INTO usuario (nome, endereco, celular, email, senha) VALUES (?, ?, ?, ?, ?)',
                         (nome, endereco, celular, email, senha))
            conn.commit()
            conn.close()
            flash('Usuário cadastrado com sucesso!', 'success')
            return redirect(url_for('home'))

    return render_template('cadusuario.html')


@ app.route('/addfarma', methods=['GET', 'POST'])
def addfarma():
    if request.method == 'POST':
        nome = request.form['nome']
        endereco = request.form['endereco']
        cnpj = request.form['cnpj']
        email = request.form['email']
        senha = request.form['senha']
        if not nome:
            flash('O nome é requerido!', 'danger')
        else:
            conn = get_db_connection()
            conn.execute('INSERT INTO farmacia (nome, endereco, cnpj, email, senha) VALUES (?, ?, ?, ?, ?)',
                         (nome, endereco, cnpj, email, senha))
            conn.commit()
            conn.close()
            flash('Farmácia cadastrada com sucesso!', 'success')
            return redirect(url_for('home'))

    return render_template('cadfarma.html')


@ app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        conn = get_db_connection()
        usuarios = conn.execute('SELECT * FROM usuario').fetchall()
        conn.close()
        found = False
        for usuario in usuarios:
            if request.form['email'] == usuario['email'] and request.form['senha'] == usuario['senha']:
                found = True
                break
        if found:
            session['email'] = request.form['email']
            return redirect(url_for('produtos'))
        else:
            error = 'Senha inválida. Tente novamente.'

    return render_template('login.html', error=error)


@ app.route('/logout')
def logout():
    session.pop('email', None)
    session.pop('pedidos', None)
    return redirect(url_for('home'))


app.jinja_env.globals.update(is_logged_out=is_logged_out)
app.jinja_env.globals.update(number2real=number2real)
app.jinja_env.globals.update(carrinho_itens=carrinho_itens)

if __name__ == '__main__':
    app.run(debug=True)
