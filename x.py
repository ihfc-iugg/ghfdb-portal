from copy import deepcopy

class A():
    def __init__(self):
        self.Meta = deepcopy(A.Meta)

    class Meta:
        x = 8



if __name__ == '__main__':

    x = 'asdasd.asdasd'
    print(x.split('.'))


