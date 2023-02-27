import esp32
from machine import deepsleep, Pin, ADC
import time
from ir_tx.nec import NEC


class ButtonController:
    def __init__(self, ir_controller):
        self.ir_controller = ir_controller
        self.init_pins()

    def init_pins(self):
        input_b = Pin(12, Pin.IN, Pin.PULL_UP)
        up = Pin(15, Pin.IN, Pin.PULL_UP)
        down = Pin(32, Pin.IN, Pin.PULL_UP)
        left = Pin(27, Pin.IN, Pin.PULL_UP)
        right = Pin(33, Pin.IN, Pin.PULL_UP)
        ok = Pin(14, Pin.IN, Pin.PULL_UP)
        esp32.wake_on_ext0(pin = input_b, level = esp32.WAKEUP_ALL_LOW)
        # esp32.wake_on_ext1(pins = (input_b, up), level = esp32.WAKEUP_ALL_LOW)
        # esp32.wake_on_ext1(pins = (input_b,) up, down, left, right, ok), level = esp32.WAKEUP_ALL_LOW)
        self.mapping = [
            (input_b, self.ir_controller.send_input),
            (up,      self.ir_controller.send_left),
            (down,    self.ir_controller.send_right),
            (left,    self.ir_controller.send_up),
            (right,   self.ir_controller.send_down),
            (ok,      self.ir_controller.send_ok)
            ]

    def check_for_press(self):
        time.sleep(0.1)
        for button in self.mapping:
            if button[0].value() == 0:
                time.sleep(0.05)
                if button[0].value() == 0:
                    button[1]()
                    return True


class IRController:
    def __init__(self):
        self.codes = {
            'IN': (0xbf00, 0x12),
            'UP': (0xbf00, 0x16),
            'DN': (0xbf00, 0x17),
            'LE': (0xbf00, 0x19),
            'RI': (0xbf00, 0x18),
            'OK': (0xbf00, 0x15)
        }
        self.nec = NEC(Pin(23, Pin.OUT, value = 0))
    def send_input(self):
        self.nec.transmit(self.codes['IN'][0], self.codes['IN'][1])
        print("IN")
    def send_left(self):
        self.nec.transmit(self.codes['LE'][0], self.codes['LE'][1])
        print("LE")
    def send_right(self):
        self.nec.transmit(self.codes['RI'][0], self.codes['RI'][1])
        print("RI")
    def send_up(self):
        self.nec.transmit(self.codes['UP'][0], self.codes['UP'][1])
        print("UP")
    def send_down(self):
        self.nec.transmit(self.codes['DN'][0], self.codes['DN'][1])
        print("DN")
    def send_ok(self):
        self.nec.transmit(self.codes['OK'][0], self.codes['OK'][1])
        print("OK")


class BatteryMonitor:
    def __init__(self):
        self.bat_pin = ADC(Pin(35))
        self.bat_pin.width(ADC.WIDTH_12BIT)
        self.bat_pin.atten(ADC.ATTN_11DB)

    def get_voltage(self):
        value_12b = self.bat_pin.read()
        value_v = value_12b / 4095 * 2 * 3.3 * 1.1
        return value_v

print("Boot")
monitor = BatteryMonitor()
print("Monitor init")
ir_ctrl = IRController()
print("IR init")
main = ButtonController(ir_ctrl)
print("CTRL init")
print("mainloop")
init_time = time.time()
awake = True
while awake:
    did_press = main.check_for_press()
    if did_press:
        init_time = time.time()
        print(f"did_press, init time: {init_time}")
        print(f"Bat voltage: {monitor.get_voltage()}V")
    else:
        if time.time() > init_time + 5:
            print("going to sleep...")
            deepsleep()

# Pinout:
# 12: IN
# 27: UP
# 33: DN
# 15: L
# 32: R
# 14: OK
