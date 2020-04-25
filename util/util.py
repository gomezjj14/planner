'''
Created on 25 abr. 2020

@author: j.gomez.de.la.cueva
'''
import datetime
import math

def str_to_date(f):
    return(datetime.datetime.strptime(f, '%d/%m/%Y') if (type(f)==str and f!= 'DD/MM/YYYY') or (type(f)==float and not math.isnan(f))  else None)

def date_to_str(fecha):
    return str(fecha) if not fecha else fecha.strftime('%d/%m/%Y')

if __name__ == '__main__':
    pass