import customtkinter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np
import serial
import threading

ser = serial.Serial('com3', 9600)

customtkinter.set_default_color_theme("dark-blue")

app = customtkinter.CTk()
app.title("Logic Analyzer")

samples = 200  # taken
SPP = 50  # displayed

Channel_on = "0"
channels = [[], [], [], [], [], [], [], []]
t = list(range(0, SPP))
times = [0]*samples
freq = [0, 0, 0, 0, 0, 0, 0, 0]
freq_count = 0
dc_counter = 0
duty_cycle = [0, 0, 0, 0, 0, 0, 0, 0]


Runnung_Flag = True
DataDisplayed_Flag = True
flag_error = 0

# error = 100
# def check_freq(frequencies):
#     if len(frequencies) == 0:
#         return 0
#     elif len(frequencies) == 1:
#         return frequencies[0]
#     # print(frequencies)
#     mean = np.mean(frequencies)
#     max_freq = np.max(frequencies)
#     min_freq = np.min(frequencies)

#     if ((max_freq - min_freq)/2 - mean) < error:
#         return mean
#     if (max_freq - mean) > error or (mean - min_freq) > error:
#         if (max_freq - mean) > (mean - min_freq):
#             frequencies = np.delete(frequencies, np.argmax(frequencies))
#         else:
#             frequencies = np.delete(frequencies, np.argmin(frequencies))
#         mean = check_freq(frequencies)
#     return mean


def calculate_freq(start, end):
    ticks = end - start
    return (1/(ticks * 125 * 10**(-9)))


def Read_thread():
    global dc_counter
    global freq_count
    global times
    global channels
    global Runnung_Flag
    global DataDisplayed_Flag
    global ser
    global SPP
    global flag_error

    while (Runnung_Flag):
        if (DataDisplayed_Flag):
            for i in range(samples):
                Frame = ser.read(7)
                data = Frame[1]
                # Convert the slice into an integer
                time = int.from_bytes(Frame[2:6], byteorder='big')
                # Append the integer to 'times'
                times[i] = time
                binary_num = bin(data)[2:].zfill(8)

                for k in range(8):
                    channels[k].append(int(binary_num[7-k]))

            for i in range(8):
                time1 = 0
                time2 = 0
                frequencies = []
                for j in range(5, samples-1):
                    if channels[i][j] == 0 and channels[i][j+1] == 1:
                        time1 = times[j+1]
                        for k in range(j+1, samples-1):
                            if channels[i][k] == 0 and channels[i][k+1] == 1:
                                time2 = times[k+1]
                                frequencies.append(calculate_freq(time1, time2))
                                break
                frequencies = np.array(frequencies)
                if len(frequencies) == 0:
                    freq[i] = 0
                else:
                    freq[i] = frequencies.mean()
            for i in range(8):
                time1 = 0
                time2 = 0
                time3 = 0
                DutyCycle = []
                for j in range(5, samples-1):
                    if channels[i][j] == 0 and channels[i][j+1] == 1:
                        time1 = times[j+1]
                        for k in range(j+1, samples-1):
                            if channels[i][k] == 1 and channels[i][k+1] == 0:
                                time2 = times[k+1]
                                for m in range(k+1, samples-1):
                                    if channels[i][m] == 0 and channels[i][m+1] == 1:
                                        time3 = times[m+1]
                                        DutyCycle.append(((time2-time1) /(time3-time1))*100)
                                        dc_counter += 1
                                        break
                                break
                DutyCycle = list(set(DutyCycle))
                DutyCycle = np.array(DutyCycle)
                if len(DutyCycle) == 0:
                    duty_cycle[i] = 0
                else:
                    duty_cycle[i] = DutyCycle.mean()
            DataDisplayed_Flag = False
            print("Readed")
            # for i in range(8):
            #     print(f"channel{i}: freq={int(freq[i])}, DC = {int(duty_cycle[i])}")
        else:
            for j in range(int(samples / SPP)):
                for i in range(8):
                    draw_signal(channels[i][j * SPP: j * SPP + SPP], times[j * SPP: j * SPP + SPP], i)
            channels = [[], [], [], [], [], [], [], []]
            DataDisplayed_Flag = True
            print("Displayed")
            ser.write(bytes(f'G{Channel_on}', 'utf-8'))
            print(bytes(f'G{Channel_on}', 'utf-8'))


home_frame = customtkinter.CTkFrame(master=app)
home_frame.grid(row=0, column=0, sticky="ns")

new_frame = customtkinter.CTkFrame(master=app)
new_frame.grid_columnconfigure(0, weight=1)

label_frame = customtkinter.CTkFrame(master=home_frame)
label_frame.pack(padx=10, pady=10)
tklabel = customtkinter.CTkLabel(
    master=label_frame, text='\t\t\t\t\t             Logic Analyzer     \t\t\t\t\t', font=('arial', 22))
tklabel.pack(padx=10, pady=1)

fig = [0, 0, 0, 0, 0, 0, 0, 0]
newfig = [0, 0, 0, 0, 0, 0, 0, 0]
ax = [0, 0, 0, 0, 0, 0, 0, 0]
newax = [0, 0, 0, 0, 0, 0, 0, 0]
frame = [0, 0, 0, 0, 0, 0, 0, 0]
new_frame = [0, 0, 0, 0, 0, 0, 0, 0]
line = [0, 0, 0, 0, 0, 0, 0, 0]
newline = [0, 0, 0, 0, 0, 0, 0, 0]
freq_labels = [0, 0, 0, 0, 0, 0, 0, 0]
duty_cycle_labels = [0, 0, 0, 0, 0, 0, 0, 0]
y = list(np.full(SPP, 0.5))
canvases = []
newcanvases = []
index = 0


def back_to_home():
    global Channel_on
    new_frame[index].grid_forget()
    home_frame.grid(row=0, column=0, sticky="nsew")
    Channel_on = "0"


def channel0_action_button():
    global Channel_on
    global index
    index = 0
    home_frame.grid_forget()
    new_frame[index].grid(row=0, column=0, sticky="nsew")
    Channel_on = "1"


def channel1_action_button():
    global Frequency
    global DutyCycle
    global index
    global Channel_on
    index = 1
    home_frame.grid_forget()
    new_frame[index].grid(row=0, column=0, sticky="nsew")
    Frequency = ""
    DutyCycle = ""
    Frequency = "{:07d}".format(int(freq[index]))
    DutyCycle = "{:02d}".format(int(duty_cycle[index]))
    Channel_on = "2"


def channel2_action_button():
    global index
    global Channel_on
    index = 2
    home_frame.grid_forget()
    new_frame[index].grid(row=0, column=0, sticky="nsew")
    Channel_on = "3"


def channel3_action_button():
    global index
    global Channel_on
    index = 3
    home_frame.grid_forget()
    new_frame[index].grid(row=0, column=0, sticky="nsew")
    Channel_on = "4"


def channel4_action_button():
    global index
    global Channel_on
    index = 4
    home_frame.grid_forget()
    new_frame[index].grid(row=0, column=0, sticky="nsew")
    Channel_on = "5"


def channel5_action_button():
    global index
    global Channel_on
    index = 5
    home_frame.grid_forget()
    new_frame[index].grid(row=0, column=0, sticky="nsew")
    Channel_on = "6"


def channel6_action_button():
    global index
    global Channel_on
    index = 6
    home_frame.grid_forget()
    new_frame[index].grid(row=0, column=0, sticky="nsew")
    Channel_on = "7"


def channel7_action_button():
    global index
    global Channel_on
    index = 7
    home_frame.grid_forget()
    new_frame[index].grid(row=0, column=0, sticky="nsew")
    Channel_on = "8"


channels_action_buttons = [channel0_action_button, channel1_action_button, channel2_action_button,
                           channel3_action_button, channel4_action_button, channel5_action_button, channel6_action_button, channel7_action_button]


for i in range(8):
    frame[i] = customtkinter.CTkFrame(master=home_frame)
    frame[i].pack(padx=10, pady=1)
    new_frame[i] = customtkinter.CTkFrame(master=app)
    new_frame[i].grid_columnconfigure(0, weight=1)

    label_frame = customtkinter.CTkFrame(master=new_frame[i])
    label_frame.pack(padx=10, pady=10)
    tklabel = customtkinter.CTkLabel(
        master=label_frame, text=f'\t\t\t\t\t       Channel {i}\t\t\t\t\t\t', font=('arial', 22))
    tklabel.pack(padx=10, pady=1)
    label_frame = customtkinter.CTkFrame(master=frame[i])
    label_frame.pack(side='left', padx=10, pady=10)

    button = customtkinter.CTkButton(master=label_frame, text=f'Channel {i}', font=(
        'arial', 20), command=channels_action_buttons[i])
    button.pack()

    fig[i], ax[i] = plt.subplots(figsize=(10, 1))
    newfig[i], newax[i] = plt.subplots(figsize=(10, 5))
    ax[i].set_ylim(-0.5, 1.5)
    newax[i].set_ylim(-0.5, 1.5)
    fig[i].set_facecolor(
        'white' if app._get_appearance_mode() == 'light' else 'black')
    newfig[i].set_facecolor(
        'white' if app._get_appearance_mode() == 'light' else 'black')
    ax[i].set_facecolor('white' if app._get_appearance_mode()
                        == 'light' else 'black')
    newax[i].set_facecolor(
        'white' if app._get_appearance_mode() == 'light' else 'black')
    ax[i].axis('off')
    newax[i].axis('off')
    line[i], = ax[i].step(t, y, 'b-')
    newline[i], = newax[i].step(t, y, 'b-')

    canvas = FigureCanvasTkAgg(fig[i], master=frame[i])
    newcanvas = FigureCanvasTkAgg(newfig[i], master=new_frame[i])

    canvas_widget = canvas.get_tk_widget()
    newcanvas_widget = newcanvas.get_tk_widget()

    canvas_widget.pack(side=customtkinter.TOP,
                       fill=customtkinter.BOTH, expand=1)
    newcanvas_widget.pack(side=customtkinter.TOP,
                          fill=customtkinter.BOTH, expand=1)

    canvases.append(canvas)
    newcanvases.append(newcanvas)

    fr = customtkinter.CTkFrame(master=new_frame[i])
    fr.pack(padx=10, pady=10)

    fr2 = customtkinter.CTkFrame(master=fr)
    fr2.pack(padx=10, pady=10)

    label = customtkinter.CTkLabel(master=fr2, text='Freqancy:')
    label.pack(side='left', padx=10, pady=10)

    fr3 = customtkinter.CTkFrame(master=fr2)
    fr3.pack(side='left', padx=10, pady=10)

    freq_labels[i] = customtkinter.CTkLabel(master=fr3, text='0')
    freq_labels[i].pack(padx=10, pady=10)

    label = customtkinter.CTkLabel(master=fr2, text='Duty Cycle:')
    label.pack(side='left', padx=10, pady=10)

    fr3 = customtkinter.CTkFrame(master=fr2)
    fr3.pack(side='left', padx=10, pady=10)

    duty_cycle_labels[i] = customtkinter.CTkLabel(master=fr3, text='0')
    duty_cycle_labels[i].pack(padx=10, pady=10)

    back_button = customtkinter.CTkButton(
        master=fr, text='Back', command=back_to_home)
    back_button.pack(padx=10, pady=1)


def change_appearance(new_appearance_mode):
    global fig
    global ax
    customtkinter.set_appearance_mode(new_appearance_mode)
    for i in range(8):
        ax[i].axis('off')
        fig[i].set_facecolor(
            'white' if new_appearance_mode.lower() == 'light' else 'black')
        newfig[i].set_facecolor(
            'white' if app._get_appearance_mode() == 'light' else 'black')
        ax[i].set_facecolor(
            'white' if new_appearance_mode.lower() == 'light' else 'black')
        newax[i].set_facecolor(
            'white' if app._get_appearance_mode() == 'light' else 'black')
        canvases[i].draw()
        app.update_idletasks()


appearance = customtkinter.CTkOptionMenu(master=home_frame, values=[
                                         'Dark', 'Light', 'System'], command=change_appearance)
appearance.pack(side='right', padx=10, pady=10)


def draw_signal(signal, time, channelNumber):
    wave = np.array(signal)
    time_x = np.array(time)
    # time_x = np.array(t[0:SPP])
    freq_labels[channelNumber].configure(text=freq[channelNumber])
    duty_cycle_labels[channelNumber].configure(text=duty_cycle[channelNumber])
    ax[channelNumber].set_xlim(time_x.min() - 50, time_x.max() + 50)
    newax[channelNumber].set_xlim(time_x.min() - 50, time_x.max() + 50)
    line[channelNumber].set_ydata(wave)
    line[channelNumber].set_xdata(time_x)
    newline[channelNumber].set_ydata(wave)
    newline[channelNumber].set_xdata(time_x)
    canvases[channelNumber].draw()
    newcanvases[channelNumber].draw()
    app.update_idletasks()


thread = threading.Thread(target=Read_thread)
thread.start()

# Start the Tkinter event loop
app.mainloop()

Runnung_Flag = False
