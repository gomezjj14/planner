'''
Created on 30 dic. 2019

@author: j.gomez.de.la.cueva
'''


import math
import datetime
import re

from types import *


import pandas as pd

from incurridos.dao import IncurridosDAOExcel
from gestion.dao import GestionDAOExcel
from util.util import date_to_str, str_to_date
from tarea.model import Tarea, HeadersFactory

''' 
Subtarea: 
    [Elaborar Enfoque] ARU
    [Elaborar DEF+PF+DPI] ARU
    
    [Elaborar EFF] DDE
    
    [Construcción+Prueba Unitaria] PPU + DTI
    
    [Q&A] TUA
    [Entregar a IBD]
    
    codigo
    fecha_desde
    fecha_hasta
    responsable
'''

'''
Tarea
    codigo
    descripcion
    estado
    fecha_creacion
    fecha_vencimiento
    responsables {tarea, responsable}
    subtareas {codigo, subtarea}
    tareaGestion
  Validaciones
'''

class TareaDAOExcel:
    
    def __init__(self, excel,area):
        self.excel=excel
        self.df=pd.read_excel(excel, skiprows=4)
        self.tareas=None
        self.validaciones=None
        self.area=area
    
        
    def getAllTareas(self):
        if not self.tareas:
            h = HeadersFactory.create(self.df.columns)
            self.tareas=[Tarea.from_record(row,self.area)  for (index, row) in self.df.iterrows()
                         if re.match(r'S-[0-9]{4}-[0-9]{5}.*' , row[h.NOMBRE]) and row[h.PROGRESO]!= h.COMPLETADA]
        
        return self.tareas
    
    def getAllValidaciones(self):
        from collections import defaultdict
        self.validaciones=defaultdict(list)        
        
        for tarea in self.tareas:
            for razon in tarea.validate():
                if razon:
                    self.validaciones[razon.what].append((razon, tarea))
        return self.validaciones


        
    
        


    


if __name__=='__main__':
    from tarea.model import CodigoSubtarea
    
    index_list=[CodigoSubtarea.DTE,CodigoSubtarea.DEF]
    
    index_list.sort()
    print(index_list)
