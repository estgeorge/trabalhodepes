import sqlite3
from flask import Flask, render_template, redirect, url_for, flash, request, session
from werkzeug.exceptions import abort


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


def getFarmacia():
    conn = get_db_connection()
    farmacia = conn.execute(
        "SELECT * FROM farmacia WHERE email='"+session['email_farm']+"'").fetchone()
    conn.close()
    return farmacia


def getUsuario():
    conn = get_db_connection()
    usuario = conn.execute(
        "SELECT * FROM usuario WHERE email='"+session['email']+"'").fetchone()
    conn.close()
    return usuario


def carrinho_itens():
    if 'pedidos' in session:
        pedidos = session['pedidos']
        return len(pedidos)
    else:
        return 0


def is_logged_out():
    return 'email' not in session


def is_logged_out_farm():
    return 'email_farm' not in session


def dumpclean(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if hasattr(v, '__iter__'):
                print(k)
                dumpclean(v)
            else:
                print('%s : %s' % (k, v))
    elif isinstance(obj, list):
        for v in obj:
            if hasattr(v, '__iter__'):
                dumpclean(v)
            else:
                print(v)
    else:
        print(obj)


def number2real(n):
    return f'{n:.2f}'.replace('.', ',')


def build_pedidos(pedidos):
    i = 0
    pedidos_new = []
    for pedido in pedidos:
        if int(pedido['nitens']) > 0:
            pedidos_new.append({'pedido_id': i,
                                'produto': pedido['produto'],
                                'preco': float(pedido['preco']),
                                'id': int(pedido['id']),
                                'nitens': int(pedido['nitens']),
                                'total': int(pedido['nitens']) * float(pedido['preco'])
                                })
            i = i+1
    return pedidos_new


def get_total_pedidos(pedidos):
    s = 0
    for pedido in pedidos:
        s = s+pedido['nitens']*pedido['preco']
    return s


def add_pedido(pedidos, produto):
    pedidos.append({'produto': produto['produto'],
                    'preco': produto['preco'],
                    'id': produto['id'],
                    'nitens': 1})
    return build_pedidos(pedidos)


def update_pedido(pedidos, pedido_id, nitens):
    for pedido in pedidos:
        if (int(pedido['pedido_id']) == int(pedido_id)):
            pedido['nitens'] = nitens
            break
    return build_pedidos(pedidos)
