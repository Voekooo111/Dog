from pca9685 import Pca
import csv
import lgpio
import time
import pickle

class Robot_pca(Pca):
    """
    Робот на PCA9685.
    Класс подключается по i2c шине к PCA9685. И управляет серво, подключенными к PCA.
    
    Args:
        pin_bus_address: (int, hex) - шина и адрес i2c
        freq - частота подключенных устройств
    """
    def __init__(self, count_servo: int = 12, pin_bus_address: tuple = (1, 0x40), freq: int = 50, ):
        super().__init__(pin_bus_address, freq)
        self.channal_to_body: dict[int, str] = {}
        self.body: dict[str, int | None] = {}
        self.count_servo = count_servo
        self.centers = [1500] * count_servo
        self.flag_success_run = False
        self.flag_success_stop = False
        self.pwm = [None] * self.count_servo

    def name_body(self, *args):
        """
        Класс для названий частей тела.
        
        Args:
            args - названия тел (Если пустой, используется по умолчанию)
        """
        if args is None:
            self.body = {
                "r_forward_low": None,
                "r_forward_middle" : None,
                "r_forward_high" : None,
                "l_forward_low": None,
                "l_forward_middle" : None,
                "l_forward_high" : None,
                "r_back_low": None,
                "r_back_middle" : None,
                "r_back_high" : None,
                "l_back_low": None,
                "l_back_middle" : None,
                "l_back_high" : None,
            }
            return

        if len(args) != self.count_servo:
            raise ValueError(f"Количество элементов в count_servo ({self.count_servo}) не совпадает с количеством элементов в переменной ({len(args)}).")

        for b_n in args:
            self.body = dict(zip(args, [None] * self.count_servo))
        
    
    def servo_side(self, channal: int):
        """
        По каналу возвращает положение стороны (1, -1).
        ВНИМАНИЕ!!! РАБОТАЕТ ТОЛЬКО ДЛЯ НАЗВАНИЙ ПО УМОЛЧАНИЮ.
        """
        mapping: dict[str, int] = {
            "r_forward_low": 1,
            "r_forward_middle" : 1,
            "r_forward_high" : 1,
            "l_forward_low": 1,
            "l_forward_middle" : 1,
            "l_forward_high" : 1,
            "r_back_low": 1,
            "r_back_middle" : 1,
            "r_back_high" : 1,
            "l_back_low": 1,
            "l_back_middle" : 1,
            "l_back_high" : 1,
        }
        return mapping.get(self.channal_to_body.get(channal))
    
    def class_start(self, skip_calibration : bool = True):
        """Преднастройка класса."""
        self.define_servo()
        self.calibrate(skip_calibration)

    def update(self):
        """Обновление channal_to_body"""
        self.channal_to_body = {value: key for key, value in self.body.items()}

    def define_servo(self):
        """Определение сервопривода."""
        try:
            with open('define.pkl', mode='rb') as file:
                self.body = pickle.load(file)
            self.update()

        except FileNotFoundError:
            for i in range(self.count_servo):
                self.servo_run(i, 1800)
                time.sleep(0.6)
                self.servo_run(i, 1600)
                time.sleep(0.6)
                self.servo_run(i, 1400)
                time.sleep(0.6)
                self.servo_run(i, 1300)
                time.sleep(0.6)
                self.servo_run(i, 1400)
                time.sleep(0.6)
                self.servo_run(i, 1500)
                time.sleep(0.6)
                self.servo_stop(i)
                flag_input = True
                while flag_input:
                    inp = input("Какая часть робота?  ")
                    if inp in self.body.keys():
                        flag_input = False
                        self.body[inp] = i
                    else:
                        print("Попробуйте снова.")
            with open('define.pkl', mode='wb') as file:
                pickle.dump(self.body, file)
            self.update()

    
    def calibrate(self, skip_calibration=True):
        """
        Калибровка серво.
        
        Args:
            skip_calibration (по умолчанию True) при True - только считывает данные с файла.
        """
        try:
            with open('calibration.csv', mode='r') as file:
                self.centers = list(int(x) for x in list(csv.reader(file))[0])
            if len(self.centers) != self.count_servo: 
                raise FileNotFoundError
            print(self.centers)

        except FileNotFoundError:
            if not skip_calibration:
                for i in range(self.count_servo):
                    self.servo_run(list(self.body.values())[i], 1500)
                    time.sleep(0.2)

                print("Для сохранения значения напишите -1")
                for i in range(self.count_servo):
                    value = input(f"Середина сервопривода(мс) {list(self.body.keys())[i]}: ")
                    while value != '-1':
                        try:
                            value = int(value)
                            self.servo_run(list(self.body.values())[i], value)
                            self.centers[i] = value
                            value = input(f"Середина сервопривода(мс) {list(self.body.keys())[i]}: ")
                        except (ValueError, TypeError):
                            print('Введите число')
                            
                for i in range(self.count_servo):
                    self.servo_stop(list(self.body.values())[i])
                    time.sleep(0.2)

            with open('calibration.csv', mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(self.centers)


    def stop_all(self):
        """Выключить все сервоприводы."""
        for i in range(self.count_servo):
            self.servo_stop(i)
            time.sleep(0.2)


    def full(self):
        """Робот запускает все сервоприводы."""
        for i in range(self.count_servo):
            self.servo_run(i, self.centers[i])     
            time.sleep(0.2)

    def servo_run(self, channel, pulse):
        """
        Запуск сервопривода по каналу.
        """
        super().servo_run(channel, pulse)
        self.pwm[channel] = pulse

    def servo_stop(self, channel):
        """
        Остановка сервопривода по каналу
        """
        super().servo_stop(channel)
        self.pwm[channel] = None
    
    def servo_run_name(self, name: str, value: int):
        """
        Запуск сервопривода по названию.
        
        Args:
            name - название сервопривода.
            value - значение, на которое надо переместить сервопривод.
        """
        self.flag_success_run = True
        if name in self.body:
            body_num = self.body[name]
            body_num = (body_num, )
        else:
            self.flag_success_run = False
        for b_n in body_num:
            pulse = self.centers[b_n] + value * self.servo_side(b_n)
            self.servo_run(b_n, pulse)

    def servo_stop_name(self, name: str):
        """
        Выключение сервопривода по названию.
        
        Args:
            name - название сервопривода.
        """
        self.flag_success_stop = True
        if name in self.body:
            body_num = self.body[name]
            body_num = (body_num, )
        elif name in self.bodypart:
            body_num = self.bodypart[name]
        else:
            self.flag_success_stop = False
        for b_n in body_num:
            self.servo_stop(b_n)
