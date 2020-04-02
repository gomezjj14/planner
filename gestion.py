import pandas as pd
from tabulate import tabulate
import abc
import datetime
from pprint import pprint

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class Gestion:
    datasource=''
#     datasource=r'C:\Users\j.gomez.de.la.cueva\Accenture\Peticiones - NUEVO CALCULADOR INTERNACIONAL\0 - GESTION\GESTION PETICIONES_v6.3.xlsx'
    sheet='Seguimiento-Iberbill'
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


    
    @classmethod
    def create(cls):
        cls.df=pd.read_excel(cls.datasource, cls.sheet, engine = 'xlrd', index_col=1, na_values=[datetime.time(0)])
        cls.df=cls.df.loc[~cls.df.index.duplicated(keep='first')]


    
    
    @classmethod
    def createTarea(cls,codigo):
        t = Tarea()
        try:
            t.setTarea(codigo,*cls.df.fillna(Gestion.defaultValues).replace(Gestion.defaultValuesNone).loc[codigo,['Título','Estado gadget',  
                                                    'Total incurrible',
                                                    'ARU','DDE', 'PPU','DTI','TUA',
                                                    'Fecha planificada valoración previa',
                                                    'Fecha planificada funcional',
                                                    'Fecha planificada entrega']].values.flatten().tolist())
            
        except TypeError:
            cls.df.fillna(Gestion.defaultValues).replace(Gestion.defaultValuesNone).loc[codigo,['Título','Estado gadget',  
                                                    'Total incurrible',
                                                    'ARU','DDE', 'PPU','DTI','TUA'
                                                    'Fecha planificada valoración previa',
                                                    'Fecha planificada funcional',
                                                    'Fecha planificada entrega']].values.flatten().tolist()
            raise
            
        return(t)

    @classmethod
    def createAllTarea(cls):
        for gadget in cls.df.index:
            try:
                yield(cls.createTarea(gadget))
            except TypeError:
                continue
    
class Tarea:    
    def __init__(self):
        self.codigo=''
        self.descripcion=''
        self.estado=''
        self.total=0.0
        self.ARU=0.0
        self.DDE=0.0
        self.PPU=0.0
        self.DTI=0.0
        self.TUA=0.0
        self.fecha_valoracion=''
        self.fecha_entrega=''
        self.fecha_funcional=''
    
    def setTarea(self,codigo, descripcion, estado, total, ARU, DDE, PPU, DTI, TUA, valo, funcional,entrega):
        self.codigo=codigo
        self.descripcion=descripcion
        self.estado=estado
        self.total=int(total)
        self.ARU=int(ARU)
        self.DDE=int(DDE)
        self.PPU=int(PPU)
        self.DTI=int(DTI)
        self.TUA=int(TUA)
        self.fecha_valoracion=valo
        self.fecha_funcional=funcional
        self.fecha_entrega=entrega
        
        

class TareaView:
    __metaclass__ = abc.ABCMeta
    def __init__(self,t):
        self.t=t

    @abc.abstractmethod
    def __str__(self):
        None
        
class TareaPrettyView(TareaView):
    def fechaToStr(self, fecha):
        return fecha.strftime('%Y-%m-%d') if type(fecha) == pd._libs.tslibs.timestamps.Timestamp else str(fecha)
    def __str__(self):
        return (str(self.t.codigo) + " - " + str(self.t.descripcion) + "\n" +
                "\tEstado    :" + self.t.estado + "\n"+
                "\tValoracion:" + str(self.t.total) + "[" + str(self.t.ARU) + "/" + str(self.t.DDE) + "/" + str(self.t.PPU)  + "/" + str(self.t.DTI) + "]" + "\n" +
                "\tFechas" + "\n" +
                "\t  Valoracion : " + self.fechaToStr(self.t.fecha_valoracion) + "\n" + 
                "\t  Funcional  : " + self.fechaToStr(self.t.fecha_funcional) + "\n" +
                "\t  Entrega    : " + self.fechaToStr(self.t.fecha_entrega) + "\n")              


if __name__ == "__main__":


#     with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
#         pprint(Gestion.df)
#         
                
    t=Gestion.createTarea('S-2020-01749')
    print(TareaPrettyView(t))


        
#         for t in Gestion.createAllTarea():
#             print(TareaPrettyView(t))
        


