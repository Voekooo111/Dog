from robot_pca import Robot_pca


def main():
    dog = Robot_pca()
    dog.name_body()
    dog.class_start(skip_calibration=False)

    # хождение

    dog.servo_run_name('r_forward_middle', )

if __name__ == '__main__':
    main()