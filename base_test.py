from src.stacking_setup.components.stacking_backend.hardware.main_xy_controller import MainXYController
from src.stacking_setup.components.stacking_backend.hardware.base_stepper import BaseStepper
from src.stacking_setup.components.stacking_backend.configs.settings import Settings
import multiprocessing as mp
from time import sleep


if __name__ == '__main__':
    settings = Settings()
    em_event = mp.Event()
    controller = MainXYController(settings, em_event)
    stepper = BaseStepper(settings=settings, controller=controller, id='H', em_event=em_event)
    stepper.connect()

    # Do some tests
    print('Is connected: {}'.format(stepper.is_connected()))
    stepper.home()
    stepper.start_jog(direction='-')
    # controller.start_jog('y', velocity=400)
    sleep(0.5)
    stepper.stop_jog()
    print('Moving')
    stepper.move_to(20000, convert=False)
    print('X position {}'.format(stepper.position))
    stepper.move_by(5000, convert=False)
    stepper.move_to(20000, convert=False)
    print('X position {}'.format(stepper.position))
    stepper.move_by(5000, convert=False)
    stepper.home()
    # print('Current temp is {}'.format(controller.temperature))
    # print('old target temp is {}'.format(controller.target_temperature))
    # controller.target_temperature = 65
    # print('Current target temp is {}'.format(controller.target_temperature))
    # sleep(10)
    # print('Current temp is {}'.format(controller.temperature))
    # controller.target_temperature = 20

    controller.disconnect()
    
