import os
import threading
import time
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk

import serial
import serial.tools.list_ports
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

window1 = tk.Tk()
window1.title("Control GUI")

window2 = tk.Tk()
window2.title("BMS Logger")

##### Função da GUI da Unidade de Controlo #####

def controloGUI():
    frame = tk.Frame(window1)
    frame.pack()

    connect_device = tk.LabelFrame(frame, text="Connect Device")
    connect_device.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

    com_label = tk.Label(connect_device, text="Select COM Port:")
    com_label.grid(row=0, column=0, padx=5, pady=5)

    com_var = tk.StringVar(connect_device)
    ports = [port.device for port in serial.tools.list_ports.comports()]

    com_option = tk.OptionMenu(connect_device, com_var, *ports)
    com_option.grid(row=0, column=1)

    baudrate_label = tk.Label(connect_device, text="Baud Rate:")
    baudrate_label.grid(row=1, column=0, sticky="W", padx=5, pady=5)

    baud_rate = tk.IntVar(connect_device, 9600)
    baudrate_option = tk.OptionMenu(connect_device, baud_rate, 9600, 19200, 38400, 57600, 115200)
    baudrate_option.grid(row=1, column=1, sticky="W", padx=5, pady=5)

    def toggle_autoscroll():
        global autoscroll_enabled
        autoscroll_enabled = not autoscroll_enabled
        autoscroll_button.config(text="Autoscroll: " + ("On" if autoscroll_enabled else "Off"))

    def autoscroll():
        if autoscroll_enabled:
            text_output.yview(tk.END)
            text_output.after(100, autoscroll)

    serial_monitor_lable_frame = tk.LabelFrame(frame, text="Serial Monitor:")
    serial_monitor_lable_frame.grid(row=0, column=1, rowspan=2, padx=10, pady=10)

    text_output = tk.Text(serial_monitor_lable_frame, width=50, height=30, font=("Consolas", 9), bg="black", fg="white")
    text_output.grid(row=0, column=0)

    scrollbar = ttk.Scrollbar(serial_monitor_lable_frame, command=text_output.yview)
    scrollbar.grid(row=0, column=2, sticky='ns')

    text_output.config(yscrollcommand=scrollbar.set)

    def clear_text():
        text_output.delete(1.0, tk.END)

    clear_button = tk.Button(serial_monitor_lable_frame, text="Clear", command=clear_text)
    clear_button.grid(row=1, column=0)

    autoscroll_enabled = True
    autoscroll_button = tk.Button(serial_monitor_lable_frame, text="Autoscroll: On", command=toggle_autoscroll)
    autoscroll_button.grid(row=2, column=0)

    def connect():
        global ser
        port = com_var.get()
        try:
            ser = serial.Serial(port, baud_rate.get())
        except serial.SerialException as e:
            text_output.insert(tk.END, str(e) + "\n")
        else:
            text_output.insert(tk.END, "Connected to " + port + "\n")
            read_data()

    def disconnect():
        global ser
        if ser:
            ser.close()
            ser = None
            text_output.insert(tk.END, "Disconnected from " + com_var.get() + "\n")

    def read_data():
        global ser
        if ser:
            data = ser.read(ser.in_waiting).decode('utf-8', 'ignore')
            text_output.insert(tk.END, data)
            #text_output.see(tk.END) #autoscroll na nova function
        window1.after(5, read_data)

    connect_button = tk.Button(connect_device, text="Connect", width=10, command=connect)
    connect_button.grid(row=2, column=0, padx=5, pady=5)

    disconnect_button = tk.Button(connect_device, text="Disconnect", width=10, command=disconnect)
    disconnect_button.grid(row=2, column=1, padx=5, pady=5)

    def manual_input_send(): #acabar função adicionar um protocolo com uma keyword inicial para cada tipo de comando
        command = manual_input_send_command_entry.get()
        if command:
            ser.write(command.encode())
            manual_input_send_command_entry.delete(0, tk.END)

    manual_input_lableframe = tk.LabelFrame(frame, text="Manual Input")
    manual_input_lableframe.grid(row=2, column=1, padx=10, pady=10, sticky="nsew")

    manual_input_send_command_entry = tk.Entry(manual_input_lableframe, width=30)
    manual_input_send_command_entry.grid(row=0, column=0, padx=5, pady=5)

    manual_input_send_button = tk.Button(manual_input_lableframe, text="Send", width=10, command=manual_input_send)
    manual_input_send_button.grid(row=0, column=1, padx=5, pady=5)

    ##### Finalizar função battery_input_send do protocolo que envia os parametros da celula #####

    def battery_input_send():
        command = "SETV1-" + battery_input_nominalvoltage_entry.get() + "\n" + "-" + battery_input_nominalcapacity_entry.get() + "Ah\n" + "SETC1-" + battery_input_charge_standartcurrent_entry.get() + "\n" + "-" + battery_input_charge_limitedvoltage_entry.get() + "V\n" + "SETC2-" + battery_input_discharge_standartcurrent_entry.get() + "\n" + "SETV2-" + battery_input_discharge_cutoffdvoltage_entry.get() + "V\n" + "SETMAXTEMP-" + battery_input_maxtemp_entry.get() + "\n" + "-" + battery_input_model_entry.get()
        if command:
            ser.write(command.encode())
            #battery_input_nominalcapacity_entry.delete(0, tk.END) #Limpar input após o pressionar 'Set'

    battery_input_labelframe = tk.LabelFrame(frame, text="Battery Specifications")
    battery_input_labelframe.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

    battery_input_nominalvoltage_label = tk.Label(battery_input_labelframe, text="Nominal Voltage (V):")
    battery_input_nominalvoltage_label.grid(row=0, column=0, padx=5, pady=5)

    battery_input_nominalvoltage_entry = tk.Entry(battery_input_labelframe, width=5)
    battery_input_nominalvoltage = 3.2
    battery_input_nominalvoltage_entry.insert(0, battery_input_nominalvoltage)
    battery_input_nominalvoltage_entry.grid(row=0, column=1, padx=5, pady=5)

    battery_input_nominalcapacity_label = tk.Label(battery_input_labelframe, text="Norminal Capacity (Ah):")
    battery_input_nominalcapacity_label.grid(row=1, column=0, padx=5, pady=5)

    battery_input_nominalcapacity_entry = tk.Entry(battery_input_labelframe, width=5)
    battery_input_nominalcapacity = 100
    battery_input_nominalcapacity_entry.insert(0, battery_input_nominalcapacity)
    battery_input_nominalcapacity_entry.grid(row=1, column=1, padx=5, pady=5)

    battery_input_charge_standartcurrent_label = tk.Label(battery_input_labelframe, text="Charge - Standart Current (A):")
    battery_input_charge_standartcurrent_label.grid(row=2, column=0, padx=5, pady=5)

    battery_input_charge_standartcurrent_entry = tk.Entry(battery_input_labelframe, width=5)
    battery_input_charge_standartcurrent = 33
    battery_input_charge_standartcurrent_entry.insert(0, battery_input_charge_standartcurrent)
    battery_input_charge_standartcurrent_entry.grid(row=2, column=1, padx=5, pady=5)

    battery_input_charge_limitedvoltage_label = tk.Label(battery_input_labelframe, text="Charge - Limited Voltage (V):")
    battery_input_charge_limitedvoltage_label.grid(row=3, column=0, padx=5, pady=5)

    battery_input_charge_limitedvoltage_entry = tk.Entry(battery_input_labelframe, width=5)
    battery_input_charge_limitedvoltage = 3.65
    battery_input_charge_limitedvoltage_entry.insert(0, battery_input_charge_limitedvoltage)
    battery_input_charge_limitedvoltage_entry.grid(row=3, column=1, padx=5, pady=5)

    battery_input_discharge_standartcurrent = tk.Label(battery_input_labelframe, text="Discharge - Standart Current (A):")
    battery_input_discharge_standartcurrent.grid(row=4, column=0, padx=5, pady=5)

    battery_input_discharge_standartcurrent_entry = tk.Entry(battery_input_labelframe, width=5)
    battery_input_discharge_standartcurrent = 33
    battery_input_discharge_standartcurrent_entry.insert(0, battery_input_discharge_standartcurrent)
    battery_input_discharge_standartcurrent_entry.grid(row=4, column=1, padx=5, pady=5)

    battery_input_disccharge_cutoffdvoltage = tk.Label(battery_input_labelframe, text="Discharge - Cutoff Voltage (V):")
    battery_input_disccharge_cutoffdvoltage.grid(row=5, column=0, padx=5, pady=5)

    battery_input_discharge_cutoffdvoltage_entry = tk.Entry(battery_input_labelframe, width=5)
    battery_input_discharge_cutoffdvoltage = 2.5
    battery_input_discharge_cutoffdvoltage_entry.insert(0, battery_input_discharge_cutoffdvoltage)
    battery_input_discharge_cutoffdvoltage_entry.grid(row=5, column=1, padx=5, pady=5)

    battery_input_maxtemp = tk.Label(battery_input_labelframe, text="Max. Temperature (Celsius):")
    battery_input_maxtemp.grid(row=6, column=0, padx=5, pady=5)

    battery_input_maxtemp_entry = tk.Entry(battery_input_labelframe, width=5)
    battery_input_maxtemp = 45
    battery_input_maxtemp_entry.insert(0, battery_input_maxtemp)
    battery_input_maxtemp_entry.grid(row=6, column=1, padx=5, pady=5)

    battery_input_model = tk.Label(battery_input_labelframe, text="Model of the Battery:")
    battery_input_model.grid(row=7, column=0, padx=5, pady=5)

    battery_input_model_entry = tk.Entry(battery_input_labelframe, width=10)
    battery_input_model = "SP-LFP-100AHA(A)"
    battery_input_model_entry.insert(0, battery_input_model)
    battery_input_model_entry.grid(row=7, column=1, padx=5, pady=5)

    battery_input_send_button = tk.Button(battery_input_labelframe, text="Set", width=10, command=battery_input_send)
    battery_input_send_button.grid(row=8, column=0, columnspan=2, padx=5, pady=5)

    procedure_input_lableframe = tk.LabelFrame(frame, text="Battery Test")
    procedure_input_lableframe.grid(row=2, column=0, rowspan=2, padx=10, pady=10, sticky="nsew")

    procedure = tk.StringVar(procedure_input_lableframe)
    procedure.set("Select")

    def procedure_type():
        if procedure.get() == "Select":
            text_output.insert(tk.END, "\nProcedure wasn't selected\n")
        else:
            text_output.insert(tk.END, "\nTest selected: " + procedure.get() + "\n" + "The procedure is about to begin...\n")
            command = procedure.get()
            if command:
                ser.write(command.encode())

    procedure_type_lable = tk.Label(procedure_input_lableframe, text="Procedure:")
    procedure_type_lable.grid(row=0, column=0, padx=5, pady=5)

    procedure = tk.StringVar(procedure_input_lableframe, "Charging")
    procedure_type_option = tk.OptionMenu(procedure_input_lableframe, procedure, "Charging", "Discharging")
    procedure_type_option.grid(row=0, column=1, sticky="W", padx=5, pady=5)

    procedure_type_send_button = tk.Button(procedure_input_lableframe, text="Set", width=10, command=procedure_type)
    procedure_type_send_button.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

    def send_command(command):
        # Send command
        ser.write(command.encode())

    actions_input_lableframe = tk.LabelFrame(frame, text="Actions")
    actions_input_lableframe.grid(row=3, column=1, padx=10, pady=10, sticky="nsew")

    actions_input_send_button = tk.Button(actions_input_lableframe, text="Start", width=10, command=lambda: send_command("START"))
    actions_input_send_button.grid(row=0, column=0, padx=5, pady=5)

    actions_input_send_button = tk.Button(actions_input_lableframe, text="Pause", width=10, command=lambda: send_command("PAUSE"))
    actions_input_send_button.grid(row=0, column=1, padx=5, pady=5)

    actions_input_send_button = tk.Button(actions_input_lableframe, text="Stop", width=10, command=lambda: send_command("STOP"))
    actions_input_send_button.grid(row=0, column=2, padx=5, pady=5)

    ##### Ideia inicial era mostrar um plot a capcidade da bateria pela tensão (se possível em tempo real para monitorização)

    def plot_data():
        # Prompt user to select a log file
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if not file_path:
            return

        current = []
        charging_time = []

        # Read data from selected log file
        with open(file_path, 'r') as file:
            for line in file:
                line = line.strip()
                if line:
                    data = line.split(',')
                    current.append(float(data[0]))
                    charging_time.append(float(data[1]))

        # Clear the existing plot
        figure.clear()

        # Create a new plot
        axes = figure.add_subplot(111)
        axes.plot(current, charging_time, marker='o')

        # Set plot labels and title
        axes.set_xlabel('Charging Time (minutes)')
        axes.set_ylabel('Current (A)')
        axes.set_title('Battery Charging Time')

        # Update the canvas
        canvas.draw()

    plot_lableframe = tk.LabelFrame(frame, text="Battery Charging Plot")
    plot_lableframe.grid(row=0, column=3, rowspan=2, padx=10, pady=10)

    # Create a plot area
    figure = Figure(figsize=(5, 4), dpi=100)
    canvas = FigureCanvasTkAgg(figure, master=plot_lableframe)
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    # Create a toolbar for plot controls
    toolbar = NavigationToolbar2Tk(canvas, plot_lableframe)
    toolbar.pack(side=tk.TOP, pady=5)

    # Create a button to plot data
    plot_button = ttk.Button(plot_lableframe, text="Select Log File", command=plot_data)
    plot_button.pack(side=tk.BOTTOM)

    ##### As funções de cálculo do SOC e do SOH não foram finalizadas

    def calculate_soh(log_file):
        total_ah = 0.0

        with open(log_file, 'r') as file:
            first_line = file.readline()
            first_time, initial_current = map(float, first_line.strip().split(','))
            prev_time = first_time
            prev_current = initial_current

            for line in file:
                time, current = map(float, line.strip().split(', '))
                elapsed_time = time - prev_time
                average_current = (current + prev_current) / 2
                total_ah += (average_current * (elapsed_time / 60))
                prev_time = time
                prev_current = current

        return (total_ah / 100) * 100

    def calculate_soc(log_file):
        initial_soh = calculate_soh(log_file)
        final_soh = 100.0
        soc = (initial_soh / final_soh) * 100.0
        return soc

    def select_log_file():
        log_file_path = filedialog.askopenfilename(filetypes=[('Text Files', '*.txt')])
        if log_file_path:
            soh = calculate_soh(log_file_path)
            soc = calculate_soc(log_file_path)
            SoH_actual_label.config(text=f"SoH: {soh:.2f}%")
            SoC_actual_label.config(text=f"SoC: {soc:.2f}%")

    Battery_capacityhealth_labelframe = tk.LabelFrame(frame, text="Battery Actual Capacity and Health")
    Battery_capacityhealth_labelframe.grid(row=2, column=3, rowspan=2, padx=10, pady=10, sticky="nsew")

    SoH = "Not Calculated"
    SoH_actual_label = tk.Label(Battery_capacityhealth_labelframe, text="SoH: " + SoH)
    SoH_actual_label.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

    SoC = "Not Calculated"
    SoC_actual_label = tk.Label(Battery_capacityhealth_labelframe, text="SoC: " + SoC)
    SoC_actual_label.grid(row=0, column=0, columnspan=2, padx=5, pady=5)

    select_button = tk.Button(Battery_capacityhealth_labelframe, text="Select Log File", command=select_log_file)
    select_button.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

    #autoscroll() #Autoscrool necessita de ser corrigido, mas é uma feature que pode ser removida

M_Lines = ""
B_Lines = ""
P_Lines = ""
S01_Lines = ""
S02_Lines = ""

##### Função para conectar o BMS #####

def bmsLOG():

    # Get the directory path of the current script
    current_dir = os.path.dirname(os.path.realpath(__file__))

    # Generate a timestamp for the log file name
    timestamp = time.strftime("%Y%m%d_%H%M%S")

    # Define the log file name with the timestamp
    log_file_name = f"LOG_{timestamp}.txt"

    # Construct the full path to the log file
    log_file_path = os.path.join(current_dir, log_file_name)

    ##### Acabar Função receive_data do BMS_LOG para receber e processar a informação vinda do BMS em tempo real #####
    
    # Function to handle receiving data from Arduino
    def receive_data():
        while True:
            line = ser_BMS.readline().decode().rstrip('\r\n')  # Read a line from the serial port and decode it
            print(line)

            #Find 'S 01'
            index_p = line.find('S 01')
            data = line[index_p+2:index_p+6]

            # Split the data into individual values
            values = data.split()

            print(values)

            # if len(data) >= 16:
            #     Tipo = data[10]
            #     SubTipo = data[12:14]
            #     if Tipo == "P":
            #         P_Lines = P_Lines + data
            #         print("Received P line:", P_Lines)
                #Words = line.split(' ')
                #if (Words.__len__() < 2):
                #    continue
                #print(line)
                # if Tipo == "B" and (len(line) == 70):
                #     B_Lines = B_Lines + data
                #     print("Received B line:", B_Lines)
                # elif Tipo == "M" and (42 <= len(line) <= 44):
                #     M_Lines = M_Lines + data
                #     print("Received M line:", M_Lines)
                # elif Tipo == "S":
                #     if SubTipo == "01" and (len(line) == 106):
                #         S01_Lines = S01_Lines + data
                #         print("Received S01 line:", S01_Lines)
            # current_time = datetime.now().strftime('%H:%M:%S')
            # log_line = f'{current_time}: {line}'

            with open(log_file_path, 'a') as log_file:
                log_file.write(line + '\n')
                log_file.flush()  # Flush the buffer to ensure data is written immediately
                #print(line)  # Print data to console

    connect_device = tk.LabelFrame(window2, text="Connect Device")
    connect_device.grid(row=0, column=1, padx=10, pady=10)

    com_label = tk.Label(connect_device, text="Select COM Port:")
    com_label.grid(row=0, column=0, padx=5, pady=5)

    com_var = tk.StringVar(connect_device)
    ports = [port.device for port in serial.tools.list_ports.comports()]

    com_option = tk.OptionMenu(connect_device, com_var, *ports)
    com_option.grid(row=0, column=1)

    baudrate_label = tk.Label(connect_device, text="Baud Rate:")
    baudrate_label.grid(row=1, column=0, sticky="W", padx=5, pady=5)

    baud_rate = tk.IntVar(connect_device, 115200)
    baudrate_option = tk.OptionMenu(connect_device, baud_rate, 9600, 19200, 38400, 57600, 115200)
    baudrate_option.grid(row=1, column=1, sticky="W", padx=5, pady=5)

    def connect():
        global ser_BMS
        port = com_var.get()
        try:
            ser_BMS = serial.Serial(port, baud_rate.get())
        except serial.SerialException as e:
            print(str(e) + "\n")
        else:
            print("Connected to " + port + "\n")
            # Start a separate thread to handle receiving data in the background
            threading.Thread(target=receive_data, daemon=True).start()
            # Create a log file (clearing any existing data)
            with open(log_file_path, 'w') as log_file:
                log_file.write('Log file created\n')

    def disconnect():
        global ser_BMS
        if ser_BMS:
            ser_BMS.close()
            ser_BMS = None
            print("Disconnected from " + com_var.get() + "\n")

    connect_button = tk.Button(connect_device, text="Connect", width=10, command=connect)
    connect_button.grid(row=2, column=0, padx=5, pady=5)

    disconnect_button = tk.Button(connect_device, text="Disconnect", width=10, command=disconnect)
    disconnect_button.grid(row=2, column=1, padx=5, pady=5)

    def manual_input_send():
        command = manual_input_send_command_entry.get()
        if command:
            ser_BMS.write(command.encode())
            manual_input_send_command_entry.delete(0, tk.END)

    manual_input_lableframe = tk.LabelFrame(window2, text="Manual Input")
    manual_input_lableframe.grid(row=1, column=1, padx=10, pady=10)

    manual_input_send_command_entry = tk.Entry(manual_input_lableframe, width=30)
    manual_input_send_command_entry.grid(row=0, column=0, padx=5, pady=5)

    manual_input_send_button = tk.Button(manual_input_lableframe, text="Send", width=10, command=manual_input_send)
    manual_input_send_button.grid(row=0, column=1, padx=5, pady=5)

controloGUI()

bmsLOG()

window1.mainloop()

window2.mainloop()