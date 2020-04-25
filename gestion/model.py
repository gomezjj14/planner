'''
Created on 25 abr. 2020

@author: j.gomez.de.la.cueva
'''

class TareaGestion:    
    def __init__(self,codigo, descripcion, estado, total, ARU, DDE, PPU, DTI, TUA, valo, funcional,entrega):
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
