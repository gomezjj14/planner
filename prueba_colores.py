from tkinter import *
import tkinter.ttk as ttk

def fixed_map(option):
    # Fix for setting text colour for Tkinter 8.6.9
    # From: https://core.tcl.tk/tk/info/509cafafae
    #
    # Returns the style map for 'option' with any styles starting with
    # ('!disabled', '!selected', ...) filtered out.

    # style.map() returns an empty list for missing options, so this
    # should be future-safe.
    return [elm for elm in style.map('Treeview', query_opt=option) if
      elm[:2] != ('!disabled', '!selected')]

style = ttk.Style()
style.map('Treeview', foreground=fixed_map('foreground'),
          background=fixed_map('background'))

class Test(Frame):

    def __init__(self):
        Frame.__init__(self)
        self.pack()
        self.listbox()
        self.buttons()

    def listbox(self):
        global new_customer_lb

        scrollbar = Scrollbar(self, orient="vertical")
        new_customer_lb = ttk.Treeview(self, columns=('ID','First Name','Last Name'))
        new_customer_lb['show']='headings'
        new_customer_lb.heading('#1', text= 'ID')
        new_customer_lb.column('#1', width=50, stretch=NO)
        new_customer_lb.heading('#2', text= 'First Name')
        new_customer_lb.column('#2', width=100, stretch=NO)
        new_customer_lb.heading('#3', text= 'Last Name')
        new_customer_lb.column('#3', width=100, stretch=NO)
        new_customer_lb.configure(yscroll = scrollbar.set, selectmode="browse")
        scrollbar.config(command=new_customer_lb.yview)
        new_customer_lb.pack()


    def buttons(self):
        load = Button(self, text='show customers', command=lambda:self.load_working_customers())
        test = Button(self, text='test new colors', command=lambda:self.test_colors())
        load.pack()
        test.pack()

    def load_working_customers(self):
        new_customer_lb.delete(*new_customer_lb.get_children())
        for a in range(0,10):            
            new_customer_lb.insert('','end', values=(a,'first','last'))

    def test_colors(self):
        new_customer_lb.delete(*new_customer_lb.get_children())                 

        new_customer_lb.tag_configure("evenrow",background='white',foreground='black')
        new_customer_lb.tag_configure("oddrow",background='black',foreground='white')
        for a in range(0,10):            
            if a % 2 == 0:
                new_customer_lb.insert('','end', values=(a,'first','last'), tags=('evenrow',))
            if a % 2 != 0:
                new_customer_lb.insert('','end', values=(a,'first','last'), tags=('oddrow',))

root = Tk()
app = Test()
app.mainloop()