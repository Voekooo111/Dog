from robot_pca import Robot_pca
import time


def main():
    dog = Robot_pca()
    dog.name_body()
    dog.class_start(skip_calibration=False)

    dog.servo_run_name('r_forward_low', -200)
    dog.servo_run_name('l_back_low', -200)

    time.sleep(1)

    for value in range(0, 200, 5):
            dog.servo_run_name('l_forward_low', value)
            dog.servo_run_name('r_back_low', value)
            time.sleep(0.05)
    

    for value in range(0, 200, 5):
        dog.servo_run_name('r_forward_middle', value)
        dog.servo_run_name('l_back_middle', value)
        time.sleep(0.05)

    dog.servo_run_name('l_forward_middle', -200)
    dog.servo_run_name('r_back_middle', -200)
    
    


if __name__ == '__main__':
    main()