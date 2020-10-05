user_data = dict()

def func():
    user_data['he'] = {'name': 'Vasya'}
    temp = user_data['he']
    print(type(temp))
    temp['name'] = 'Petya'
    print(user_data)

user_data['me'] = 'Misha'
func()

