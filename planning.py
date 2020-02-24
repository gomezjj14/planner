# -*- coding: latin-1 -*-
import pandas as pd

import plotly.figure_factory as ff

import tkinter.ttk as ttk
from tkinter import *
from tarea import *
from abc import abstractmethod, ABC
import datetime


def fixed_map(option):
    # Fix for setting text colour for Tkinter 8.6.9
    # From: https://core.tcl.tk/tk/info/509cafafae
    #
    # Returns the style map for 'option' with any styles starting with
    # ('!disabled', '!selected', ...) filtered out.

    # style.map() returns an empty list for missing options, so this
    # should be future-safe.
    return [elm for elm in style.map('Treeview', query_opt=option) if
      elm[:2] != ('!disabled', '!selected')]




        


class Validador(ABC):
    def __init__(self, t):
        self.tarea=t
        self.invalidos=[]
        self.validos=[]
        
    @abstractmethod
    def isValido(self):
        pass
    
class ValidadorPlanificacion(Validador):
    '''Valida que todas las tareas esten planificadas'''
    @staticmethod
    def batch(tareas):
        invalidos=[(t.codigo,ValidadorPlanificacion(t).invalidos) for t in tareas ]
        return [tarea + '->' + sub for tarea,subs in invalidos for sub in subs]

    def __init__(self,t):
        Validador.__init__(self,t)
        self.invalidos=[str(s) for s in self.tarea.subtareas if not s.isComplete()]
        
    def isValido(self):
        return self.invalidos==[]

class ValidadorPlanning(Validador):
    r'''Valida los estados que vencen en los proximos n dias para preparar la planning de un sprint'''
    @staticmethod
    def calcula_fechas(dias=14, offset=0):
        return (datetime.datetime.today()+datetime.timedelta(days=offset), datetime.datetime.today()+ datetime.timedelta(days=offset + dias))
    
    @staticmethod
    def batch(tareas, desde, hasta):
        validos=[(t.codigo,ValidadorPlanning(t, desde, hasta).validos) for t in tareas ]
        return [tarea + '->' + sub for tarea,subs in validos for sub in subs]
        
    def __init__(self, t, desde, hasta):
        Validador.__init__(self,t)
        self.desde=desde
        self.hasta=hasta
        self.validos=[str(s) for s in self.tarea.subtareas if s.isComplete() and s.fecha_hasta >= self.desde and s.fecha_hasta <= self.hasta]
    
    def isValido(self):
        return self.validos!=[]    
    
class ValidadorFechaVencimiento(Validador):
    r'''Valida que la fecha de vencimiento no se haya cumplido'''
    @staticmethod
    def batch(tareas):
        validadores=[ValidadorFechaVencimiento(tarea) for tarea in tareas]
        return [ str(val.tarea) for val in validadores if not val.isValido()]
    
    def __init__(self,t):
        Validador.__init__(self,t)

    def isValido(self):
        return self.tarea.fecha_vencimiento >= datetime.datetime.today()
    
class ValidadorFechaEntrega(Validador):
    r'''Valida que la fecha de entrega esté asignada'''
    @staticmethod
    def batch(tareas):
        validadores=[ValidadorFechaEntrega(tarea) for tarea in tareas]
        return [ str(val.tarea) for val in validadores if not val.isValido()]
    
    def __init__(self,t):
        Validador.__init__(self,t)

    def isValido(self):
        return any(x for x in self.tarea.subtareas if x.codigo=='Entregar a IBD')



class Arbol(ttk.Frame):
    def __init__(self,main_window):
        super().__init__(main_window)
        main_window.title("Vista de ï¿½rbol en Tkinter")
        
        self.grid(column=0, row=0, sticky="ns")
        self.treeview = ttk.Treeview(self, columns=("inicio","fin", "responsable"))

        self.treeview.pack(expand=True, fill=BOTH)
        self.pack()
        
        
        self.treeview.tag_configure("red", background='yellow', foreground="red")
        

    def add_tarea(self, tarea):
        return self.treeview.insert("", END, text=f'{tarea.codigo} {tarea.descripcion}', values=(tarea.fecha_creacion, tarea.fecha_vencimiento, tarea.estado), tags=("red",))

    def add_subtarea(self, tarea, subtarea):
        self.treeview.insert(tarea, END, text=f'{subtarea.codigo}', values=(subtarea.fecha_desde, subtarea.fecha_hasta, subtarea.responsable), tags=("red",))

    
df_gant_estado=[]
df_gant_responsable=[]
df_gant_por_responsable=[]
if __name__ == "__main__":
    df=pd.read_excel(r'FI - Area 1.xlsx', skiprows=4)

    sin_fecha=[]
    tareas=[]
    for index, x in df.iterrows():
        if(re.match(r'S-[0-9]{4}.*' , x['Nombre de la tarea'])):
            t=Tarea.from_record(x)
            if not t.fecha_vencimiento:
                sin_fecha.append(t)
            elif t.subtareas:
                df_gant_estado+=t.to_dict_by_estado()
                df_gant_responsable+=t.to_dict_by_responsable()
                df_gant_por_responsable+=t.to_dict_for_responsable()
                tareas.append(t)

    print("** Mostrar **")
    print(" 1.- Tareas sin fecha de entrega")
    
    option=int(input("> "))

    df=pd.DataFrame([s for t in tareas for s in t.as_dict()])
    
    if option==1:
        print('\n'.join(ValidadorFechaEntrega.batch(tareas)))
        print(df)



    sys.exit()


    print("** Todas **")
    print('\n'.join([ str(a) for a in tareas]))
        
    print("** Subtareas sin planificar **")
    print('\n'.join(ValidadorPlanificacion.batch(tareas)))
        
    print("** Tareas Vencidas **")
    print('\n'.join(ValidadorFechaVencimiento.batch(tareas)))
    

    print("** Tareas planning **")
    desde, hasta=ValidadorPlanning.calcula_fechas(14, 0)
    print('\n'.join(ValidadorPlanning.batch(tareas,desde, hasta)))
    

# result = ask_multiple_choice_question(
#     "ï¿½Quï¿½ quieres hacer?",
#     [
#         "Subtareas sin planificar",
#         "Tareas vencidas",
#         "Planning para las prï¿½ximas semanas"
#     ]
# )
# 
# print("User's response was: {}".format(repr(result)))

style = ttk.Style()
style.map('Treeview', foreground=fixed_map('foreground'),
          background=fixed_map('background'))
main_window = Tk()
app = Arbol(main_window)
for t in tareas:
    nodo=app.add_tarea(t)
    for s in t.subtareas:
        app.add_subtarea(nodo, s)
        
        
app.mainloop()




fig = ff.create_gantt(df_gant_estado, index_col='Resource', show_colorbar=True, group_tasks=True, showgrid_x=True)
fig.show()
  
fig = ff.create_gantt(df_gant_responsable, index_col='Resource', show_colorbar=True, group_tasks=True, showgrid_x=True)
fig.show()
  
df_ordered=sorted(df_gant_por_responsable, key= lambda k: k['Task'])
df_ordered
fig = ff.create_gantt(df_ordered, index_col='Resource', show_colorbar=True, group_tasks=False, showgrid_x=True)
fig.show()


