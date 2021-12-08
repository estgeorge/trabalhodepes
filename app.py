import sqlite3
from flask import Flask, render_template, redirect, url_for, flash, request, session
from flask_paginate import Pagination
from werkzeug.exceptions import abort
from utils import *
# from flask_paginate import Pagination

app = Flask(__name__)
app.secret_key = b'\xf85~.("^\xee\r\xf20OF\xbaC\xff'


@app.route('/produtos')
def produtos():
    if is_logged_out():
        return redirect(url_for('login'))

    produtos = None
    resultado = ""
    if request.args.get('search', None):
        search = request.args['search'].strip()
        conn = get_db_connection()
        query = f"""SELECT e.*, f.nome AS farmacia FROM estoque AS e
                    INNER JOIN farmacia AS f ON e.farmacia_id = f.id
                    WHERE produto LIKE '%{search}%'"""
        produtos = conn.execute(query).fetchall()
        if not produtos:
            resultado = "Nenhum produto encontrado!"
        conn.close()

    return render_template('produtos.html', produtos=produtos, resultado=resultado)


@app.route('/produto/<produto_id>', methods=['GET', 'POST'])
def produto(produto_id):
    if is_logged_out():
        return redirect(url_for('login'))

    produto = get_produto(produto_id)

    if request.method == 'POST':

        if ('token' in request.form):
            token = request.form['token']
        else:
            token = ""

        if 'pedidos' in session:
            session['pedidos'] = add_pedido(session['pedidos'], produto, token)
        else:
            session['pedidos'] = add_pedido([], produto, token)
        return redirect(url_for('carrinho'))

    return render_template('produto.html', produto=produto)


@app.route('/carrinho', methods=['GET', 'POST'])
def carrinho():
    if is_logged_out():
        return redirect(url_for('login'))

    if request.method == 'POST':
        task = request.form['task']
        if (task == "update"):
            pedido_id = int(request.form['pedido_id'])
            try:
                nitens = int(request.form[f'nitens{pedido_id}'])
            except ValueError:
                nitens = 0
            if check_prescricao(session['pedidos'], pedido_id):
                flash(
                    'Não é possível alterar quantidade de produto com prescrição digital!', 'danger')
            else:
                session['pedidos'] = update_pedido(
                    session['pedidos'], pedido_id, nitens)
        elif (task == "delete"):
            pedido_id = int(request.form['pedido_id'])
            session['pedidos'] = delete_pedido(
                session['pedidos'], pedido_id)

    if carrinho_itens() == 0:
        return render_template('produtos.html')
    else:
        pedidos = session['pedidos']
        return render_template('carrinho.html', pedidos=pedidos, total_geral=get_total_pedidos(pedidos))


@app.route('/pagamento', methods=['GET', 'POST'])
def pagamento():
    if is_logged_out():
        return redirect(url_for('login'))
    if request.method == 'POST':
        pass
    return render_template('pagamento.html')


@app.route('/farmacia', methods=['GET', 'POST'])
@app.route('/farmacia/<int:offset>', methods=['GET', 'POST'])
def farmacia(offset=0):
    if is_logged_out_farm():
        return redirect(url_for('login'))

    page = request.args.get('page', type=int, default=1)
    per_page = 5
    offset = (page - 1) * per_page

    farmacia = getFarmacia()
    farmacia_id = farmacia['id']
    query = f"""SELECT e.* FROM estoque As e 
                WHERE farmacia_id = {farmacia_id} 
                ORDER BY e.produto LIMIT {per_page} OFFSET {offset}"""
    conn = get_db_connection()
    estoque = conn.execute(query).fetchall()
    count = conn.execute(f"""SELECT COUNT(*) AS total FROM estoque 
                         WHERE farmacia_id = {farmacia_id}""").fetchone()
    conn.close()

    pagination = Pagination(page=page, per_page=per_page,
                            total=count['total'], css_framework='bootstrap5')
    return render_template('farmacia.html', estoque=estoque, pagination=pagination)


@app.route('/estoque/add', methods=['GET', 'POST'])
def estoque_add():
    if is_logged_out_farm():
        return redirect(url_for('login'))

    farmacia = getFarmacia()
    farmacia_id = farmacia['id']

    if request.method == 'POST':
        produto = request.form['produto'].strip()
        preco = request.form['preco'].strip()
        qtd = int(request.form['qtd'].strip())

        success = True
        if not produto:
            flash('O nome é requerido!', 'danger')
            success = False

        if not preco:
            flash('O preco é requerido!', 'danger')
            success = False

        if not qtd:
            flash('A quantidade é requerida!', 'danger')
            success = False
        else:
            if qtd < 0:
                flash('A quantidade não pode ser número negativo!', 'danger')
                success = False

        if success:
            conn = get_db_connection()
            conn.execute('INSERT INTO estoque (produto, preco, qtd, farmacia_id) VALUES (?, ?, ?, ?)',
                         (produto, preco, qtd, farmacia_id))
            conn.commit()
            conn.close()
            flash('Produto adicionado com sucesso!', 'success')
            return redirect(url_for('farmacia'))

    return render_template('estoque_add.html')


@app.route('/estoque/edit/<int:produto_id>', methods=['GET', 'POST'])
def estoque_edit(produto_id):
    if is_logged_out_farm():
        return redirect(url_for('login'))

    estoque_item = get_produto(produto_id)
    farmacia = getFarmacia()
    if (farmacia['id'] != estoque_item['farmacia_id']):
        abort(404)

    if (estoque_item['prescricao']):
        prescricao_checked = "checked"
    else:
        prescricao_checked = ""

    if request.method == 'POST':
        produto = request.form['produto'].strip()
        preco = request.form['preco'].strip()
        qtd = int(request.form['qtd'].strip())

        if ('prescricao' in request.form):
            prescricao_checked = "checked"
            prescricao = 1
        else:
            prescricao_checked = ""
            prescricao = 0

        success = True
        if not produto:
            flash('O nome é requerido!', 'danger')
            success = False

        if not preco:
            flash('O preco é requerido!', 'danger')
            success = False

        if not qtd:
            flash('A quantidade é requerida!', 'danger')
            success = False
        else:
            if qtd < 0:
                flash('A quantidade não pode ser número negativo!', 'danger')
                success = False

        if success:
            conn = get_db_connection()
            conn.execute('UPDATE estoque SET produto=?, preco=?, qtd=?, prescricao=? WHERE id = ?',
                         (produto, preco, qtd, prescricao, produto_id))
            conn.commit()
            conn.close()
            flash('Produto atualizado com sucesso!', 'success')
            return redirect(url_for('farmacia'))

    return render_template('estoque_edit.html', estoque_item=estoque_item, prescricao_checked=prescricao_checked)


@app.route('/estoque/delete/<int:produto_id>', methods=['GET', 'POST'])
def estoque_delete(produto_id):
    if is_logged_out_farm():
        return redirect(url_for('login'))

    estoque_item = get_produto(produto_id)
    farmacia = getFarmacia()
    if (farmacia['id'] != estoque_item['farmacia_id']):
        abort(404)

    conn = get_db_connection()
    conn.execute('DELETE FROM estoque WHERE id = ?', (produto_id,))
    conn.commit()
    conn.close()
    flash('Produto deletado com sucesso!', 'success')
    return redirect(url_for('farmacia'))


@ app.route('/')
def home():
    return render_template('home.html')


@ app.route('/addusuario', methods=['GET', 'POST'])
def addusuario():
    if request.method == 'POST':
        nome = request.form['nome'].strip()
        endereco = request.form['endereco'].strip()
        celular = request.form['celular'].strip()
        email = request.form['email'].strip()
        senha = request.form['senha'].strip()

        success = True
        if not nome:
            flash('O nome é requerido!', 'danger')
            success = False

        if not endereco:
            flash('O endereco é requerido!', 'danger')
            success = False

        if not email:
            flash('O email é requerido!', 'danger')
            success = False

        if not senha:
            flash('A senha é requerida!', 'danger')
            success = False

        if email:
            conn = get_db_connection()
            usuario = conn.execute(
                f"SELECT * FROM usuario WHERE email='{email}'").fetchone()
            conn.close()
            if usuario:
                flash('O email já existe!', 'danger')
                success = False

        if success:
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
        nome = request.form['nome'].strip()
        endereco = request.form['endereco'].strip()
        cnpj = request.form['cnpj'].strip()
        email = request.form['email'].strip()
        senha = request.form['senha'].strip()

        success = True
        if not nome:
            flash('O nome é requerido!', 'danger')
            success = False

        if not endereco:
            flash('O endereco é requerido!', 'danger')
            success = False

        if not cnpj:
            flash('O CNPJ é requerido!', 'danger')
            success = False

        if not email:
            flash('O email é requerido!', 'danger')
            success = False

        if not senha:
            flash('A senha é requerida!', 'danger')
            success = False

        if email:
            conn = get_db_connection()
            usuario = conn.execute(
                f"SELECT * FROM farmacia WHERE email='{email}'").fetchone()
            conn.close()
            if usuario:
                flash('O email já existe!', 'danger')
                success = False

        if success:
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
        email = request.form['email'].strip()
        senha = request.form['senha'].strip()
        conn = get_db_connection()
        usuario = conn.execute(
            f"SELECT * FROM usuario WHERE email='{email}' AND senha = '{senha}'").fetchone()
        redir = None
        if (usuario):
            session['email'] = email
            session.pop('email_farm', None)
            redir = 'produtos'
        else:
            farmacia = conn.execute(
                f"SELECT * FROM farmacia WHERE email='{email}' AND senha = '{senha}'").fetchone()
            if (farmacia):
                session['email_farm'] = email
                session.pop('email', None)
                redir = 'farmacia'
        conn.close()
        if redir:
            return redirect(url_for(redir))
        else:
            error = 'Senha inválida. Tente novamente.'

    return render_template('login.html', error=error)


@ app.route('/logout')
def logout():
    session.pop('email', None)
    session.pop('email_farm', None)
    session.pop('pedidos', None)
    return redirect(url_for('home'))


app.jinja_env.globals.update(is_logged_out=is_logged_out)
app.jinja_env.globals.update(is_logged_out_farm=is_logged_out_farm)
app.jinja_env.globals.update(number2real=number2real)
app.jinja_env.globals.update(carrinho_itens=carrinho_itens)

if __name__ == '__main__':
    app.run(debug=True)
