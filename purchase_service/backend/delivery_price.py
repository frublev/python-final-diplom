
WEIGHT, WEIGHT_MAX = [{'w': 5, 'price': 300}, {'w': 10, 'price': 600}], 1000
PACKAGE, PACKAGE_MAX = [{'p': 30, 'price': 250}, {'p': 100, 'price': 500}], 1000
BUYER_SHOP_MIN, BUYER_SHOP_MAX = 300, 1000

ordered_items = [
    {'id': 3, 'order': 2, 'product_info':
        {'model': 'apple/iphone/xs-max', 'product': 1, 'shop': 1, 'external_id': 4216292, 'price': 112222,
         'weight': 1, 'package': 1,
         'product_parameters':
             [{'parameter': 'Диагональ (дюйм)', 'value': '6.5'},
              {'parameter': 'Разрешение (пикс)', 'value': '2688x1242'},
              {'parameter': 'Встроенная память (Гб)', 'value': '512'},
              {'parameter': 'Цвет', 'value': 'золотистый'}]},
     'quantity': 1},
    {'id': 4, 'order': 2, 'product_info':
        {'model': 'cover/iphone/xs-max', 'product': 5, 'shop': 2, 'external_id': 1000000, 'price': 1100,
         'weight': 1, 'package': 1,
         'product_parameters':
             [{'parameter': 'Цвет', 'value': 'золотистый'}]},
     'quantity': 1},
    {'id': 5, 'order': 2, 'product_info':
        {'model': 'ikea/box', 'product': 7, 'shop': 2, 'external_id': 3000000, 'price': 26500,
         'weight': 40, 'package': 1000,
         'product_parameters':
             [{'parameter': 'Цвет', 'value': 'Белый'}]},
     'quantity': 1}]


def calc_price(weight, package, buyer_shop=False):
    for w in WEIGHT:
        if weight < w['w']:
            price_w = w['price']
            break
        else:
            price_w = WEIGHT_MAX
    for p in PACKAGE:
        if package < p['p']:
            price_p = p['price']
            break
        else:
            price_p = PACKAGE_MAX
    # if buyer_shop:
    #     price_bs = BUYER_SHOP_MIN
    # else:
    #     price_bs = BUYER_SHOP_MAX
    return price_p + price_w # + price_bs


def delivery_price(order_items):
    shops = {}
    for item in order_items:
        shop_id = item['product_info']['shop']
        weight = item['product_info']['weight']
        package = item['product_info']['package']
        id_existed = shops.get(shop_id)
        if id_existed:
            weight = weight + id_existed[0]
            package = package + id_existed[1]
        shops.update({shop_id: [weight, package]})
    price = 0
    for shop in shops:
        w = shops[shop][0]
        p = shops[shop][1]
        price += calc_price(w, p)
    return price
