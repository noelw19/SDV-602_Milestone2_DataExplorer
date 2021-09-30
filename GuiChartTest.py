import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import PySimpleGUI as sg
import matplotlib
import matplotlib.dates as mdates
import datetime as dt
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import os.path as Path
from DES_View import View as DES
# from NewWindow import open_window as O_Window

message=''
def receive():
    """Handles receiving of messages."""
    while True:
        try:
            global msg_list
            msg_list = []
            msg = client_socket.recv(BUFSIZ).decode("utf8")
            msg_list.append(msg)
            window['msg'].update(msg_list)
        except OSError:  # Possibly client has left the chat.
            break


def send(event=None):  # event is passed by binders.
    """Handles sending of messages."""
    msg = message
    client_socket.send(bytes(msg, "utf8"))
    if msg == "{end}":
        client_socket.close()
        window.close()


def on_closing(event=None):
    """This function is to be called when the window is closed."""
    message = "{end}"
    send()

fig = matplotlib.figure.Figure(figsize=(3, 2), dpi=100)
ax = fig.add_axes([1, 4, 15, 50], projection=None, polar=False)

x = np.array([0, 1, 2, 3])
y = np.array([3, 8, 1, 10])

# changing the subplot values affects size of the graph not values
fig.add_subplot(1, 1, 1).plot(x,y)
# fig.add_axis(min(x), min(y), max(x), max(y))

sg.theme('Dark Blue 3')  # please make your windows colorful
# login credentials for testing purposes
user = 'Noel'
password = '1234'
# scene Variable to indicate where the program is in its lifecycle
current = 'login'

def des(screen=0):

    login = DES().login(sg)
    screen1 = DES().layout('DES Screen 1', sg)
    screen2 = DES().layout('DES Screen 2', sg)
    screen3 = DES().layout('DES Screen 3', sg)

    if screen == 1:
        return screen1
    if screen == 2:
        return screen2
    if screen == 3:
        return screen3
    return login

# Define the initial window layout
layout = des()

def returnCoordinates(fig, xVals, yVals):
    valsX = np.array(xVals)
    valsY = np.array(yVals)
    fig.add_subplot(1, 1, 1).plot(valsX, valsY)

def event_checker(w):
    # if event == '#1' for button click and loginEvent for if user logs out and logs back in
    # since the des1 button is not pushed on login
    if event == '#1' or event == 'loginEvent':

        client_socket.connect(ADDR)
        receive_thread = Thread(target=receive)
        receive_thread.start()
        print('Rendering: Screen1')
        w['msg'].update(msg_list)

    elif event == '#2':

        client_socket.connect(ADDR)
        receive_thread = Thread(target=receive)
        receive_thread.start()
        print('Rendering: Screen2')
        w['msg'].update(msg_list)

    elif event == '#3':

        client_socket.connect(ADDR)
        receive_thread = Thread(target=receive)
        receive_thread.start()
        print('Rendering: Screen3')
        w['msg'].update(msg_list)

matplotlib.use("TkAgg")

def draw_figure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side="top", fill="both", expand=1)
    return figure_canvas_agg


def des_render(prevWindow, num, csv= None):
    prevWindow.close()
    # VARIABLE equals a new layout that corresponds to function num value
    layout_instance = des(num)
    # new global window obj 
    global window
    # window equals a new PySimpleGUI.Window(screen name, layout, other methods)
    window = sg.Window('Data exploration Screen #' + str(num), layout_instance, size=(700, 500), finalize=True)
    # added draw figure for the graph to render properly
    if num == 1:
        newFig = matplotlib.figure.Figure(figsize=(3, 2), dpi=100)
        if csv == None:
            returnCoordinates(newFig, [3, 2, 1, 0], [9, 5, 8, 1])
        else:
            returnCoordinates(newFig, csv[0], csv[1])
        draw_figure(window["-CANVAS-"].TKCanvas, newFig)
    if num == 2:
        newFig = matplotlib.figure.Figure(figsize=(3, 2), dpi=100)
        returnCoordinates(newFig, [1, 3, 2, 4], [7, 3, 6, 7])
        draw_figure(window["-CANVAS-"].TKCanvas, newFig)
    if num == 3:
        newFig = matplotlib.figure.Figure(figsize=(3, 2), dpi=100)
        returnCoordinates(newFig, [1, 4, 6, 8], [9, 7, 3, 2])
        draw_figure(window["-CANVAS-"].TKCanvas, newFig)
    # returns the event checker function with window as the first arguement
    event_checker(window)

# first window instance
window = sg.Window('Simple data entry window', layout, size=(700, 500))

# ----Now comes the sockets part----
# HOST = input('Enter host: ')
# PORT = input('Enter port: ')

# when page change port will be changed to reflect different rooms per screen so
# users can talk to other people within the same room.
HOST = '127.0.0.1'
PORT = 33000

BUFSIZ = 1024
ADDR = (HOST, PORT)
client_socket = socket(AF_INET, SOCK_STREAM)

def structureCsvData(data):
    rows = []
    list1 = [list(row) for row in f.values]
    newRows = []
    count = 0
        # newRows.append(datum)
    
    # print(rows)
    for d in data.columns:
        newRows.append(d)
        for dataList in list1:
            newRows.append(dataList[count])
        count += 1
        rows.append(newRows)
        newRows = []
    # print(rows)
    return rows
        
        


while True:
    # Event Loop
    event, values = window.read()
    print(event, values)
    if event == sg.WIN_CLOSED or event == 'Exit':
        on_closing()
        break
    # IF send message button is pressed
    if event == 'Send':
        global my_msg
        my_msg = values['choice']
        message = my_msg
        send()
        print(my_msg)
    # LOGIN PAGE 
    if current == 'login' or event == 'loginEvent':
        # if the username and password entered match local data
        if values['-USER-'] == user and values['-PASSWORD-'] == password:
            # print logged in and change current scene to des1
            print('User logged in')
            current = des_render(window, 1)
    
    if event == 'logout':
        # if it is a logout event we close the current window by passing it as an arg
        window.close()
        # Close current socket communication so it reopens comms if user login in with same window
        client_socket.close()
        # new socket instance incase of re login with same window
        client_socket = socket(AF_INET, SOCK_STREAM)
        # login_screen becomes a layout list by calling the des func which returns a login list layout if no args or 0 is input
        login_screen = des()
        # open new window, with new layout
        window = sg.Window('New', login_screen, size=(700, 500))
        print('User is logged out.')
        # return 'login'

    if event == '#1':
        # closing socket then creating new instance of client socket for new
        # communications, error is received wwhen new instance is not created,
        # because closed comms cannot be reopened with socket.
        client_socket.close()
        client_socket = socket(AF_INET, SOCK_STREAM)
        current = des_render(window, 1)
    if event == '#2':
        client_socket.close()
        client_socket = socket(AF_INET, SOCK_STREAM)
        current = des_render(window, 2)
    if event == '#3':
        client_socket.close()
        client_socket = socket(AF_INET, SOCK_STREAM)
        current = des_render(window, 3)
    # Conditional for when upload button i pressed
    if event == 'uploadBtn':
        filename = values['upload']
        print(filename)
        if Path.isfile(filename):
            try:
                value = []
                f = pd.read_csv(filename, delimiter=',')
                val = f
                listData = structureCsvData(val)
                XandY = [listData[0], listData[1]]
                print(XandY)
                # dateObj = datetime.strptime(vChild[0], "%Y-%m-%d")
                # values.append(dateObj)
                uploadWindow  = des_render(window,1 , XandY)
            except Exception as e:
                print("Error: ", e)


window.close()

