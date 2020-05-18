#!/usr/bin/python
# -*- coding: latin-1 -*-
'''
Created on 17 may. 2020

@author: j.gomez.de.la.cueva
'''

from tkinter import Tk
from tkinter.filedialog import askopenfilename
from incurridos.dao import IncurridosDAOExcel

if __name__ == '__main__':
    #Excel de Gestion
    Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing    
    gestion_filename = askopenfilename(title = "Excel de Incurridos", filetypes = (("excel","*.xlsm"),("all files","*.*"))) 
    print(gestion_filename)   
    i=IncurridosDAOExcel(gestion_filename)
    
#     print(i.getDF().columns.values)
    
    cols=['Versión','Fecha','Actividad.1','Objeto.1','Ppto. Incurrible','Lenguaje','Área Funcional / Work Plan','xReference','State','ATotal']
    

    
    
    short_df=i.getDF().loc[:, [*cols,'Detalle\nHoras Incurridas','Detalle\n% Asignación']]
    short_df=short_df.assign(detalle=short_df['Detalle\nHoras Incurridas'].str.split('\n'))\
                     .assign(porc=short_df['Detalle\n% Asignación'].str.split('\n'))\
                     .explode('detalle').explode('porc')
    short_df['persona']=short_df['detalle'].str.extract('([^0-9]+)', expand=False).str.strip()
    short_df['horas incurridas']=short_df['detalle'].str.extract('([0-9]+)', expand=False).str.strip()
    short_df['p_persona']=short_df['porc'].str.extract('([^0-9%]+)', expand=False).str.strip()
    short_df['% asignacion']=short_df['porc'].str.extract('([0-9%]+)', expand=False).str.strip()

    
    
    df=short_df[short_df.persona==short_df.p_persona].loc[:,[*cols,'persona','horas incurridas','% asignacion']]
    df.to_excel('detalle_incurridos.xlsx')
#     print(short_df.assign(horas=short_df['Detalle\nHoras Incurridas'].str.extract('([0-9]+)')).explode('horas'))

    
    
