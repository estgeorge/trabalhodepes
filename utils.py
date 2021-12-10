import sqlite3
import re
import os
from flask import Flask, render_template, redirect, url_for, flash, request, session
from werkzeug.exceptions import abort


def get_db_connection():
    conn = sqlite3.connect(os.path.dirname(__file__)+'/database.db')
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


def real2number(n):
    return float(n.replace(',', '.'))


def build_pedidos(pedidos):
    i = 0
    pedidos_new = []
    for pedido in pedidos:
        if int(pedido['nitens']) > 0:
            pedidos_new.append({'pedido_id': i,
                                'produto': pedido['produto'],
                                'preco': float(pedido['preco']),
                                'id': int(pedido['id']),
                                'token': pedido['token'],
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


def add_pedido(pedidos, produto, token):
    pedidos.append({'produto': produto['produto'],
                    'preco': produto['preco'],
                    'id': produto['id'],
                    'token': token,
                    'nitens': 1})
    return build_pedidos(pedidos)


def check_prescricao(pedidos, pedido_id):
    for pedido in pedidos:
        if (int(pedido['pedido_id']) == int(pedido_id)):
            if (pedido['token']):
                return True
            else:
                return False


def update_pedido(pedidos, pedido_id, nitens):
    for pedido in pedidos:
        if (int(pedido['pedido_id']) == int(pedido_id)):
            pedido['nitens'] = nitens
            break
    return build_pedidos(pedidos)


def delete_pedido(pedidos, pedido_id):
    for pedido in pedidos:
        if (int(pedido['pedido_id']) == int(pedido_id)):
            pedido['nitens'] = 0
            break
    return build_pedidos(pedidos)


def validar_cnpj(cnpj):
    """
    Valida CNPJs, retornando apenas a string de números válida.

    # CNPJs errados
    >>> validar_cnpj('abcdefghijklmn')
    False
    >>> validar_cnpj('123')
    False
    >>> validar_cnpj('')
    False
    >>> validar_cnpj(None)
    False
    >>> validar_cnpj('12345678901234')
    False
    >>> validar_cnpj('11222333000100')
    False

    # CNPJs corretos
    >>> validar_cnpj('11222333000181')
    '11222333000181'
    >>> validar_cnpj('11.222.333/0001-81')
    '11222333000181'
    >>> validar_cnpj('  11 222 333 0001 81  ')
    '11222333000181'
    """
    cnpj = ''.join(re.findall('\d', str(cnpj)))

    if (not cnpj) or (len(cnpj) < 14):
        return False

    # Pega apenas os 12 primeiros dígitos do CNPJ e gera os 2 dígitos que faltam
    inteiros = map(int, cnpj)
    novo = inteiros[:12]

    prod = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    while len(novo) < 14:
        r = sum([x*y for (x, y) in zip(novo, prod)]) % 11
        if r > 1:
            f = 11 - r
        else:
            f = 0
        novo.append(f)
        prod.insert(0, 6)

    # Se o número gerado coincidir com o número original, é válido
    if novo == inteiros:
        return cnpj
    return False


if __name__ == "__main__":
    print("OK!")
