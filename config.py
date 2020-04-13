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

class Config:
    config_file='config.yml'
    filenames={'planner':{'title':'Extracción de planner', 'filetypes':(("excel","*.xlsx"),("all files","*.*")), 'initialdir':str(Path.home())+ '/Downloads' },
               'gestion':{'title':'Excel de Gestion', 'filetypes':(("excel","*.xlsx"),("all files","*.*")), 'initialdir':str(Path.home())+ '/Accenture/Peticiones - NUEVO CALCULADOR INTERNACIONAL/0 - GESTION' },
               'incurridos':{'title':'Excel de incurridos', 'filetypes':(("excel","*.xlsm"),("all files","*.*")), 'initialdir':str(Path.home())+ '/OneDrive - Accenture/Iberdrola/incurridos' }}
    

    def process_filename(self, cfg, elemento):
        filename=""
        initial_dir=""
        try:
            initial_dir=cfg['files'][elemento]['path']
        except KeyError:
            initial_dir=Config.filenames[elemento]['initialdir']

        try:
            filename = os.path.join(cfg['files'][elemento]['path'], cfg['files'][elemento]['name']) 
            print('->', filename)
            if not os.path.isfile(filename):
                raise FileNotFoundError()
        except (TypeError, KeyError, FileNotFoundError):
            filename = \
                askopenfilename(title = Config.filenames[elemento]['title'], 
                                filetypes = Config.filenames[elemento]['filetypes'], 
                                initialdir=initial_dir)
        return filename

    def __init__(self):
        Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing        
        self.cfg={}

        with open(Config.config_file, "r") as ymlfile:
            self.cfg = yaml.safe_load(ymlfile)
        
        if not self.cfg or not self.cfg['files']:
            self.cfg={'files':{}}
            
        self.incurridos_filename = self.process_filename(self.cfg,'incurridos') 
        self.planner_filename = self.process_filename(self.cfg,'planner') 
        self.gestion_filename = self.process_filename(self.cfg,'gestion') 

    def save(self):
        self.cfg['files']['incurridos']['path'], self.cfg['files']['incurridos']['name']=os.path.split(self.incurridos_filename)
        self.cfg['files']['planner']['path'], self.cfg['files']['planner']['name']=os.path.split(self.planner_filename)
        self.cfg['files']['gestion']['path'], self.cfg['files']['gestion']['name']=os.path.split(self.gestion_filename)
        with open(Config.config_file, "w") as ymlfile:
            yaml.dump(self.cfg, ymlfile)


class ConfigView:
    def fetch(self,entries):
        for entry in entries:
            field = entry[0]
            text  = entry[1].get()
            print('%s: "%s"' % (field, text)) 
    
    def run(self):
        print(self.config.cfg)
        self.config.gestion_filename=self.ents['Gestión'].get()
        self.config.incurridos_filename=self.ents['Incurridos'].get()
        self.config.planner_filename=self.ents['Planner'].get()
        print(self.config)
        self.config.save()
        

    def makeform(self,root,fields):
        entries = {}
        for field, filename in fields.items():
            row = tk.Frame(root)
            row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

            lab = tk.Label(row, width=15, text=field, anchor='w').pack(side=tk.LEFT)
            
            ent = tk.Entry(row, width=len(max(fields.values(), key=len)))
            ent.insert(0, filename)
            ent.pack(side=tk.LEFT)

            
            button = tk.Button(row, 
                               text="...", 
                               command=quit).pack(side=tk.LEFT, padx=5, expand=tk.YES)
                               
            entries[field] = ent
        return entries
    
    
    
    def __init__(self, config):
        root = tk.Tk()
        self.config=config
        
        fields={'Gestión':config.gestion_filename, 'Planner':config.planner_filename, 'Incurridos':config.incurridos_filename}
        
        self.ents = self.makeform(root, fields)

        b2 = tk.Button(root, text='Quit', command=root.destroy)
        b2.pack(padx=5, pady=5, side=tk.RIGHT)        
        
        b1 = tk.Button(root, text='Ok', command=self.run)
        b1.pack(padx=5, pady=5, side=tk.RIGHT)
        

        print(root.wait_window(root))
        root.mainloop()
        
if __name__ == '__main__':
    config=Config()
    
    c=ConfigView(config)
    
    print('fin')
    
    
    