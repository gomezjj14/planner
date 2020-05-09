# -*- coding: latin-1 -*-
import pandas as pd

# import plotly.figure_factory as ff
# import tkinter.ttk as ttk
# from abc import abstractmethod, ABC

# from tkinter import *
import os
from pathlib import Path
from xlsxwriter.exceptions import FileCreateError


from incurridos.dao import IncurridosDAOExcel 
from gestion.dao import GestionDAOExcel
from config import config    
from tarea.dao import TareaDAOExcel
from tarea.daoMongoDB import TareaDAOMongoDB
from tarea.view import TareaView, TareasSinPlanificarView, TareasPlanning
from tarea.model import Tarea

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
        config.ConfigView(c)
        
        self.planner= TareaDAOExcel(c.filenames[config.Filenames.PLANNER])
        self.gestion = GestionDAOExcel(c.filenames[config.Filenames.GESTION])
        self.incurridos = IncurridosDAOExcel(c.filenames[config.Filenames.INCURRIDOS])

        self.cargarPlanner()

        self.generarExcel()
        
#        self.insertMongoDB()
                
        
    def cargarPlanner(self):
        self.tareas = self.planner.getAllTareas()
        self.validaciones=self.planner.getAllValidaciones()      

    def addTodas(self):
        self.map_excel['Todas']=pd.DataFrame([subtarea for t in self.tareas if t.subtareas for subtarea in TareaView.show_as_lists(t)], 
                                         columns=TareaView.headers().split('#'))

    def addSinPlanificar(self):        
        self.map_excel['Sin planificar']=pd.DataFrame([subtarea for t in self.tareas if t.subtareas for subtarea in TareasSinPlanificarView.show_as_lists(t)], 
                                         columns=TareaView.headers().split('#'))
    
    def addPlanning(self):
        self.map_excel['Planning']=pd.DataFrame([subtarea for t in self.tareas if t.subtareas for subtarea in TareasPlanning.show_as_lists(t,14)], 
                                         columns=TareaView.headers().split('#'))

    def addValidaciones(self):
        headers=["Razon","Info Raz�n","Resp. funcional", "Codigo", "Descripcion", "Estado"]
        validaciones=[[razon.what, razon.why, t.responsables.get("RF","") if t.responsables else "", t.codigo, t.descripcion, t.estado]  
                  for validacion in self.validaciones.values()
                  for razon, t in validacion if t.estado in Tarea.estados() + ['PENDIENTE - IBD']]
                    
        self.map_excel['Validaciones']=pd.DataFrame(validaciones,columns=headers)
    
    def addIncurridos(self):
        headers=["Codigo", "Descripcion", "Total", "Subtarea","Incurridos Disponibles"]
        incurridos=[[t.codigo,t.descripcion,t.tareaIncurridos.balance, k, v]  for t in self.tareas if t.tareaIncurridos for (k,v) in t.tareaIncurridos.incurridos.items()]
        
        self.map_excel['incurridos']=pd.DataFrame(incurridos,columns=headers)

        
    def generarExcel(self):
        self.addTodas()
        self.addSinPlanificar()
        self.addPlanning()
        self.addValidaciones()
        self.addIncurridos()
        
    
        self.outFileName=OutputExcelName.getName()
        while True:
            try:
                writer = pd.ExcelWriter(self.outFileName, engine='xlsxwriter')
        
                for name, tab in self.map_excel.items():
                    tab.to_excel(writer,sheet_name=name,index=False)     
                writer.save()
            except (PermissionError, FileCreateError):
                self.outFileName=OutputExcelName.getNextName()
                continue
            break
            
        return self.outFileName

    def insertMongoDB(self):
        db=TareaDAOMongoDB()
        print(db.insertAll(self.tareas))
        
    
        
    
        
        

if __name__ == "__main__":

    p=Planning()

    os.system(r'start excel.exe "' + p.outFileName+'"')
   
    
    
    print("Etiquetas:")
    print(Tarea.ck)
    print(Tarea.traduccion.keys())
    for x in Tarea.ck:
        if x not in Tarea.traduccion.values():
            print("* [" + x +"]")
            
            
            
            
            
#     for t in p.tareas:
#         df_gant_estado+=t.to_dict_by_estado()
#         df_gant_responsable+=t.to_dict_by_responsable()
#         df_gant_por_responsable+=t.to_dict_for_responsable()


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





