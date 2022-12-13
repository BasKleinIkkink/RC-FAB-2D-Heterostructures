from src.stacking_setup.stacking_backend.hardware.main_xy_controller import MainXYController
from src.stacking_setup.stacking_backend.configs.settings import Settings
import multiprocessing as mp
from time import sleep


if __name__ == '__main__':
    settings = Settings()
    em_event = mp.Event()
    controller = MainXYController(settings, em_event)
    controller.connect()

    # Do some tests
    print('Is connected: {}'.format(controller.is_connected()))

    controller.vacuum_on()
    sleep(2)
    controller.vacuum_off()
    controller.zero()
    controller.start_jog('x', velocity=10)
    controller.start_jog('y', velocity=10)
    #print('Moving')
    #controller.move_to('X', 5000)
    #print('X position {}'.format(controller.get_position(axis='x')))
    #controller.move_by('X', 5000)
    #controller.move_to('Y', 5000)
    #print('Y position {}'.format(controller.get_position(axis='y')))
    #controller.move_by('Y', 5000)
    #controller.home()
    #print('Current temp is {}'.format(controller.temperature))
    #print('old target temp is {}'.format(controller.target_temperature))
    #controller.target_temperature = 65
    #print('Current target temp is {}'.format(controller.target_temperature))
    #sleep(10)
    #print('Current temp is {}'.format(controller.temperature))
    #controller.target_temperature = 20

    controller.disconnect()
    
