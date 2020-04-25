'''
Created on 25 abr. 2020

@author: j.gomez.de.la.cueva
'''

class TareaIncurridos:
    def __init__(self, codigo, incurridos):
        self.codigo=codigo
        self.incurridos=incurridos
        self.balance=sum(incurridos.values())
    
    def show(self):
        print(self.codigo +' - ' + str(self.balance))
        print("\t", "\n\t".join([k+' -> ' + str(int(v))   for k, v in self.incurridos.items()]))


if __name__ == '__main__':
    pass