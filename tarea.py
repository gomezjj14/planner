'''
Created on 30 dic. 2019

@author: j.gomez.de.la.cueva
'''

from collections import OrderedDict
import math
import datetime
from enum import Enum
from gestion import Gestion, Tarea as TareaGestion
from types import *
# from gestion import Gestion

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
    

    


class Subtarea:
    def __init__(self, codigo, fecha_desde, fecha_hasta, responsable, incurrible):
        print("Creando subtarea...",codigo)
        self.codigo=codigo
        self.fecha_desde=self.str_to_date(fecha_desde)
        self.fecha_hasta=self.str_to_date(fecha_hasta)
        self.responsable=responsable
        self.incurrible=incurrible
        

    def str_to_date(self, f):
        print(f)
        return(datetime.datetime.strptime(f, '%d/%m/%Y') if (type(f)==str and f!= 'DD/MM/YYYY') or (type(f)==float and not math.isnan(f))  else None)
    def isValid(self):
        return len([x for x in self.validate()]) == 0
    
    def validate(self):
        if not self.fecha_desde:
            yield "Sin fecha desde"
        
        if not self.fecha_hasta:
            yield "Sin fecha hasta"
            
        if not self.responsable:
            yield "Sin asignar"
    
    def __str__(self):
        return "Subtarea:[" + '#'.join([self.codigo,self.fecha_desde.strftime('%Y-%m-%d') if self.fecha_desde else '', self.fecha_hasta.strftime('%Y-%m-%d') if self.fecha_hasta else '', self.responsable, self.incurrible])+"]"

class SubtareaView:
    @classmethod
    def show(self, s):
        return '#'.join([s.codigo,s.fecha_desde.strftime('%Y-%m-%d') if s.fecha_desde else '', s.fecha_hasta.strftime('%Y-%m-%d') if s.fecha_hasta else '', s.responsable, str(s.incurrible)])
    @classmethod
    def headers(cls):
        return '#'.join(['subtarea','inicio', 'fin', 'Responsable', 'Incurrible'])
    @classmethod
    def to_list(cls, s):
        return [s.codigo,s.fecha_desde.strftime('%Y-%m-%d') if s.fecha_desde else '', s.fecha_hasta.strftime('%Y-%m-%d') if s.fecha_hasta else '', s.responsable, str(s.incurrible)]


class Tarea:
    ck=set()
    traduccion = {
        #"VALORACION - DEF"
        'DEF':'DEF',
        #DESARROLLO- EFF
        'EFF': 'EFF',
        #DESARROLLO - DTE
        'DTE + PPU + RPI':'DESARROLLO',
        'DTE + PPU +RPI':'DESARROLLO',
        'DTE + PPU  +RPI':'DESARROLLO',
        'DTE + PPU':'DESARROLLO',
        'DTE + PPU  Rework':'DESARROLLO',
        #ACN - INTEGRACION
        'RPI + QA':'QA',
        'RPI':'QA',
        'RPI Rework':'QA',
        'RPI QA':'QA',
        'QA del RPI':'QA',
        'QA RPI':'QA',
        'QA':'QA',
        'QA + RPI':'QA'}
    dict_estados_tareas=OrderedDict({"VALORACION - DEF":[{"Tarea":"Elaborar Enfoque", "start":'Due date Valoración Previa', "end":'Due date Valoración Previa', "Responsable":'RF'},
                                                         {"Tarea":"Elaborar DEF+PF+DPI", "start":'Due date Valoración Previa', "end":'DEF', "Responsable":'RF', "Incurrible":['ARU']}], 
                                     "DESARROLLO- EFF":[{"Tarea":"Elaborar EFF", "start":'DEF', "end":'EFF', "Responsable":"RT", "Incurrible":['DDE']}],
                                     "DESARROLLO - DTE":[{"Tarea":"Construcción+Prueba Unitaria+RPI", "start":'EFF', "end":'DESARROLLO', "Responsable":"RD", "Incurrible":['PPU','DTI']}],
                                     "ACN - INTEGRACION":[{"Tarea":"Q&A", "start":'DESARROLLO', "end":'QA', "Responsable":"QA", "Incurrible":['TUA']},
                                                          {"Tarea":"Entregar a IBD", "start":'QA', "end":'Due date Entrega', "Responsable":"RF"}]
                                     })    
    
        
    def __init__(self,codigo,descripcion, fecha_creacion, checklist=None, estado="VALORACION - DEF", fecha_vencimiento=None, responsables=None):
        print('Creando tarea:', codigo)
        self.codigo=codigo
        self.descripcion=descripcion.strip('- ')
        self.estado=estado
        self.fecha_creacion=datetime.datetime.strptime(fecha_creacion, '%d/%m/%Y')
        self.fecha_vencimiento=datetime.datetime.strptime(fecha_vencimiento, '%d/%m/%Y') if type(fecha_vencimiento)==str or (type(fecha_vencimiento)==float and not math.isnan(fecha_vencimiento))  else None
        self.setTareaGestion()
        self.create_responsables(responsables)
        self.create_subtareas(checklist)
            
#         self.gestion=Gestion()
#         self.gestion.createTarea(codigo)      

    @classmethod
    def from_record(cls, r):
        return cls(r['Nombre de la tarea'][0:12], r['Nombre de la tarea'][13:], r['Fecha de creación'], r['Elementos de la lista de comprobación'], r['Nombre del depósito'], r['Fecha de vencimiento'], r['Descripción'])
    
    def setTareaGestion(self):
        try:
            self.tareaGestion=Gestion.createTarea(self.codigo)
        except KeyError:
            self.tareaGestion=None
    
    def isValid(self):
        return self.validate() is not None

    def fechaToStr(self, fecha):
        return str(fecha) if not fecha else fecha.strftime('%d/%m/%Y')
    
    def validate(self):
        if not self.fecha_vencimiento:
            yield "Sin fecha de vencimiento"
            
        if any([not x.isValid() for x in self.subtareas.values()]):
            yield "Tiene subtareas sin planificar"
        
        if not self.tareaGestion:
            yield "No tiene tarea en la excel de Gestión asociada"
        
        try:
            '''Fecha de entrega'''
            if self.tareaGestion and self.tareaGestion.fecha_entrega != self.subtareas["Entregar a IBD"].fecha_hasta:
                yield "Fecha de entrega no coincide [GESTION][PLANNER]: [" + self.fechaToStr(self.tareaGestion.fecha_entrega) + "][" + self.fechaToStr(self.subtareas["Entregar a IBD"].fecha_hasta) + "]"
        except KeyError:
            yield "No existe subtarea 'Entregar a IBD'"
        
        try:
            '''Fecha de valoración previa'''
            if self.tareaGestion and self.tareaGestion.fecha_valoracion != self.subtareas["Elaborar Enfoque"].fecha_hasta:
                yield "Fecha de valoración previa no coincide [GESTION][PLANNER]: [" + self.fechaToStr(self.tareaGestion.fecha_valoracion) + "][" + self.fechaToStr(self.subtareas["Elaborar Enfoque"].fecha_hasta) + "]"
        except KeyError:
            if self.estado=='VALORACION - DEF':
                yield "No existe subtarea 'Elaborar Enfoque'"
        
        try:
            '''Fecha de funcional'''
            if self.tareaGestion and self.tareaGestion.fecha_funcional != self.subtareas["Elaborar DEF+PF+DPI"].fecha_hasta:
                yield "Fecha de DEF no coincide [GESTION][PLANNER]: [" + self.fechaToStr(self.tareaGestion.fecha_funcional) + "][" + self.fechaToStr(self.subtareas["Elaborar DEF+PF+DPI"].fecha_hasta) + "]"
        except KeyError:
            if self.estado=='VALORACION - DEF':
                yield "No existe subtarea 'DEF'"

        if not self.responsables or "RF" not in self.responsables.keys() or not self.responsables["RF"]:
            yield "No tiene asignado responsable funcional"
            
        if self.estado!='VALORACION - DEF':
            try:
                if not self.subtareas["Entregar a IBD"].fecha_hasta:
                    yield "Sin fecha de entrega planificada"
            except KeyError:
                    yield "Sin fecha de entrega planificada"    
        
    def create_subtareas(self, checklist):
        print(checklist,[ [ Tarea.traduccion.get(a.lstrip().rstrip(),a.lstrip().rstrip()) for a in  item.split('-')[:2]] for item in checklist.split(';') if '-' in item], sep='\n')
        checklist_to_dict=dict( [ [ Tarea.traduccion.get(a.lstrip().rstrip(),a.lstrip().rstrip()) for a in  item.split('-')[:2]] for item in checklist.split(';') if '-' in item])
        self.subtareas={}
        Tarea.ck=Tarea.ck.union(checklist_to_dict.keys())
        
        if self.estado in list(Tarea.dict_estados_tareas.keys()):
            for estado in list(Tarea.dict_estados_tareas.keys())[list(Tarea.dict_estados_tareas.keys()).index(self.estado):] :
                for subt in Tarea.dict_estados_tareas[estado]:
                    print("\tsubt",subt["Tarea"], "["+subt["start"]+".."+ subt["end"] + "]", list(checklist_to_dict.keys()) , sep=' - ')

                    incurrible=0
                    try:
                        for i in subt["Incurrible"]:
                            if self.tareaGestion:
                                incurrible+=self.tareaGestion.__getattribute__(i)
                    except KeyError:
                        incurrible=0
                    
                    if(subt["start"] in list(checklist_to_dict.keys()) and subt["end"] in list(checklist_to_dict.keys())):
                        s=Subtarea(subt["Tarea"],checklist_to_dict[subt["start"]], checklist_to_dict[subt["end"]], self.responsables[subt["Responsable"]], incurrible)
                        self.subtareas[subt["Tarea"]]=s            


    def create_responsables(self, r):
        self.responsables={}
        validos=["RF","RD","RT","QA"]
        self.responsables=dict( [ [a.lstrip() for a in  resp.split(':')] for resp in r.split('\n') if resp[0:2] in validos]) if type(r)==str else None
        
    @classmethod
    def estados(self):
        return list(Tarea.dict_estados_tareas.keys())

    def __str__(self):
        return '>>' + str(self.codigo) + ' ' + self. descripcion + ' - ' + str(self.fecha_vencimiento) + \
               ' - ' + (self.responsables.get("RF","Nadie asignado") if self.responsables else "Nadie asignado") + \
               ''.join([ '\n\t'+ str(subtarea) for subtarea in self.subtareas.values()]) ;

                       
    def as_dict(self):
        return [{"codigo":self.codigo, 'descripcion':self.descripcion, "subtarea":s.codigo, "inicio":s.fecha_desde, "fin":s.fecha_hasta} for s in self.subtareas.values()]

    def to_dict_by_responsable(self):
        return [dict(Task=self.codigo, Start=sub.fecha_desde.strftime('%Y-%m-%d'), Finish=sub.fecha_hasta.strftime('%Y-%m-%d'), Resource=sub.responsable ) \
            for sub in self.subtareas.values() if sub.isComplete()]
        
    def to_dict_by_estado(self):
        return [dict(Task=self.codigo, Start=sub.fecha_desde.strftime('%Y-%m-%d'), Finish=sub.fecha_hasta.strftime('%Y-%m-%d'), Resource=sub.codigo ) \
            for sub in self.subtareas.values() if sub.isComplete()]
    def to_dict_for_responsable(self):
        return [dict(Task=sub.responsable, Start=sub.fecha_desde.strftime('%Y-%m-%d'), Finish=sub.fecha_hasta.strftime('%Y-%m-%d'), Resource=sub.codigo ) \
            for sub in self.subtareas.values() if sub.isComplete()]
        
    
        

class TareaView:
    @classmethod
    def headers(cls):
        return '#'.join(['codigo','descripcion', 'estado', 'fec. vencimiento', 'Resp. funcional', SubtareaView.headers()])

    @classmethod
    def to_str(cls,t,subtarea):
        return '#'.join([ str(t.codigo), t.descripcion, t.estado, str(t.fecha_vencimiento), \
                  (t.responsables.get("RF","Nadie asignado") if t.responsables else "Nadie asignado"), \
                  SubtareaView.show(subtarea)])+'\n'
    @classmethod
    def to_list(cls,t, subtarea):
        return [ str(t.codigo), t.descripcion, t.estado, str(t.fecha_vencimiento), \
                (t.responsables.get("RF","Nadie asignado") if t.responsables else "Nadie asignado")] + SubtareaView.to_list(subtarea)

    @classmethod
    def show_as_lists(cls,t):
        return [ cls.to_list(t,subtarea) for subtarea in t.subtareas.values() ]
    
    @classmethod
    def show(cls,t):
        return ''.join([cls.to_str(t, subtarea) for subtarea in t.subtareas.values()])

        
        
class TareasSinPlanificarView(TareaView):        
    @classmethod
    def show_as_lists(cls,t):
        return [cls.to_list(t, subtarea) for subtarea in t.subtareas.values() if subtarea.fecha_hasta is None]

    @classmethod
    def show(cls,t):
        return ''.join([cls.to_str(t, subtarea) for subtarea in t.subtareas.values() if subtarea.fecha_hasta is None])

    
class TareasPlanning(TareaView):
    @classmethod
    def show_as_lists(cls,t,dias):
        return [cls.to_list(t, subtarea) for subtarea in t.subtareas.values() 
                        if subtarea.fecha_hasta is not None 
                        and subtarea.fecha_hasta <= datetime.datetime.today()+datetime.timedelta(days=dias)]

    @classmethod
    def show(cls,t,dias):
        return ''.join([cls.to_str(t, subtarea) for subtarea in t.subtareas.values() 
                        if subtarea.fecha_hasta is not None 
                        and subtarea.fecha_hasta <= datetime.datetime.today()+datetime.timedelta(days=dias)])
    
