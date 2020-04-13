# -*- coding: latin-1 -*-
import pandas as pd

import plotly.figure_factory as ff

import tkinter.ttk as ttk
from tkinter import *
from abc import abstractmethod, ABC
import os
from pathlib import Path
from xlsxwriter.exceptions import FileCreateError


import tarea 
import incurridos 
import gestion
import config    


# def fixed_map(option):
#     # Fix for setting text colour for Tkinter 8.6.9
#     # From: https://core.tcl.tk/tk/info/509cafafae
#     #
#     # Returns the style map for 'option' with any styles starting with
#     # ('!disabled', '!selected', ...) filtered out.
#  
#     # style.map() returns an empty list for missing options, so this
#     # should be future-safe.
#     return [elm for elm in style.map('Treeview', query_opt=option) if
#       elm[:2] != ('!disabled', '!selected')]




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



class OutputExcelName:
    version=0
    path=str(Path.home())+ '/Downloads'
    name='planning'
    extension='xlsx'
    
    @classmethod
    def getName(cls):
        return '{}/{}{}.{}'.format(cls.path, cls.name, ("-"+str(cls.version)) if cls.version else "", cls.extension)

    @classmethod
    def getNextName(cls):
        cls.version+=1
        return cls.getName()
        

class Planning:
    '''Atributos
        - self.df
        - self.tareas [Tarea]
        - self.validaciones {razon.what, (razon, Tarea)}
    '''
        
    def __init__(self):
        self.map_excel={}
        self.tareas=[]
        self.validaciones={}

        c=config.Config()
        
        self.df=pd.read_excel(c.planner_filename, skiprows=4)

        gestion.Gestion.datasource=c.gestion_filename
        gestion.Gestion.create()

        incurridos.Incurridos.datasource=c.incurridos_filename
        incurridos.Incurridos.create()        


        self.cargarTareasPlanner()
        self.validarTareasPlanner()
        
        c=config.ConfigView(c)        
        
    def cargarTareasPlanner(self):
        '''Cargar tareas'''
        self.tareas=[tarea.Tarea.from_record(row)  for (index, row) in self.df.iterrows()
                     if re.match(r'S-[0-9]{4}-[0-9]{5}.*' , row['Nombre de la tarea']) and row['Progreso']!= 'Se ha completado']

    def validarTareasPlanner(self):
        from collections import defaultdict
        self.validaciones=defaultdict(list)        
        
        for tarea in self.tareas:
            for razon in tarea.validate():
                if razon:
                    self.validaciones[razon.what].append((razon, tarea))

    def addTodas(self):
        self.map_excel['Todas']=pd.DataFrame([subtarea for t in self.tareas if t.subtareas for subtarea in tarea.TareaView.show_as_lists(t)], 
                                         columns=tarea.TareaView.headers().split('#'))

    def addSinPlanificar(self):        
        self.map_excel['Sin planificar']=pd.DataFrame([subtarea for t in self.tareas if t.subtareas for subtarea in tarea.TareasSinPlanificarView.show_as_lists(t)], 
                                         columns=tarea.TareaView.headers().split('#'))
    
    def addPlanning(self):
        self.map_excel['Planning']=pd.DataFrame([subtarea for t in self.tareas if t.subtareas for subtarea in tarea.TareasPlanning.show_as_lists(t,14)], 
                                         columns=tarea.TareaView.headers().split('#'))

    def addValidaciones(self):
        headers=["Razon","Info Razón","Resp. funcional", "Codigo", "Descripcion", "Estado"]
        validaciones=[[razon.what, razon.why, t.responsables.get("RF","") if t.responsables else "", t.codigo, t.descripcion, t.estado]  
                  for validacion in self.validaciones.values()
                  for razon, t in validacion if t.estado in tarea.Tarea.estados() + ['PENDIENTE - IBD']]
                    
        self.map_excel['Validaciones']=pd.DataFrame(validaciones,columns=headers)
        
    def generarExcel(self):
        self.addTodas()
        self.addSinPlanificar()
        self.addPlanning()
        self.addValidaciones()
        
    
        outFileName=OutputExcelName.getName()
        while True:
            try:
                writer = pd.ExcelWriter(outFileName, engine='xlsxwriter')
        
                for name, tab in self.map_excel.items():
                    tab.to_excel(writer,sheet_name=name,index=False)     
                writer.save()
            except (PermissionError, FileCreateError):
                outFileName=OutputExcelName.getNextName()
                continue
            break
            
        return outFileName

    
    
        
    
        
        

if __name__ == "__main__":

    p=Planning()

    os.system(r'start excel.exe "' + p.generarExcel() +'"')
   
    
    
    print("Etiquetas:")
    print(tarea.Tarea.ck)
    print(tarea.Tarea.traduccion.keys())
    for x in tarea.Tarea.ck:
        if x not in tarea.Tarea.traduccion.values():
            print("* [" + x +"]")
            
            
            
            
            
    for t in p.tareas:
        df_gant_estado+=t.to_dict_by_estado()
        df_gant_responsable+=t.to_dict_by_responsable()
        df_gant_por_responsable+=t.to_dict_for_responsable()


# style = ttk.Style()
# style.map('Treeview', foreground=fixed_map('foreground'),
#           background=fixed_map('background'))
# main_window = Tk()
# app = Arbol(main_window)
# for t in tareas:
#     nodo=app.add_tarea(t)
#     for s in t.subtareas:
#         app.add_subtarea(nodo, s)
#         
#         
# app.mainloop()
# 
# 
# 
# 
# fig = ff.create_gantt(df_gant_estado, index_col='Resource', show_colorbar=True, group_tasks=True, showgrid_x=True)
# fig.show()
#    
# fig = ff.create_gantt(df_gant_responsable, index_col='Resource', show_colorbar=True, group_tasks=True, showgrid_x=True)
# fig.show()
#    
# df_ordered=sorted(df_gant_por_responsable, key= lambda k: k['Task'])
# df_ordered
# fig = ff.create_gantt(df_ordered, index_col='Resource', show_colorbar=True, group_tasks=False, showgrid_x=True)
# fig.show()





