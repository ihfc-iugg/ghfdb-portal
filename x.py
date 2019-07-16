from copy import deepcopy

class A():
    def __init__(self):
        self.Meta = deepcopy(A.Meta)

    class Meta:
        x = 8



if __name__ == '__main__':

    a = A()
    b = deepcopy(a)

    b.Meta.x = 4

    print(a.Meta.x)
    print(b.Meta.x)


