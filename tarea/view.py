'''
Created on 25 abr. 2020

@author: j.gomez.de.la.cueva
'''
from util.util import date_to_str

import datetime

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


if __name__ == '__main__':
    pass

