'''
Created on 25 abr. 2020

@author: j.gomez.de.la.cueva
'''
import pandas as pd
import datetime
from gestion.model import TareaGestion


class GestionDAOExcel:
    excel=''
    sheet='Seguimiento-Iberbill-nuevo'
    defaultValues={'Título':'N/A',
                   'Estado gadget':'N/A',  
                    'Total incurrible':0.0,
                    'ARU':0.0,
                    'DDE':0.0, 
                    'PPU':0.0,
                    'DTI':0.0,
                    'TUA':0.0}
    defaultValuesNone={
                    'Fecha planificada valoración previa':{pd.NaT:None},
                    'Fecha planificada funcional':{pd.NaT:None},
                    'Fecha planificada entrega':{pd.NaT:None}}
    tareas={}
    
    def __init__(self, excel=""):
        print(excel)
        if excel and GestionDAOExcel.excel != excel:
            GestionDAOExcel.excel=excel
            GestionDAOExcel.df=pd.read_excel(excel, GestionDAOExcel.sheet, engine = 'xlrd', index_col=1, na_values=[datetime.time(0)])
            GestionDAOExcel.df=GestionDAOExcel.df.loc[~GestionDAOExcel.df.index.duplicated(keep='first')]
            self.getAll()
    
    def getOne(self, codigo):
        try:
            if codigo in GestionDAOExcel.tareas:
                return GestionDAOExcel.tareas[codigo]
            else:
                return TareaGestion(codigo, *GestionDAOExcel.df.fillna(GestionDAOExcel.defaultValues).replace(GestionDAOExcel.defaultValuesNone).loc[codigo, ['Título', 'Estado gadget',
                                                    'Total incurrible',
                                                    'ARU', 'DDE', 'PPU', 'DTI', 'TUA',
                                                    'Fecha planificada valoración previa',
                                                    'Fecha planificada funcional',
                                                    'Fecha planificada entrega']].values.flatten().tolist())
            
        except TypeError:
            GestionDAOExcel.df.fillna(GestionDAOExcel.defaultValues).replace(GestionDAOExcel.defaultValuesNone).loc[codigo, ['Título', 'Estado gadget',
                                                    'Total incurrible',
                                                    'ARU', 'DDE', 'PPU', 'DTI', 'TUA'
                                                    'Fecha planificada valoración previa',
                                                    'Fecha planificada funcional',
                                                    'Fecha planificada entrega']].values.flatten().tolist()
            raise

    def getAll(self):
        if not GestionDAOExcel.tareas:
            GestionDAOExcel.tareas={ gadget:self.getOne(gadget) for gadget in GestionDAOExcel.df.index } 
        return GestionDAOExcel.tareas.values()


if __name__ == '__main__':
    from tkinter.filedialog import askopenfilename
    from tkinter import Tk
    import sys
    from pathlib import Path
    from gestion.view import TareaPrettyView
    
    Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing    
    gestion_filename = askopenfilename(title = "Excel de Gestión", filetypes = (("excel","*.xlsx"),("all files","*.*")), initialdir=str(Path.home())+ '/Accenture/Peticiones - NUEVO CALCULADOR INTERNACIONAL/0 - GESTION') # show an "Open" dialog box and return the path to the selected file
    g=GestionDAOExcel(gestion_filename)

    for arg in sys.argv[1:]:
        t=g.getOne(arg)
        print(TareaPrettyView(t))
        
        