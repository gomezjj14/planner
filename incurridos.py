import pandas as pd
import datetime
import sys
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from pathlib import Path


class TareaIncurridos:
	def __init__(self, codigo, incurridos):
		self.codigo=codigo
		self.incurridos=incurridos
		self.balance=sum(incurridos.values())
	
	def show(self):
		print(self.codigo +' - ' + str(self.balance))
		print("\t", "\n\t".join([k+' -> ' + str(int(v))   for k, v in self.incurridos.items()]))


class Incurridos:
	datasource=''
	sheet='Desglose Petición Según GESTEP'


	@classmethod
	def create(cls):
		cls.df=pd.read_excel(cls.datasource, cls.sheet, skiprows=4, engine = 'xlrd', index_col=0, na_values=[datetime.time(0)])
		cls.pivot=cls.df.pivot_table(index=['Código','Actividad'],  values=['Ppto. Incurrible','TOTAL'], aggfunc=sum)
# 		with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
# 		    print(cls.df)

	@classmethod
	def createTarea(cls,codigo):
		print('Tarea [%s]' % codigo)
		incurrido_disponible={c:int(v['Ppto. Incurrible'] - v['TOTAL']) for (c,v) in cls.pivot.xs(codigo, level=0).iterrows()}
		return(TareaIncurridos(codigo,incurrido_disponible))
		pass
		
		
if __name__=='__main__':
	
	#Excel de Gestion
	Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing	
	gestion_filename = askopenfilename(title = "Excel de Incurridos", filetypes = (("excel","*.xlsm"),("all files","*.*")), initialdir=r'C:\Users\j.gomez.de.la.cueva\OneDrive - Accenture\Iberdrola\incurridos') 
	print(gestion_filename)   
	Incurridos.datasource=gestion_filename
	Incurridos.create()
	
    	
	for arg in sys.argv[1:]:
		try:
			Incurridos.createTarea(arg).show()
		except KeyError:
			pass
		