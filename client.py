import requests

URL = 'http://127.0.0.1:8000'

TOKEN = 'Token ###'


def to_request(token=TOKEN, **kwargs):
    view = kwargs['view']
    if kwargs['method'] == 'post':
        response = requests.post(f'{URL}/{view}/', headers={'Authorization': token}, json={**kwargs})
    elif kwargs['method'] == 'get':
        response = requests.get(f'{URL}/{view}/', headers={'Authorization': token}, json={**kwargs})
    elif kwargs['method'] == 'put':
        response = requests.put(f'{URL}/{view}/', headers={'Authorization': token}, json={**kwargs})
    elif kwargs['method'] == 'patch':
        response = requests.patch(f'{URL}/{view}/', headers={'Authorization': token}, json={**kwargs})
    elif kwargs['method'] == 'delete':
        response = requests.delete(f'{URL}/{view}/', headers={'Authorization': token}, json={**kwargs})
    else:
        print('Method not used')
        return None
    print(response.status_code)
    print(response.json())


def log_in(email, password):
    response = requests.post(f'{URL}/login/',
                             json={'email': email, 'password': password},
                             )
    print(response.status_code)
    print(response.json())


create_user = {
            'method': 'post',
            'view': 'create_user',
            'first_name': 'Mail',
            'last_name': 'Ru',
            'email': '###',
            'password': '###',
            'company': 'Shop-2',
            'position': 'Manager',
            'type': 'shop'
       }

contacts = {
            'method': 'post',
            'view': 'contacts',
            'id': '32',
            'city': 'City_32',
            'street': 'Street_32',
            'house': '32',
            'structure': '32',
            # 'building': 'Shop-1',
            # 'apartment': 'Manager',
            'phone': '+7(495)123-45-32',
            'url': 'http://127.0.0.1:8000/'
       }

delete_contacts = {
            'method': 'delete',
            'view': 'contacts',
            'items': '10,11'
       }

update_price = {
        'method': 'post',
        'view': 'update_price',
        'url': 'http://127.0.0.1:8000/media/shop2.yaml'
    }

basket = {
        'method': 'post',
        'view': 'basket',
        'items': [{'product_info': 6, 'quantity': 1}, {'product_info': 7, 'quantity': 1}],
    }

account = {
        'method': 'get',
        'view': 'account',
    }

catalog = {
        'method': 'get',
        'view': 'catalog?shop_id=5&?category_id=224',
    }

user_orders = {
        'method': 'patch',
        'view': 'user_orders',
        'state': 'new',
        'contact': 7,
    }

shops_state = {
        'method': 'post',
        'view': 'shops_state',
        'state': 'True',
    }

shop_orders = {
        'method': 'get',
        'view': 'shop_orders',
        'state': 'True',
    }

to_request(TOKEN, **shop_orders)