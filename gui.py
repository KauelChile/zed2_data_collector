import PySimpleGUI as sg

import cv2

import numpy as np

class ZED_GUI:
    def __init__(self):

        sg.theme("LightGreen")

        # Define the window layout
        layout = [
            [sg.Image(filename="", key="-IMAGE-")],
            
            [sg.Text("IMU Orientation ", size=(60, 1), justification="left"), 
                sg.Text(size=(65, 1), key="-IMU_ORIENTATION-"),
                    sg.Text(" [deg]", size=(60, 1), justification="left")],

            [sg.Text("IMU Acceleration ", size=(60, 1), justification="left"), 
                sg.Text(size=(65, 1), key="-IMU_ACCELERATION-"),
                    sg.Text(" [m/sec^2]", size=(60, 1), justification="left")],

            [sg.Text("IMU Angular Velocity ", size=(60, 1), justification="left"), 
                sg.Text(size=(65, 1), key="-IMU_ANG_VEL-"),
                    sg.Text(" [deg/sec]", size=(60, 1), justification="left")],

            [sg.Text("Magnetometer Magnetic Field ", size=(60, 1), justification="left"), 
                sg.Text(size=(65, 1), key="-IMU_MAG_FIELD-"),
                    sg.Text(" [uT]", size=(60, 1), justification="left")],

            [sg.Text("Barometer Atmospheric Pressure", size=(60, 1), justification="left"), 
                sg.Text(size=(65, 1), key="-IMU_ATM_PRESS-"),
                    sg.Text(" [hPa]", size=(60, 1), justification="left")],

            
            [sg.Text("Ingreso de dimensiones (en cm)", size=(60, 1), justification="center")],
                
            [sg.Text("Alto", size=(60, 1), justification="left"), sg.InputText(key='-HEIGHT-'),\
                sg.Text(" [cm]", size=(60, 1), justification="left")],
            [sg.Text("Ancho", size=(60, 1), justification="left"), sg.InputText(key='-WIDTH-'),\
                sg.Text(" [cm]", size=(60, 1), justification="left")],
            [sg.Text("Largo", size=(60, 1), justification="left"), sg.InputText(key='-LENGTH-'),\
                sg.Text(" [cm]", size=(60, 1), justification="left")],

            [sg.Submit(button_text="Capturar", key="Capture")],
            [sg.Button("Cerrar", size=(10, 1), key="Exit")],

        ]
        # Create the window and show it without the plot
        self.window = sg.Window("Captura de objetos con ZED 2", layout, location=(0, 0))
        
if __name__ == "__main__":
    gui = ZED_GUI()

    cap = cv2.VideoCapture(0)

    while True:

        event, values = gui.window.read(timeout=20)

        if event == "Exit" or event == sg.WIN_CLOSED:

            break

        ret, frame = cap.read()

        imgbytes = cv2.imencode(".png", frame)[1].tobytes()

        gui.window["-IMAGE-"].update(data=imgbytes)

    gui.window.close()
