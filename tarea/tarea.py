'''
Created on 30 dic. 2019

@author: j.gomez.de.la.cueva
'''

from collections import OrderedDict
import math
import datetime
from enum import Enum
from types import *
import logging
import traceback

from incurridos.incurridos import Incurridos
from gestion.gestion import Gestion


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
    
class Validacion:
    def __init__(self, what, why=''):
        self.what=what
        self.why=why
        
class CodigoSubtarea(Enum):
    ENFOQUE = "Elaborar Enfoque"
    DEF = "Elaborar DEF+PF+DPI"
    EFF = "Elaborar EFF"
    DTE = "Construcción+Prueba Unitaria+RPI"
    QA = "Q&A"
    ENTREGA = "Entregar a IBD"
    
    __ordering__ = ['ENFOQUE', 'DEF','EFF','DTE','QA','ENTREGA']
    def __lt__(self, other):
        return self.__ordering__.index(self.name) < self.__ordering__.index(other.name)
    
class HeadersFactory():
    @classmethod    
    def create(cls,l):
        if   HeadersSP.NOMBRE in l:
            return HeadersSP
        elif HeadersEN.NOMBRE in l:
            return HeadersEN
        else:
            return None
  
    
        
        
        
class HeadersSP():
    NOMBRE = 'Nombre de la tarea'
    F_CREACION = 'Fecha de creación'
    CHECKLIST = 'Elementos de la lista de comprobación'
    DEPOSITO = 'Nombre del depósito'
    F_VENCIMIENTO = 'Fecha de vencimiento'
    DESCRIPCION = 'Descripción'
    PROGRESO = 'Progreso'
    COMPLETADA = 'Se ha completado'
    
class HeadersEN():
    NOMBRE = 'Task Name'
    F_CREACION = 'Created Date'
    CHECKLIST = 'Checklist Items'
    DEPOSITO = 'Bucket Name'
    F_VENCIMIENTO = 'Due Date'
    DESCRIPCION = 'Description'
    PROGRESO = 'Progress'
    COMPLETADA = 'Completed'


def str_to_date(f):
    return(datetime.datetime.strptime(f, '%d/%m/%Y') if (type(f)==str and f!= 'DD/MM/YYYY') or (type(f)==float and not math.isnan(f))  else None)

def date_to_str(fecha):
    return str(fecha) if not fecha else fecha.strftime('%d/%m/%Y')

class Subtarea:
    def __init__(self, codigo, fecha_desde, fecha_hasta, responsable, incurrible):
        print("  Creando subtarea...",codigo.value)
        self.codigo=codigo
        self.fecha_desde=str_to_date(fecha_desde)
        self.fecha_hasta=str_to_date(fecha_hasta)
        self.responsable=responsable
        self.incurrible=incurrible

    def isValid(self):
        return self.fecha_desde and self.fecha_hasta and self.responsable
   
    def __str__(self):
        return "Subtarea:[" + '#'.join([self.codigo,date_to_str(self.fecha_desde), date_to_str(self.fecha_hasta), self.responsable, self.incurrible])+"]"

class SubtareaView:
    @classmethod
    def show(self, s):
        return '#'.join([s.codigo.value,date_to_str(s.fecha_desde), date_to_str(s.fecha_hasta), s.responsable, str(s.incurrible)])
    @classmethod
    def headers(cls):
        return '#'.join(['subtarea','inicio', 'fin', 'Responsable', 'Incurrible'])
    @classmethod
    def to_list(cls, s):
        return [s.codigo.value,date_to_str(s.fecha_desde), date_to_str(s.fecha_hasta), s.responsable, str(s.incurrible)]


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
    dict_estados_tareas=OrderedDict({"VALORACION - DEF":[{"Tarea": CodigoSubtarea.ENFOQUE, "start":'Due date Valoración Previa', "end":'Due date Valoración Previa', "Responsable":'RF', "Incurrible":[]},
                                                         {"Tarea": CodigoSubtarea.DEF, "start":'Due date Valoración Previa', "end":'DEF', "Responsable":'RF', "Incurrible":['ARU']}], 
                                     "DESARROLLO- EFF":[{"Tarea": CodigoSubtarea.EFF, "start":'DEF', "end":'EFF', "Responsable":"RT", "Incurrible":['DDE']}],
                                     "DESARROLLO - DTE":[{"Tarea": CodigoSubtarea.DTE, "start":'EFF', "end":'DESARROLLO', "Responsable":"RD", "Incurrible":['PPU','DTI']}],
                                     "ACN - INTEGRACION":[{"Tarea": CodigoSubtarea.QA, "start":'DESARROLLO', "end":'QA', "Responsable":"QA", "Incurrible":['TUA']},
                                                          {"Tarea": CodigoSubtarea.ENTREGA, "start":'QA', "end":'Due date Entrega', "Responsable":"RF", "Incurrible":[]}]
                                     })    
    
        
    def __init__(self,codigo,descripcion, fecha_creacion, checklist=None, estado="VALORACION - DEF", fecha_vencimiento=None, responsables=None):
        print('Creando tarea:', codigo, ' - ', estado)
        self.codigo=codigo
        self.descripcion=descripcion.strip('- ')
        self.estado=estado
        self.fecha_creacion=str_to_date(fecha_creacion)
        self.fecha_vencimiento=str_to_date(fecha_vencimiento)
        self.setTareaGestion()
        self.setTareaIncurridos()
        self.create_responsables(responsables)
        self.create_subtareas(checklist)

    @classmethod
    def from_record(cls, r):
        h = HeadersFactory.create(r.keys())
#         return cls(r[h.NOMBRE][0:12], r[h.NOMBRE][13:], r[h.F_CREACION], r[h.CHECKLIST], r[h.DEPOSITO], r[h.F_VENCIMIENTO], r[h.DESCRIPCION])
        return cls(r[h.NOMBRE][0:12], r[h.NOMBRE][13:], r[h.F_CREACION], r[h.CHECKLIST], r[h.DEPOSITO], r[h.F_VENCIMIENTO], r[h.DESCRIPCION])

    def create_subtareas(self, checklist):
        checklist_to_dict=dict( [ [ Tarea.traduccion.get(a.lstrip().rstrip(),a.lstrip().rstrip()) for a in  item.split('-')[:2]] for item in checklist.split(';') if '-' in item])
        self.subtareas={}
        Tarea.ck=Tarea.ck.union(checklist_to_dict.keys())
        
        try:
            for estado in Tarea.estados()[Tarea.estados().index(self.estado):] :
                for subt in Tarea.dict_estados_tareas[estado]:
                    incurrible=sum([ self.tareaGestion.__getattribute__(i)  for i in subt["Incurrible"] if self.tareaGestion ])
                    if subt["start"] in checklist_to_dict and subt["end"] in checklist_to_dict:
                        self.subtareas[subt["Tarea"]]=Subtarea(subt["Tarea"],checklist_to_dict[subt["start"]], checklist_to_dict[subt["end"]], self.responsables[subt["Responsable"]], incurrible)
        except ValueError:
            pass

    def create_responsables(self, r):
        validos=["RF","RD","RT","QA"]
        self.responsables=dict( [ [a.lstrip() for a in  resp.split(':')] for resp in r.split('\n') if resp[0:2] in validos]) if type(r)==str else {}

    
    def setTareaGestion(self):
        try:
            self.tareaGestion=Gestion.createTarea(self.codigo)
        except KeyError:
            self.tareaGestion=None
    
    def setTareaIncurridos(self):
        try:
            self.tareaIncurridos=Incurridos.createTarea(self.codigo)
        except KeyError:
            self.tareaIncurridos=None
    
    def isValid(self):
        return self.validate() is not None


    
    def validate(self):
        try: 
            ''' Si la peticion esta pendiente de IBD no realiza mas validaciones '''
            if self.estado=='PENDIENTE - IBD':
                yield Validacion("Tarea pendiente de Iberdrola",self.tareaGestion.estado)
            else:
                ''' Gestion vs Planner '''
                if not self.tareaGestion:
                    yield Validacion("No tiene tarea en la excel de Gestión asociada")
                
                try:
                    '''Fecha de valoración previa'''
                    if self.tareaGestion and self.tareaGestion.fecha_valoracion != self.subtareas[CodigoSubtarea.ENFOQUE].fecha_hasta:
                        yield Validacion("Fecha de valoración previa no coincide [GESTION][PLANNER]", 
                                         "[" + date_to_str(self.tareaGestion.fecha_valoracion) + "][" + date_to_str(self.subtareas[CodigoSubtarea.ENFOQUE].fecha_hasta) + "]")
                except KeyError:
                    if self.estado=='VALORACION - DEF':
                        yield Validacion("No existe subtarea 'Elaborar Enfoque'")
        
                try:
                    '''Fecha de funcional'''
                    if self.tareaGestion and self.tareaGestion.fecha_funcional != self.subtareas[CodigoSubtarea.DEF].fecha_hasta and self.tareaGestion.fecha_funcional:
                        yield Validacion("Fecha de DEF no coincide [GESTION][PLANNER]", 
                                         "[" + date_to_str(self.tareaGestion.fecha_funcional) + "][" + date_to_str(self.subtareas[CodigoSubtarea.DEF].fecha_hasta) + "]")
                except KeyError:
                    if self.estado=='VALORACION - DEF':
                        yield Validacion("No existe subtarea 'DEF'")
        
                try:
                    '''Fecha de entrega'''
                    if self.tareaGestion and self.tareaGestion.fecha_entrega != self.subtareas[CodigoSubtarea.ENTREGA].fecha_hasta and self.tareaGestion.fecha_entrega:
                        yield Validacion("Fecha de entrega no coincide [GESTION][PLANNER]", 
                                         "[" + date_to_str(self.tareaGestion.fecha_entrega) + "][" + date_to_str(self.subtareas[CodigoSubtarea.ENTREGA].fecha_hasta) + "]")
                except KeyError:
                    yield Validacion("No existe subtarea 'Entregar a IBD'")
                
                '''Validaciones generales en planner'''
                if not self.fecha_vencimiento:
                    yield Validacion("Sin fecha de vencimiento")
                if not self.responsables or "RF" not in self.responsables.keys() or not self.responsables["RF"]:
                    yield Validacion("No tiene asignado responsable funcional")
                
                '''Validaciones por estado en planner'''
                if self.estado=='VALORACION - DEF':
                    try:
                        if self.fecha_vencimiento and (self.fecha_vencimiento > self.subtareas[CodigoSubtarea.ENFOQUE].fecha_hasta and 
                                                       self.fecha_vencimiento > self.subtareas[CodigoSubtarea.DEF].fecha_hasta):
                            yield Validacion("Fecha de vencimiento de la tarea es mayor que la fecha planificada [Vencimiento][Enfoque-DEF]",
                                             "["+date_to_str(self.fecha_vencimiento)+ "][" + date_to_str(self.subtareas[CodigoSubtarea.ENFOQUE].fecha_hasta) + "-" + date_to_str(self.subtareas[CodigoSubtarea.DEF].fecha_hasta)+ "]")
                    except TypeError:
                        '''Las fechas no permiten hacer la validacion'''
                        yield Validacion("No tiene planificadas fechas de Enfoque y/o DEF ",
                                         "-".join([date_to_str(self.subtareas[CodigoSubtarea.ENFOQUE].fecha_hasta), date_to_str(self.subtareas[CodigoSubtarea.DEF].fecha_hasta) ]))
                                                   
        
                if self.estado=='DESARROLLO- EFF':
                    try:
                        if self.fecha_vencimiento and self.fecha_vencimiento > self.subtareas[CodigoSubtarea.EFF].fecha_hasta:
                            yield Validacion("Fecha de vencimiento de la tarea es mayor que la fecha planificada [Vencimiento][EFF]",
                                             "["+date_to_str(self.fecha_vencimiento)+ "][" + date_to_str(self.subtareas[CodigoSubtarea.EFF].fecha_hasta) + "]")
                    except TypeError:
                        yield Validacion("No tiene planificada fecha de EFF")
                    
                    if not self.responsables['RT']:
                        yield Validacion("La tarea no tiene asignado responsable técnico [RT]")
                                                   
                if self.estado=='DESARROLLO - DTE':
                    try:
                        if self.fecha_vencimiento and self.fecha_vencimiento > self.subtareas[CodigoSubtarea.DTE].fecha_hasta:
                            yield Validacion("Fecha de vencimiento de la tarea es mayor que la fecha planificada [Vencimiento][DTE]",
                                             "["+date_to_str(self.fecha_vencimiento)+ "][" + date_to_str(self.subtareas[CodigoSubtarea.DTE].fecha_hasta) + "]")
                    except TypeError:
                        yield Validacion("No tiene planificada fecha de DTE + PPU + RPI")    
                    
                    if not self.responsables['RD']:
                        yield Validacion("La tarea no tiene asignado responsable de desarrollo [RD]")
                    
                if self.estado=='ACN - INTEGRACION':
                    try:
                        if self.fecha_vencimiento and (self.fecha_vencimiento > self.subtareas[CodigoSubtarea.QA].fecha_hasta and 
                                                       self.fecha_vencimiento > self.subtareas[CodigoSubtarea.ENTREGA].fecha_hasta):
                            yield Validacion("Fecha de vencimiento de la tarea es mayor que la fecha planificada [Vencimiento][Q&A-Entrega IBD]",
                                             "["+date_to_str(self.fecha_vencimiento)+ "][" + date_to_str(self.subtareas[CodigoSubtarea.QA].fecha_hasta) + "/" + date_to_str(self.subtareas[CodigoSubtarea.ENTREGA].fecha_hasta)+ "]")
                    except TypeError:
                        yield Validacion("No tiene planificada fecha de Q&A")                 
                                                                      
                    if not self.responsables['QA']:
                        yield Validacion("La tarea no tiene asignado responsable de Q&A [QA]")
                    
                    
                if self.estado!='VALORACION - DEF':
                    if CodigoSubtarea.ENTREGA not in self.subtareas or not self.subtareas[CodigoSubtarea.ENTREGA].fecha_hasta:
                        yield Validacion("Sin fecha de entrega planificada [GESTION]", date_to_str(self.tareaGestion.fecha_entrega) if self.tareaGestion else "")
        
        except:
            logging.error('Error validando petición [{}]'.format(self.codigo))
            logging.error(traceback.format_exc())
            
        
    @classmethod
    def estados(cls):
        return list(cls.dict_estados_tareas.keys())

    def __str__(self):
        return '>>' + str(self.codigo) + ' ' + self. descripcion + ' - ' + date_to_str(self.fecha_vencimiento) + \
               ' - ' + (self.responsables.get("RF","Nadie asignado") if self.responsables else "Nadie asignado") + \
               ''.join([ '\n\t'+ str(subtarea) for subtarea in self.subtareas.values()]) ;

                       
    def as_dict(self):
        return [{"codigo":self.codigo, 'descripcion':self.descripcion, "subtarea":s.codigo, "inicio":s.fecha_desde, "fin":s.fecha_hasta} for s in self.subtareas.values()]

    def to_dict_by_responsable(self):
        return [dict(Task=self.codigo, Start=sub.fecha_desde.strftime('%Y-%m-%d'), Finish=sub.fecha_hasta.strftime('%Y-%m-%d'), Resource=sub.responsable ) \
            for sub in self.subtareas.values() if sub.isValid()]
        
    def to_dict_by_estado(self):
        return [dict(Task=self.codigo, Start=sub.fecha_desde.strftime('%Y-%m-%d'), Finish=sub.fecha_hasta.strftime('%Y-%m-%d'), Resource=sub.codigo ) \
            for sub in self.subtareas.values() if sub.isValid()]
    def to_dict_for_responsable(self):
        return [dict(Task=sub.responsable, Start=sub.fecha_desde.strftime('%Y-%m-%d'), Finish=sub.fecha_hasta.strftime('%Y-%m-%d'), Resource=sub.codigo ) \
            for sub in self.subtareas.values() if sub.isValid()]
        
    
        

class TareaView:
    @classmethod
    def headers(cls):
        return '#'.join(['codigo','descripcion', 'estado', 'fec. vencimiento', 'Resp. funcional', 'Total Incurridos disponibles', SubtareaView.headers()])

    @classmethod
    def to_str(cls,t,subtarea):
        return '#'.join([ str(t.codigo), t.descripcion, t.estado, date_to_str(t.fecha_vencimiento), \
                  (t.responsables.get("RF","Nadie asignado") if t.responsables else "Nadie asignado"), \
                  t.tareaIncurridos.balance, \
                  SubtareaView.show(subtarea)])+'\n'
    @classmethod
    def to_list(cls,t, subtarea):
        return [ str(t.codigo), t.descripcion, t.estado, date_to_str(t.fecha_vencimiento), \
                (t.responsables.get("RF","Nadie asignado") if t.responsables else "Nadie asignado"), t.tareaIncurridos.balance if t.tareaIncurridos else 'NA'] + SubtareaView.to_list(subtarea)

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
    


if __name__=='__main__':
    
    index_list=[CodigoSubtarea.DTE,CodigoSubtarea.DEF]
    
    index_list.sort()
    print(index_list)
