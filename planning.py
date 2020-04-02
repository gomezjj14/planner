# -*- coding: latin-1 -*-
import pandas as pd
import tempfile

import plotly.figure_factory as ff

import tkinter.ttk as ttk
from tkinter import *
from tarea import *
from abc import abstractmethod, ABC
import datetime
import os
from pprint import pprint
import gestion

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








if __name__ == "__main__":
    
    from tkinter import Tk
    from tkinter.filedialog import askopenfilename

    Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
    planner_filename = askopenfilename(title = "Extracción de planner", filetypes = (("excel","*.xlsx"),("all files","*.*"))) # show an "Open" dialog box and return the path to the selected file
    print(planner_filename)
    df=pd.read_excel(planner_filename, skiprows=4)
 
    gestion_filename = askopenfilename(title = "Excel de Gestión", filetypes = (("excel","*.xlsx"),("all files","*.*"))) # show an "Open" dialog box and return the path to the selected file
    print(gestion_filename)   
    Gestion.datasource=gestion_filename
    Gestion.create()
    
    
    '''Cargar tareas'''
    tareas=[]
    for index, x in df.iterrows():
        if(re.match(r'S-[0-9]{4}-[0-9]{5}.*' , x['Nombre de la tarea'])):
            t=Tarea.from_record(x)
            tareas.append(t)

    print('** Validando tareas **')
    validaciones ={}
    for t in tareas:
        if t.estado in Tarea.dict_estados_tareas.keys():
            for razon in t.validate():
                validaciones[razon.split(':')[0]]= validaciones.get(razon.split(':')[0], []) + [t.codigo + "-" + t.descripcion + " - " + t.estado + " " + "-".join(razon.split(':')[1:])] 
                    
    for v in validaciones.keys():
        print(v)
        print("\t","\n\t".join(validaciones[v]), end='\n', sep='')

        

        
#     exit(0)



    
    out=r'C:\Users\j.gomez.de.la.cueva\OneDrive - Accenture\python\planner\test.xlsx'
    writer = pd.ExcelWriter(out, engine='xlsxwriter')
    map_excel={}
    
    ''' Mostrar tareas '''
            
    print('** Todas las tareas **')
    print(TareaView.headers()) 
    print(''.join([TareaView.show(t) for t in tareas if t.subtareas]))


    new_list= []
    for t in tareas:
        if t.subtareas:
            new_list += TareaView.show_as_lists(t)
    
    map_excel['Todas']=pd.DataFrame(new_list,columns=TareaView.headers().split('#'))

            
    print('** Tareas sin planificar **')
    print(TareaView.headers()) 
    print(''.join([TareasSinPlanificarView.show(t) for t in tareas if t.subtareas]))

    new_list= []
    for t in tareas:
        if t.subtareas:
            new_list += TareasSinPlanificarView.show_as_lists(t)    

    map_excel['Sin planificar']=pd.DataFrame(new_list,columns=TareaView.headers().split('#'))
   
    
    print('** Planning **') 
    print(TareaView.headers()) 
    print(''.join([TareasPlanning.show(t,15) for t in tareas if t.subtareas]))

    new_list= []
    for t in tareas:
        if t.subtareas:
            new_list += TareasPlanning.show_as_lists(t,2)    


    map_excel['Planning']=pd.DataFrame(new_list,columns=TareaView.headers().split('#'))


    new_list=[]
    headers=["Razon","Info Razón","Resp. funcional", "Codigo", "Descripcion", "Estado"]
    for t in tareas:
        if t.estado in Tarea.dict_estados_tareas.keys():
            for razon in t.validate():
                validacion=[[razon.split(':')[0], 
                             "-".join(razon.split(':')[1:]), 
                             t.responsables.get("RF","") if t.responsables else "", 
                             t.codigo, 
                             t.descripcion, 
                             t.estado]]
                print(validacion)
                new_list += validacion
                
    print(headers)
    print(new_list)
    map_excel['Validaciones']=pd.DataFrame(new_list,columns=headers)
   
    
    
    for name, tab in map_excel.items():
        tab.to_excel(writer,sheet_name=name,index=False)     
    
        
    writer.save()
    os.system(r'start excel.exe "' + out +'"')
    
    
#     traduccion = {'DTE + PPU + RPI':'DTE + PPU',
#         'DTE + PPU +RPI':'DTE + PPU',
#         'DTE + PPU  +RPI':'DTE + PPU',
#         'DTE + PPU':'DTE + PPU',
#         'DTE + PPU  Rework':'DTE + PPU',
#         'RPI + QA':'RPI',
#         'RPI':'RPI',
#         'RPI':'RPI Rework',
#         'RPI QA':'RPI',
#         'QA del RPI':'RPI',
#         'QA RPI':'RPI',
#         'QA':'RPI',
#         'QA + RPI':'RPI'}
    print("Etiquetas:")
    print(Tarea.ck)
    print(Tarea.traduccion.keys())
    for x in Tarea.ck:
        if x not in Tarea.traduccion.values():
            print("* [" + x +"]")
        else:
            print("  [" + x +"]")
#     for t in tareas:
#         if t.subtareas:
#             print(TareasPlanning.show(t,15), end='') 
            
            
            
            
            
            
#             if not t.fecha_vencimiento:
#                 sin_fecha.append(t)
#             elif t.subtareas:
#                 df_gant_estado+=t.to_dict_by_estado()
#                 df_gant_responsable+=t.to_dict_by_responsable()
#                 df_gant_por_responsable+=t.to_dict_for_responsable()
#                 tareas.append(t)

#     print("** Mostrar **")
#     print(" 1.- Tareas sin fecha de entrega")
#     
#     option=int(input("> "))
# 
#     df=pd.DataFrame([s for t in tareas for s in t.as_dict()])
#     
#     if option==1:
#         print('\n'.join(ValidadorFechaEntrega.batch(tareas)))
#         print(df)
# 
# 
# 
#     sys.exit()
# 
# 
#     print("** Todas **")
#     print('\n'.join([ str(a) for a in tareas]))
#         
#     print("** Subtareas sin planificar **")
#     print('\n'.join(ValidadorPlanificacion.batch(tareas)))
#         
#     print("** Tareas Vencidas **")
#     print('\n'.join(ValidadorFechaVencimiento.batch(tareas)))
    

    

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





