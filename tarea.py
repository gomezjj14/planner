'''
Created on 30 dic. 2019

@author: j.gomez.de.la.cueva
'''

import re
from collections import OrderedDict
import math
import datetime
from _ast import Global


global ck
ck=set()


class Subtarea:
    def __init__(self, codigo, fecha_desde, fecha_hasta, responsable):
        print("Creando subtarea...",codigo)
        self.codigo=codigo
        self.fecha_desde=self.str_to_date(fecha_desde)
        self.fecha_hasta=self.str_to_date(fecha_hasta)
        self.responsable=responsable

    def str_to_date(self, f):
        print(f)
        return(datetime.datetime.strptime(f, '%d/%m/%Y') if (type(f)==str and f!= 'DD/MM/YYYY') or (type(f)==float and not math.isnan(f))  else None)
    def isComplete(self):
        return (self.fecha_desde and self.fecha_hasta)
    
    def __str__(self):
        return "Subtarea:[" + '#'.join([self.codigo,self.fecha_desde.strftime('%Y-%m-%d') if self.fecha_desde else '', self.fecha_hasta.strftime('%Y-%m-%d') if self.fecha_hasta else '', self.responsable])+"]"


class Tarea:
    traduccion = {'DTE + PPU + RPI':'DTE + PPU',
        'DTE + PPU +RPI':'DTE + PPU',
        'DTE + PPU  +RPI':'DTE + PPU',
        'DTE + PPU':'DTE + PPU',
        'DTE + PPU  Rework':'DTE + PPU',
        'RPI + QA':'RPI',
        'RPI':'RPI',
        'RPI':'RPI Rework',
        'RPI QA':'RPI',
        'QA del RPI':'RPI',
        'QA RPI':'RPI',
        'QA':'RPI',
        'QA + RPI':'RPI'}
    dict_estados_tareas=OrderedDict({"VALORACION - DEF":[{"Tarea":"Elaborar DEF+PF+DPI", "start":'DEF', "end":'DEF', "Responsable":'RF'}], 
                                     "DESARROLLO- EFF":[{"Tarea":"Elaborar EFF", "start":'DEF', "end":'EFF', "Responsable":"RT"}],
                                     "DESARROLLO - DTE":[{"Tarea":"Construcción+Prueba Unitaria", "start":'EFF', "end":'DTE + PPU', "Responsable":"RD"}],
                                     "ACN - INTEGRACION":[{"Tarea":"Q&A", "start":'DTE + PPU', "end":'RPI', "Responsable":"QA"},
                                                          {"Tarea":"Entregar a IBD", "start":'RPI', "end":'Due date Entrega', "Responsable":"RF"}]
                                     })    
        
    def __init__(self,codigo,descripcion, fecha_creacion, checklist=None, estado="VALORACION - DEF", fecha_vencimiento=None, responsables=None):
        print('Creando tarea:', codigo)
        self.codigo=codigo
        self.descripcion=descripcion
        self.estado=estado
        self.fecha_creacion=datetime.datetime.strptime(fecha_creacion, '%d/%m/%Y')
        #print(f"[{type(fecha_vencimiento)}]")
        self.fecha_vencimiento=datetime.datetime.strptime(fecha_vencimiento, '%d/%m/%Y') if type(fecha_vencimiento)==str or (type(fecha_vencimiento)==float and not math.isnan(fecha_vencimiento))  else None
        self.create_responsables(responsables)
        self.create_subtareas(checklist)
        

    @classmethod
    def from_record(cls, r):
        return cls(r['Nombre de la tarea'][0:12], r['Nombre de la tarea'][13:], r['Fecha de creación'], r['Elementos de la lista de comprobación'], r['Nombre del depósito'], r['Fecha de vencimiento'], r['Descripción'])
    
    def create_subtareas(self, checklist):
        
        global ck    
            
        print(checklist)
        checklist_to_dict=dict( [ [ Tarea.traduccion.get(a.lstrip().rstrip(),a.lstrip().rstrip()) for a in  item.split('-')] for item in checklist.split(';') if '-' in item])
        self.subtareas=[]
        ck=ck.union(checklist_to_dict.keys())
        print("-->", "\n".join(ck))
        
        if self.estado in list(Tarea.dict_estados_tareas.keys()):
            for estado in list(Tarea.dict_estados_tareas.keys())[list(Tarea.dict_estados_tareas.keys()).index(self.estado):] :
                for subt in Tarea.dict_estados_tareas[estado]:
                    print("subt",subt["Tarea"], subt["start"], subt["end"], list(checklist_to_dict.keys()) , sep='/')
                    if(subt["start"] in list(checklist_to_dict.keys()) and subt["end"] in list(checklist_to_dict.keys())):
                        #print("subt",subt["start"], subt["end"], sep='/')
                        s=Subtarea(subt["Tarea"],checklist_to_dict[subt["start"]], checklist_to_dict[subt["end"]], self.responsables[subt["Responsable"]])
                        self.subtareas.append(s);            


    def create_responsables(self, r):
        validos=["RF","RD","RT","QA"]
        self.responsables=dict( [ [a.lstrip() for a in  resp.split(':')] for resp in r.split('\n') if resp[0:2] in validos]) if type(r)==str else None
        
    @classmethod
    def estados(self):
        return list(Tarea.dict_estados_tareas.keys())

    def __str__(self):
        return '>>' + str(self.codigo) + ' ' + self. descripcion + ' - ' + str(self.fecha_vencimiento) + \
               ' - ' + (self.responsables.get("RF","Nadie asignado") if self.responsables else "Nadie asignado") + \
               ''.join([ '\n\t'+ str(subtarea) for subtarea in self.subtareas]) ;
    def as_dict(self):
        return [{"codigo":self.codigo, 'descripcion':self.descripcion, "subtarea":s.codigo, "inicio":s.fecha_desde, "fin":s.fecha_hasta} for s in self.subtareas]

    def to_dict_by_responsable(self):
        return [dict(Task=self.codigo, Start=sub.fecha_desde.strftime('%Y-%m-%d'), Finish=sub.fecha_hasta.strftime('%Y-%m-%d'), Resource=sub.responsable ) \
            for sub in self.subtareas if sub.isComplete()]
        
    def to_dict_by_estado(self):
        return [dict(Task=self.codigo, Start=sub.fecha_desde.strftime('%Y-%m-%d'), Finish=sub.fecha_hasta.strftime('%Y-%m-%d'), Resource=sub.codigo ) \
            for sub in self.subtareas if sub.isComplete()]
    def to_dict_for_responsable(self):
        return [dict(Task=sub.responsable, Start=sub.fecha_desde.strftime('%Y-%m-%d'), Finish=sub.fecha_hasta.strftime('%Y-%m-%d'), Resource=sub.codigo ) \
            for sub in self.subtareas if sub.isComplete()]
        
