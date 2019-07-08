

# row = [4,'',3,6,2,None,4,6]


row = {'x':8,'y':3,'z':''}

t = dict(filter(lambda item: item[1], row.items()))

print(t)
