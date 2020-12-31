import sys, os
import numpy as np
import pyzed.sl as sl
import cv2
from datetime import datetime
import csv

import PySimpleGUI as sg
from gui import ZED_GUI

def get_timestamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def save_rgb(subdir, img_rgb) :
    img_route = os.path.join(subdir, 'rgb.png')
    saved = (img_rgb.write(img_route) == sl.ERROR_CODE.SUCCESS)
    if saved :
        print("Imagen de RGB guardada en {}".format(img_route))
    else :
        print("Error al guardar la imagen RGB")

def save_depth(subdir, img_depth) :
    img_route = os.path.join(subdir, 'depth.png')
    saved = (img_depth.write(img_route) == sl.ERROR_CODE.SUCCESS)
    if saved :
        print("Imagen de profundida guardada en {}".format(img_route))
    else :
        print("Error al guardar la imagen de profundidad")

def save_pointcloud(subdir, point_cloud) :
    pc_route = os.path.join(subdir, 'pointcloud.ply')
    saved = (point_cloud.write(pc_route) == sl.ERROR_CODE.SUCCESS)
    if saved :
        print("Nube de puntos guardada correctamente en {}".format(pc_route))
    else :
        print("Falla al guardar la nube de puntos")

def get_data_from_sensors(sensors_data):
    quaternion = sensors_data.get_imu_data().get_pose().get_orientation().get()
    linear_acceleration = np.asarray(sensors_data.get_imu_data().get_linear_acceleration())
    angular_velocity = np.asarray(sensors_data.get_imu_data().get_angular_velocity())
    magnetic_field_calibrated = np.asarray(sensors_data.get_magnetometer_data().get_magnetic_field_calibrated())
    atmospheric_pressure = sensors_data.get_barometer_data().pressure

    return quaternion, linear_acceleration, angular_velocity, magnetic_field_calibrated, atmospheric_pressure

def save_sensors_data(subdir, sensors_data):
    fieldnames = ['IMU_orientation', 'IMU_acceleration', 'IMU_angular_velocity', 'Magnetometer_magnetic_field', 'Barometer_atmospheric_pressure']

    quaternion, linear_acceleration, angular_velocity, magnetic_field_calibrated, atmospheric_pressure =\
        get_data_from_sensors(sensors_data)

    print("IMU Orientation: {}".format(quaternion))
    print("IMU Acceleration: {} [m/sec^2]".format(linear_acceleration))
    print("IMU Angular Velocity: {} [deg/sec]".format(angular_velocity))
    print("Magnetometer Magnetic Field: {} [uT]".format(magnetic_field_calibrated))
    print("Barometer Atmospheric pressure: {} [hPa]".format(atmospheric_pressure))

    sd_route = os.path.join(subdir, 'sensors_data.csv')
    with open(sd_route, mode='w') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames, delimiter=',', quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()

        writer.writerow({'IMU_orientation': quaternion, 'IMU_acceleration': linear_acceleration, 'IMU_angular_velocity': angular_velocity,
                        'Magnetometer_magnetic_field': magnetic_field_calibrated, 'Barometer_atmospheric_pressure': atmospheric_pressure})

    print('Data de sensores guardada en {}'.format(sd_route))

def get_height():
    msg = 'Debe ingresar valor numérico. Decimales con punto.'

    try:
        height = float(input('Ingrese altura del objeto en cm: '))
        print("\t Altura ingresada: {}".format(height))
    except:
        print(msg)
        height = get_height()
    finally:
        return height

def get_width():
    msg = 'Debe ingresar valor numérico. Decimales con punto.'

    try:
        width = float(input('Ingrese ancho del objeto en cm: '))
        print("\t Ancho ingresado: {}".format(width))
    except:
        print(msg)
        width = get_width()
    finally:
        return width

def get_length():
    msg = 'Debe ingresar valor numérico. Decimales con punto.'

    try:
        length = float(input('Ingrese largo del objeto en cm: '))
        print("\t Largo ingresado: {}".format(length))
    except:
        print(msg)
        length = get_length()
    finally:
        return length

def save_dimensions_data(subdir, height, width, length):
    fieldnames = ['height', 'width', 'length']

    '''height = get_height()
    width = get_width()
    length = get_length()'''

    sd_route = os.path.join(subdir, 'dimensions.csv')
    with open(sd_route, mode='w') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames, delimiter=',', quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()

        writer.writerow({'height': height, 'width': width, 'length': length})

    print('Dimensiones del objeto guardadas en {}'.format(sd_route))

def capture_data(zed, height, width, length) :
    print('\n##################################################')
    print("#Capturando data, no mover la cámara ni el objeto#")
    print('##################################################')

    # capture RGB image
    tmp_img = sl.Mat()
    zed.retrieve_image(tmp_img, sl.VIEW.LEFT)

    # capture depth data
    tmp_depth = sl.Mat()
    zed.retrieve_measure(tmp_depth, sl.MEASURE.DEPTH)

    # capture pointcloud
    tmp_pointcloud = sl.Mat()
    zed.retrieve_measure(tmp_pointcloud, sl.MEASURE.XYZRGBA) 

    # capture sensors data
    tmp_sensors = sl.SensorsData()
    zed.get_sensors_data(tmp_sensors, sl.TIME_REFERENCE.IMAGE)

    # get timestamp
    ts = get_timestamp()

    # create subdir
    # subdir of current capture
    subdir = os.path.join('data', ts)
    os.makedirs(subdir, exist_ok=True)
    
    # Saving RGB image
    save_rgb(subdir, tmp_img)

    # saving depth image
    save_depth(subdir, tmp_depth)

    # saving pointcloud
    save_pointcloud(subdir, tmp_pointcloud)

    # saving sensors data
    save_sensors_data(subdir, tmp_sensors)

    # get and save dimensions
    save_dimensions_data(subdir, height, width, length)

    # done
    print('Listo para capturar siguiente objeto')

def print_help() :
    print(" Press 's' to save Side by side images")
    print(" Press 'p' to save Point Cloud")
    print(" Press 'd' to save Depth image")
    print(" Press 'm' to switch Point Cloud format")
    print(" Presiona 'n' para realizar una nueva captura")
    print(" Presiona 'q' para cerrar el programa")


def main() :
    # Create a ZED camera object
    zed = sl.Camera()

    # Set configuration parameters
    input_type = sl.InputType()
    init = sl.InitParameters(input_t=input_type)
    init.camera_resolution = sl.RESOLUTION.HD1080
    #init.camera_resolution = sl.RESOLUTION.HD720
    init.depth_mode = sl.DEPTH_MODE.PERFORMANCE
    init.coordinate_units = sl.UNIT.MILLIMETER
    #init.coordinate_units = sl.UNIT.METER

    # Open the camera
    err = zed.open(init)
    if err != sl.ERROR_CODE.SUCCESS :
        print(repr(err))
        zed.close()
        exit(1)

    # Display help in console
    print_help()

    # Creating GUI
    gui = ZED_GUI()

    # Set runtime parameters after opening the camera
    runtime = sl.RuntimeParameters()
    runtime.sensing_mode = sl.SENSING_MODE.STANDARD

    # Prepare new image size to retrieve half-resolution images
    image_size = zed.get_camera_information().camera_resolution
    image_size.width = image_size.width /2
    image_size.height = image_size.height /2

    # Declare your sl.Mat matrices
    image_zed = sl.Mat(image_size.width, image_size.height, sl.MAT_TYPE.U8_C4)
    depth_image_zed = sl.Mat(image_size.width, image_size.height, sl.MAT_TYPE.U8_C4)
    point_cloud = sl.Mat()

    sensors_data = sl.SensorsData()

    key = ' '
    event = ' '
    while key != 113:
        err = zed.grab(runtime)

        event, values = gui.window.read(timeout=20)
        if event == "Exit" or event == sg.WIN_CLOSED:
            break

        if event == "Capture":
            try:
                height = float(values["-HEIGHT-"])
                width  = float(values["-WIDTH-"])
                length = float(values["-LENGTH-"])

                sg.popup_timed('Capturando data, no mover la cámara ni el objeto', title='Capturando data', auto_close_duration=5, non_blocking=True)

                capture_data(zed, height, width, length)

                gui.window["-HEIGHT-"].update('')
                gui.window["-WIDTH-"].update('')
                gui.window["-LENGTH-"].update('')

                sg.popup_timed('Captura guardada correctamente. Listo para continuar', title='Captura exitosa', auto_close_duration=5)
            except:
                sg.popup_timed('Debe ingresar valor numérico en los tres campos. Decimales con punto.', title='Valores incorrectos', auto_close_duration=5)
                pass

        if err == sl.ERROR_CODE.SUCCESS :
            # Retrieve the left image, depth image in the half-resolution
            zed.retrieve_image(image_zed, sl.VIEW.LEFT, sl.MEM.CPU, image_size)
            zed.retrieve_image(depth_image_zed, sl.VIEW.DEPTH, sl.MEM.CPU, image_size)
            # capture sensors data
            zed.get_sensors_data(sensors_data, sl.TIME_REFERENCE.IMAGE)

            # To recover data from sl.Mat to use it with opencv, use the get_data() method
            # It returns a numpy array that can be used as a matrix with opencv
            image_ocv = image_zed.get_data()
            depth_image_ocv = depth_image_zed.get_data()

            # concatenate both images to show them side by side in the GUI
            sbs_image = np.concatenate((image_ocv, depth_image_ocv), axis=1)
            imgbytes = cv2.imencode(".png", sbs_image)[1].tobytes()
            gui.window["-IMAGE-"].update(data=imgbytes)

            # show sensors data
            quaternion, linear_acceleration, angular_velocity, magnetic_field_calibrated, atmospheric_pressure =\
                get_data_from_sensors(sensors_data)

            gui.window["-IMU_ORIENTATION-"].update(quaternion)
            gui.window["-IMU_ACCELERATION-"].update(linear_acceleration)
            gui.window["-IMU_ANG_VEL-"].update(angular_velocity)
            gui.window["-IMU_MAG_FIELD-"].update(magnetic_field_calibrated)
            gui.window["-IMU_ATM_PRESS-"].update(atmospheric_pressure)

            key = cv2.waitKey(10)

    cv2.destroyAllWindows()
    zed.close()
    gui.window.close()

    print("\nFINISH")

if __name__=='__main__':
    print('Iniciando script para captura de data desde cámara ZED 2')

    main()