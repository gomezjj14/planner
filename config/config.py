'''
Created on 12 abr. 2020

@author: j.gomez.de.la.cueva
'''
from pathlib import Path
import os

import tkinter as tk
from tkinter import Tk
from tkinter.filedialog import askopenfilename


import yaml
from enum import Enum

class Filenames(Enum):
    PLANNER = 'planner'
    GESTION = 'gestion'
    INCURRIDOS = 'incurridos'

    @staticmethod
    def list():
        return list(map(lambda f: f.value, Filenames))    

class Config:
    config_file='config.yml'
    config_filenames={Filenames.PLANNER:{'title':'Extracción de planner', 'filetypes':(("excel","*.xlsx"),("all files","*.*")), 'initialdir':str(Path.home())+ '/Downloads' },
                      Filenames.GESTION:{'title':'Excel de Gestion', 'filetypes':(("excel","*.xlsx"),("all files","*.*")), 'initialdir':str(Path.home())+ '/Accenture/Peticiones - NUEVO CALCULADOR INTERNACIONAL/0 - GESTION' },
                      Filenames.INCURRIDOS:{'title':'Excel de incurridos', 'filetypes':(("excel","*.xlsm"),("all files","*.*")), 'initialdir':str(Path.home())+ '/OneDrive - Accenture/Iberdrola/incurridos' }
               }
    

    def process_filename(self, cfg, elemento, ask=False):
        filename=""
        initial_dir=""
        try:
            initial_dir=cfg['files'][elemento.value]['path']
        except KeyError:
            initial_dir=Config.config_filenames[elemento]['initialdir']

        try:
            if ask:
                filename = \
                    askopenfilename(title = Config.config_filenames[elemento]['title'], 
                                    filetypes = Config.config_filenames[elemento]['filetypes'], 
                                    initialdir=initial_dir)
            else:
                filename = os.path.join(cfg['files'][elemento.value]['path'], cfg['files'][elemento.value]['name']) 
            print('->', filename)
            if not os.path.isfile(filename):
                raise FileNotFoundError()
        except (TypeError, KeyError, FileNotFoundError):
            filename = \
                askopenfilename(title = Config.config_filenames[elemento]['title'], 
                                filetypes = Config.config_filenames[elemento]['filetypes'], 
                                initialdir=initial_dir)
        return filename

    def __init__(self):
        Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing        
        self.cfg={}
        self.filenames={}
        
        with open(Config.config_file, "a+") as ymlfile:
            ymlfile.seek(0)
            self.cfg = yaml.safe_load(ymlfile)
        
        
        if not self.cfg or not self.cfg['files']:
            self.cfg={'files':{}}
            for f in Filenames:
                self.cfg['files'][f.value]={}
         
            
        for f in Filenames:
            self.filenames[f]=self.process_filename(self.cfg,f)

    def save(self):
        print(self.filenames)
        for f in Filenames:
            self.cfg['files'][f.value]['path'], self.cfg['files'][f.value]['name']=os.path.split(self.filenames[f])
        
        with open(Config.config_file, "w") as ymlfile:
            yaml.dump(self.cfg, ymlfile)


class ConfigView:
    def fetch(self,entries):
        for entry in entries:
            field = entry[0]
            text  = entry[1].get()
            print('%s: "%s"' % (field, text)) 
    
    def run(self):
        for f in Filenames:
            self.config.filenames[f]=self.ents[f].get()
        self.config.save()
        self.root.quit()
    
    def ask(self,field):
        filename=self.config.process_filename(self.config.cfg, field, True)
        if filename:
            self.ents[field].delete(0,tk.END)
            self.ents[field].insert(0, filename)
        

    def makeform(self,root):
        entries = {}
        buttons = {}
#         for field, filename in fields.items():
        for f in Filenames:
            row = tk.Frame(root)
            row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

            lab = tk.Label(row, width=15, text=f.value, anchor='w')
            lab.pack(side=tk.LEFT)
            
            entries[f] = tk.Entry(row, width=len(max(self.config.filenames.values(), key=len)))
            entries[f].insert(0, self.config.filenames[f])
            entries[f].pack(side=tk.LEFT)

            
            buttons[f] = tk.Button(row, 
                               text='...', 
                               command=lambda x=f: self.ask(x))
            buttons[f].pack(side=tk.LEFT, padx=5, expand=tk.YES)
                               
        return entries
    
    
    
    def __init__(self, config):
        self.root = tk.Tk()
        self.config=config
        
        self.ents = self.makeform(self.root)

        b2 = tk.Button(self.root, text='Quit', command=self.root.destroy)
        b2.pack(padx=5, pady=5, side=tk.RIGHT)        
        
        b1 = tk.Button(self.root, text='Ok', command=self.run)
        b1.pack(padx=5, pady=5, side=tk.RIGHT)

        self.root.mainloop()
        
if __name__ == '__main__':
    config=Config()
    
    c=ConfigView(config)
    
    print('fin')
    
    
    