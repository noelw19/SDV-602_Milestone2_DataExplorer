import PySimpleGUI as sg

def open_window(name, lay, size):
    layout = [[sg.Text("New Window", key="new"), lay]]
    window = sg.Window(name, layout, size, modal=True)
    return run(window, lay)
   

def run(window, data):
    choice = None
    while True:
        event, values = window.read()
        if event == "Exit" or event == sg.WIN_CLOSED:
            break
        
    window.close()