a = {'1': {'name': 'lala', 'amount': '2'}, '2': {'name': "lolo", 'amount': '7'}}

b = []
for item in a:
    f = (a[item])
    b.append(f)
print(b[0]['name'])