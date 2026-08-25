import lgpio
import time

class Pca:
    """
    Класс подключается по i2c шине к PCA9685. И управляет серво, подключенными к PCA.
    
    Args:
        pin_bus_address: (int, hex) - шина и адрес i2c
        freq - частота подключенных устройств
    """
    def __init__(self, pin_bus_address: tuple = (1, 0x40), freq: int = 50):
        self.pin_bus_address = pin_bus_address
        self.freq = freq
        self.i2c_handle = None
        self.connect()
        self.setting()

    
    def connect(self):
        """Подключение к pca."""
        self.i2c_handle = lgpio.i2c_open(*self.pin_bus_address)
    
    def setting(self):
        """Настройка"""
        Mode1 = lgpio.i2c_read_byte_data(self.i2c_handle, 0x00)
        lgpio.i2c_write_byte_data(self.i2c_handle, 0x00, Mode1 | 0x10)
        pre_scale = int(round(25_000_000 / (4096 * self.freq)) - 1)
        lgpio.i2c_write_byte_data(self.i2c_handle, 0xFE, pre_scale)
        lgpio.i2c_write_byte_data(self.i2c_handle, 0x00, (Mode1 & ~0x10) | 0x20)
        time.sleep(0.001)
        Mode2 = lgpio.i2c_read_byte_data(self.i2c_handle, 0x01)
        lgpio.i2c_write_byte_data(self.i2c_handle, 0x01, (Mode2 & ~0x03) | 0x01)

    def servo_stop(self, channel: int):
        """
        Остановка серво.
        
        Args:
            channel - канал устройства
        """
        lgpio.i2c_write_byte_data(self.i2c_handle, 0x07 + 4 * channel, 0x00)
        lgpio.i2c_write_byte_data(self.i2c_handle, 0x09 + 4 * channel, 0x10)
    
    def servo_run(self, channel: int, pulse: int):
        """
        Запуск серво.
        
        Args:
            channel - канал устройства
            pulse - мкс угла серво.
        """
        pulse = max(500, min(pulse, 2500))
        r_time = round(pulse * self.freq * 4096 / 1_000_000)
        off_low = r_time & 0b11111111
        off_high = (r_time >> 8) & 0x0F
        start_reg = 0x06 + 4 * channel
        lgpio.i2c_write_byte_data(self.i2c_handle, start_reg, 0)
        lgpio.i2c_write_byte_data(self.i2c_handle, start_reg+1, 0)
        lgpio.i2c_write_byte_data(self.i2c_handle, start_reg+2, off_low)
        lgpio.i2c_write_byte_data(self.i2c_handle, start_reg+3, off_high)
    
    def close(self):
        """
        Закрывает I2C соединение.
        """
        if self.i2c_handle is not None:
            lgpio.i2c_close(self.i2c_handle)
            self.i2c_handle = None

    
if __name__ == "__main__":
    pca = Pca()
    print("pca подключен")
    pca.servo_run(0, 1500)
    