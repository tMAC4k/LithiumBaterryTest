import tkinter as tk
from tkinter import filedialog
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.pyplot as plt
import numpy as np
import os

index = -1  # Initialize the selected line index

current_directory = os.path.dirname(os.path.abspath(__file__))

def trataTramasBMS():
    file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    if file_path:
        print("\n -- Selected file:", file_path)
        M_Lines = ""
        B_Lines = ""
        S01_Lines = ""
        S02_Lines = ""
        S03_Lines = ""

        ClockBase = "000000|"
        Clock = "000000|"
        ClockReady = 0

        with open(file_path, 'r') as infile:
            Lines = infile.readlines()
            for Line in Lines:
                if len(Line) > 14:
                    Tipo = Line[10]
                    SubTipo = Line[12:14]
                    Words = Line.split(' ')
                    if (Words.__len__() < 2):
                        continue
                    Line = Clock + Line
                    if ClockReady == 1:
                        if Tipo == "B" and (len(Line) == 70):
                            B_Lines = B_Lines + Line
                        elif Tipo == "M" and  (42 <= len(Line) <= 44):
                            M_Lines = M_Lines + Line
                        elif Tipo == "S":
                            if SubTipo == "01" and (len(Line) == 106):
                                S01_Lines = S01_Lines + Line
                            elif SubTipo == "02"  and (len(Line) == 82):
                                S02_Lines = S02_Lines + Line
                            #elif SubTipo == "03":
                            #    S03_Lines = S03_Lines + Line                   
                    if Tipo == "R":
                        ClockReady = 1
                        Counter = 0
                        #ClockBase = Words[4] + '|'
                        ClockBase = "000000" + '|'
                        Clock = ClockBase

            #file_path_Bateria = os.path.join(current_directory, "BateriaGeral.txt")

            #with open(file_path_Bateria, 'w') as outfile:
            #    outfile.write(B_Lines)

            file_path_S01 = os.path.join(current_directory, "BateriaTracao01.txt")

            with open(file_path_S01, 'w') as outfile:
                outfile.write(S01_Lines)

            file_path_S02 = os.path.join(current_directory, "BateriaTracao02.txt")

            #with open(file_path_S02, 'w') as outfile:
            #    outfile.write(S02_Lines)

            #with open("S03.txt", 'w') as outfile:
            #    outfile.write(S03_Lines)
    else:
        print("\n -- No file selected.")

def plot_data():
    Out = []
    DataInicial = 0
    Tempo = []
    Cells = [[] for _ in range(16)]

    # Prompt user to select a log file
    file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    if not file_path:
        return
    
    with open(file_path, 'r') as file:
        for Line in file:
            if len(Line) > 14:
                words = Line.split(' ')
                Out.append(words[0] + " " + words[1] + " " +
                        ' '.join(words[4:16]) + "\n")
                # Tempo
                segundos = int(words[0][7:9])*3600 + int(words[0][10:12])*60 + int(words[0][13:15])
                DataActual = int(words[0][0:6])
                if DataInicial == 0:
                    DataInicial = DataActual
                if DataInicial < DataActual:
                    segundos += (DataActual - DataInicial)*24*3600
                Tempo.append(segundos)
                # Cells
                for i in range(16):
                    Cells[i].append(int(words[4+i], 16))

    Out2 = "Tempo Tipo C0[mV/10] C1[mV/10] C2[mV/10] C3[mV/10] C4[mV/10] C5[mV/10] C6[mV/10] C7[mV/10] C8[mV/10] C9[mV/10] C10[mV/10] C11[mV/10] C12[mV/10] C13[mV/10] C14[mV/10] C15[mV/10]\n"
    Out2 += ''.join(Out)

    with open("BateriaTracao0_Out.txt", 'w') as outfile:
        outfile.write(Out2)

    # Define a list of 16 distinguishable colors
    colors = plt.cm.tab20(np.linspace(0, 1, 16))

    # Plotting
    fig, ax = plt.subplots()

    lines = []
    for i in range(16):
        line, = ax.plot(Tempo, Cells[i], label="C" + str(i), color=colors[i])
        lines.append(line)

    def on_key(event):
        global index  # Use the global index variable

        if event.key == 'enter':
            index += 1  # Increment the index on each 'Enter' key press

            # Wrap the index to ensure it stays within the valid range
            index %= len(lines)

            for i, line in enumerate(lines):
                if i == index:
                    plt.setp(line, linewidth=3.5, label="C" + str(i) + " (Selected)")  # Highlight the selected line
                else:
                    plt.setp(line, linewidth=1.0, label="C" + str(i))  # Reset the linewidth for other lines

            ax.legend()  # Update the legend to show the selected cell number

            fig.canvas.draw()

    # Connect the key press event handler to the figure
    fig.canvas.mpl_connect('key_press_event', on_key)

    ax.set(xlabel='tempo [s]', ylabel='Tensão [mV/10]', title='Tensão da(s) Célula(s)')
    ax.grid()

    plt.show()

root = tk.Tk()
root.title("TrataTramas e Plotter")
root.geometry("300x250")

frame = tk.Frame(root)
frame.pack()

tratatramasBMS_lableframe = tk.LabelFrame(frame, text="Trata Tramas")
tratatramasBMS_lableframe.grid(row=0, column=0, padx=10, pady=10)

tratatramasBMS_lable = tk.Label(tratatramasBMS_lableframe, text="Select a Tramas.txt File:")
tratatramasBMS_lable.grid(row=0, column=0, padx=10, pady=10)

tratatramasBMS_button = tk.Button(tratatramasBMS_lableframe, text="Select File", command=trataTramasBMS)
tratatramasBMS_button.grid(row=1, column=0, padx=10, pady=10)

plot_lableframe = tk.LabelFrame(frame, text="Battery Charging/Discharging Plot")
plot_lableframe.grid(row=1, column=0, padx=10, pady=10)

plot_frame = tk.Label(plot_lableframe, text="Select a BateriaTracao01.txt file:")
plot_frame.grid(row=0, column=0, padx=10, pady=10)

# Create a button to plot data
plot_button = tk.Button(plot_lableframe, text="Select file", command=plot_data)
plot_button.grid(row=1, column=0, padx=10, pady=10)

root.mainloop()