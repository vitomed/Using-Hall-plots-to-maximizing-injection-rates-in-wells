import math
import tkinter as tk
from tkinter import messagebox as mb
from tkinter import filedialog as tkFileDialog

import numpy as np
import pandas as pd
# --- matplotlib ---
import sys
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import os

# ---
#from rdp import rdp


#-------------------------------------------------------------------------------class MainApp
class MainApp(tk.Frame):

    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.parent.title('График Холла') 
        from tkinter import Tk, ttk

   
       
#------------------------------------------------------------------------------- функция Hall plot
#функция, которая формирует данные для графика Холла
#переменные на вход: массив данных из файла эксель: закачка (м3), время работы под закачкой(ч), забойное давление(атм), пластовое давление (атм)
#переменные на выходе: 2 массива: накопленная закачка и сумм(deltap*t) 
    
def Hallplot(X):

    mass_W = X[0:,1] # закачка,(м3)
    mass_t_for_i = X[0:,2] # время под закачкой, (ч)
    mass_pw = X[0:,3] # забойное давление, (атм)
    mass_pp = X[0:,4] # пластовое давление, (атм)

    for i in range(len(mass_W)-1,-1,-1):
        if ((np.isnan(mass_W[i])) or (np.isnan(mass_t_for_i[i]))or(np.isnan(mass_pw[i]))or(np.isnan(mass_pp[i]))or
           (mass_W[i]==0)or(mass_t_for_i[i]==0)or(mass_pw[i]==0)or(mass_pp[i]==0)or(mass_pw[i]<mass_pp[i])):
            X=np.delete(X,(i),0)
            
    date = pd.to_datetime(X[0:,0], dayfirst = True)

    mass_W = X[0:,1] # закачка,(м3)
    mass_t_for_i = X[0:,2] # время под закачкой, (ч)
    mass_pw = X[0:,3] # забойное давление, (атм)
    mass_pp = X[0:,4] # пластовое давление, (атм)

    print(date)
    mass_sum_deltaP_t = []
    sum_W = []
    
    if(len(X)==0):
        mb.showerror('Ошибка','Пустой файл')
    else:
        mass_sum_deltaP_t.append((mass_pw[0]-mass_pp[0])*mass_t_for_i[0]/24)
        sum_W.append(mass_W[0])
    
        for j in range(1,len(mass_pw)):
           mass_sum_deltaP_t.append(mass_sum_deltaP_t[j-1] + (mass_pw[j]-mass_pp[j])*mass_t_for_i[j]/24) # переводим в сутки

           sum_W.append(sum_W[j-1] +mass_W[j] )


    return (sum_W, mass_sum_deltaP_t,date)


#------------------------------------------------------------------------------- считывание доп. параметров
# на вход: массив окон, откуда считываем
# на выход: значения из окон
def get_input_par_val(arr):
        mass_par_input = []
        for i in range(0,6):
            mass_par_input.append(float(arr[i].get()))
        return(mass_par_input)

 #------------------------------------------------------------------------------- отрисовка Hall plot
def draw_plot(data_x,data_y,root):
    for i in range (0,len(data_x)):
        data_x[i]=data_x[i]/1000
        data_y[i]=data_y[i]/1000
    f = Figure(figsize=(8,6))
    a = f.add_subplot(111)
    a.plot(data_x,data_y,'g-o')
    a.set_title('График Холла') 
    a.set_xlabel("Накопленная закачка, м3*10^3")
    a.set_ylabel("Sum(delta_p*t), атм*сутки*10^3")  
    a.grid()
    
    canvas1 = FigureCanvasTkAgg(f, master= root)
    canvas1.draw()   
    canvas1.get_tk_widget().place(x=220,y=10)
    toolbar1 = NavigationToolbar2TkAgg(canvas1,root) 
    toolbar1.place(x = 400, y = 450) 

    
#------------------------------------------------------------------------------- функция skin
#функция, которая определяет значение skin = tg(alpha)*kw*h/(18.41*bw*muw) - ln(re/rw)
#переменные на вход: массив дат, массив значений tg углов наклона, массив значений параметров
#переменные на выходе: массив дат,  массив значений skin

def skin (date,tg, arr_par) :
    arr_skin = []
    arr_par=get_input_par_val(arr)
    for i in range(0, len(date)-1):
        arr_skin.append(tg[i]*arr_par[-3]*arr_par[-4]/(18.41*arr_par[-6]*arr_par[-5])-math.log(arr_par[-2]/arr_par[-1])) # 18.41 - российские промысловые
    print(arr_skin)
    draw_plot_skin(date[:len(date)-1], arr_skin,root)
#------------------------------------------------------------------------------- функция tg_alpha
#функция, которая считает tg угола наклона
#переменные на вход: коррдинаты точек графика Холла
#переменные на выходе: массив значений tg угла наклона

def tg_alpha(X_from_Hallplot, Y_from_Hallplot):
    mass_tg = []  
    
    for i in range(0,len(X_from_Hallplot)-1):
        mass_tg.append((Y_from_Hallplot[i+1] -Y_from_Hallplot[i] )/(X_from_Hallplot[i+1] - X_from_Hallplot[i]))    

    return(mass_tg)
#------------------------------------------------------------------------------- отрисовка скина
# вызывается из функции skin
# на вход: массив со значениями дат, массив со значениями скина
def draw_plot_skin(data_x_skin, data_y_skin,root):    
    f2 = Figure(figsize=(8,6))
    b = f2.add_subplot(111)
    b.plot(data_x_skin, data_y_skin,'g-o')
    b.set_title('СКИН') 
    b.set_xlabel("Дата")
    b.set_ylabel("СКИН")  
    b.grid()
    
    canvas2 = FigureCanvasTkAgg(f2, master= root)
    canvas2.draw()   
    canvas2.get_tk_widget().place(x=220,y=500)
    toolbar2 = NavigationToolbar2TkAgg(canvas2,root) 
    toolbar2.place(x = 400, y = 700) 
    
#------------------------------------------------------------------------------- сглаживание
def smooth(d,kernel_size):
    if kernel_size % 2 == 0:
        kernel_size -= 1
    #print(kernel_size)

    # ---smoothing---
    ynew3 = signal.savgol_filter(d, int(kernel_size), 2, mode='nearest')
    d=ynew3

    return (d)
#------------------------------------------------------------------------------- работа после нажатия кнопки "Открыть"
# происходит загрузка данных из выбранного пользователем файла, после этого отрисовка графика Холла
def button_clicked():
    op=tkFileDialog.askopenfilename()

    global tg_alpha_
    global date
    tg_alpha_ = []
    XX1 = []
    YY1 = []
    
    l1['text']=os.path.basename(op)                                             # вывод имени считываемого файла
    
    X = np.array(pd.read_excel(op,sep = ';')) 
    XX1,YY1,date = Hallplot(X)  #  график Hall
   
    tg_alpha_ = tg_alpha(XX1,YY1) # tg угла наклона

    draw_plot(XX1,YY1,root)

#-------------------------------------------------------------------------------main
if __name__ == "__main__":

    root = tk.Tk()
    root.geometry("830x980")
    root.resizable(0, 0)
    obj = MainApp(root)
    
    mass_name_par = ["Bw","mu_w, cp","kw, md","h, м", "re, м", "rw, м"] # переменные для ввода
    mass_val_par = [1.011,0.36,0.5,10,100,0.09144] # значения по умолчанию

    arr=[]
    for i in range(0,6):
        e = tk.Entry(root)
        e.insert(0,mass_val_par[i])
        l = tk.Label(root, text= mass_name_par[i])
        e.place(x = 80, y = 25 + i*50)  
        l.place(x = 20, y = 25 + i*50)
        arr.append(e)
    b1 = tk.Button(root,text="Открыть",width = 25, command=button_clicked)
    b1.place(x = 15,y = 350) 
    
    b2 = tk.Button(root, text="Рассчитать скин",width = 25, command=lambda: skin(date, tg_alpha_,arr))
    b2.place(x = 15,y = 400)
    
    l1=tk.Label(root)
    l1.place(x = 90,y = 315)
    
#    scale_smooth=tk.Scale(root,orient='horizontal',length=180)
#    scale_smooth.place(x=10,y=450)
#    
#    b_sm = tk.Button(root,text="Сгладить",width = 25, command=lambda: skin(tg_alpha_,arr,1))
#    b_sm.place(x = 10,y = 500)
   
    root.mainloop() 