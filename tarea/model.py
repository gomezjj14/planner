'''
Created on 25 abr. 2020

@author: j.gomez.de.la.cueva
'''

from collections import OrderedDict
from enum import Enum
import logging
import traceback


from util.util import date_to_str, str_to_date
from gestion.dao import GestionDAOExcel
from incurridos.dao import IncurridosDAOExcel
from pickle import NONE

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
    



class CodigoSubtarea(Enum):
    ENFOQUE = "Elaborar Enfoque"
    DEF = "Elaborar DEF+PF+DPI"
    EFF = "Elaborar EFF"
    DTE = "Construcción+Prueba Unitaria+RPI"
    QA = "Q&A"
    ENTREGA = "Entrega a IBD + Creacion Tags"
    
    __ordering__ = ['ENFOQUE', 'DEF','EFF','DTE','QA','ENTREGA']
    def __lt__(self, other):
        return self.__ordering__.index(self.name) < self.__ordering__.index(other.name)
    

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

class Validacion:
    def __init__(self, what, why=''):
        self.what=what
        self.why=why    

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
                                                          {"Tarea": CodigoSubtarea.ENTREGA, "start":'QA', "end":'Due date Entrega + Creacion Tags', "Responsable":"RF", "Incurrible":[]}]
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
            self.tareaGestion=GestionDAOExcel().getOne(self.codigo)
        except KeyError:
            self.tareaGestion=None
    
    def setTareaIncurridos(self):
        try:
            self.tareaIncurridos=IncurridosDAOExcel().getOne(self.codigo)
        except KeyError:
            self.tareaIncurridos=None
    
    def isValid(self):
        return self.validate() is not None


    
    def validate(self):
        try: 
            ''' Si la peticion esta pendiente de IBD no realiza mas validaciones '''
            if self.estado=='PENDIENTE - IBD':
             ####
                try:
                    yield Validacion("Tarea pendiente de Iberdrola",self.tareaGestion.estado)
                except AttributeError:
                    yield Validacion("Tarea pendiente iberdrola vacia o inexistente")
            ####
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
                ###
                except ValueError:
                    yield Validacion(" El campo fecha esta vacio")
                ###
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
                    except KeyError:
                        yield Validacion("Error validando peticion")
                    
                    
                    if not self.responsables['RT']:
                        yield Validacion("La tarea no tiene asignado responsable técnico [RT]")
                                                   
                if self.estado=='DESARROLLO - DTE':
                    try:
                        if self.fecha_vencimiento and self.fecha_vencimiento > self.subtareas[CodigoSubtarea.DTE].fecha_hasta:
                            yield Validacion("Fecha de vencimiento de la tarea es mayor que la fecha planificada [Vencimiento][DTE]",
                                             "["+date_to_str(self.fecha_vencimiento)+ "][" + date_to_str(self.subtareas[CodigoSubtarea.DTE].fecha_hasta) + "]")
                    ###
                    except KeyError:
                        yield Validacion(" No existe tarea para el codigo subtarea " + str(CodigoSubtarea))
                    ###
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
                    except KeyError:
                        yield Validacion("No tiene planificada fecha de Q&A")                 
                                                                      
                    if not self.responsables['QA']:
                        yield Validacion("La tarea no tiene asignado responsable de Q&A [QA]")
                    
                if self.estado!='VALORACION - DEF':
                    if CodigoSubtarea.ENTREGA not in self.subtareas or not self.subtareas[CodigoSubtarea.ENTREGA].fecha_hasta:
                    ##### 
                        try:
                            yield Validacion("Sin fecha de entrega planificada [GESTION]", date_to_str(self.tareaGestion.fecha_entrega) if self.tareaGestion else "")
                        except ValueError:
                            yield Validacion(" Campo fecha entrega planificada esta vacio")
                    #####
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

if __name__ == '__main__':
    pass