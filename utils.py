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
