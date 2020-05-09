'''
Created on 25 abr. 2020

@author: j.gomez.de.la.cueva
'''

from mongoengine import *
from pprint import pprint

from tarea.model import TareaMongoDb, Tarea, CodigoSubtarea

class TareaDAOMongoDB:
    db_name='planning'
    
    def __init__(self):
        connect(db=TareaDAOMongoDB.db_name)

    def insert(self, peticion):
        t=TareaMongoDb(**peticion.to_dict_mongodb())
        t.save()
        return t.id

    def insertAll(self, peticiones):
        ids = [ self.insert(p) for p in peticiones]
        return ids
    
    def getOne(self,Codigo):
        return TareaMongoDb.objects(codigo=Codigo)[0]
        
    def getAll(self):
        for t in TareaMongoDb.objects():
            yield t
            

if __name__ == '__main__':
    db=TareaDAOMongoDB()
    
    pprint(db.getOne('S-2020-02623').to_mongo())
