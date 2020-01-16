import pandas as pd
import pprint



class Tarea:
    __init__(self, registro):
        self.r=





df=pd.read_excel(r'FI - Area 1 (2).xlsx', skiprows=4)

pp = pprint.PrettyPrinter()

df[0]




with pd.option_context('display.max_rows', None, 'display.max_columns', None):
    checklist=df[df['Nombre de la tarea'].str.contains('6002')][r'Elementos de la lista de comprobación'].tolist()[0].split(sep=';')
    print(checklist)

