'''
Created on 25 abr. 2020

@author: j.gomez.de.la.cueva
'''
import pandas as pd
import abc

class TareaGestionView:
    __metaclass__ = abc.ABCMeta
    def __init__(self,t):
        self.t=t

    @abc.abstractmethod
    def __str__(self):
        None
        
class TareaPrettyView(TareaGestionView):
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

if __name__ == '__main__':
    pass