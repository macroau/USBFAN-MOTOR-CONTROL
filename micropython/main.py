import utime
import gc
from machine import Pin, PWM, ADC
from micropython import const


# 设定
# 电位器可调速度范围
SPEED_MIN = const(18000)
SPEED_MAX = const(65535)
# 扫风最小速度
SWEEP_MIN = const(10000)
SWEEP_MAX_LOW_LIMIT = const(25000)
# 扫风led闪频
LED_FREQ_SWEEP = const(10)
# 固定速度led闪频
LED_FREQ_NORMAL = const(60)
# 扫风步进
SWEEP_STEP = const(100)
# 扫风步进间隔时间
SWEEP_STEP_INV = const(20)


# 按键定义
sel_key = Pin(15, Pin.IN, Pin.PULL_UP)
# 电位器定义
pot_adc = ADC(28)

# pwm控制输出定义
pwm_mos  = PWM(Pin(22))
# led指示灯定义
led  = PWM(Pin(25))

# led显示频率
led.freq(10)

# 设定pwm控制mos的频率： 50 kHz
pwm_mos.freq(50000)

# 给0.5秒全输出以启动电机
pwm_mos.duty_u16(65535)
utime.sleep(0.5)


# 将电位器AD值转换为占空比
def transform(n, from_min=500, from_max=65000, to_min=SPEED_MIN, to_max=SPEED_MAX):
    if n<from_min:
        return to_min
    
    if n>from_max:
        return to_max
    
    return int((n - from_min) / (from_max - from_min) * (to_max - to_min) + to_min - 1)
    

def led_pwm_duty(n):
    n = int(((d-SWEEP_MIN) / (SPEED_MAX-SWEEP_MIN)) **3 * 30000) + 1000

    return n


sweep_flag = False
led.freq(LED_FREQ_NORMAL)

d = 1       # 当前的duty
s = SWEEP_STEP

while True:     # Main Loop
    
    pot_speed_ad = pot_adc.read_u16()
    pot_speed = transform(pot_speed_ad)
    #print(pot_speed)

    if sel_key.value()==0:
    
        utime.sleep_ms(30)
        if sel_key.value()==0:
            if sweep_flag:
                sweep_flag = False
                led.freq(LED_FREQ_NORMAL)
            else:
                sweep_flag = True
                led.freq(LED_FREQ_SWEEP)    

            while sel_key.value()==0:
                led.duty_u16(0)
                utime.sleep_ms(5)

    if sweep_flag:
        d = d + s

        if d < SWEEP_MIN:
            d = SWEEP_MIN
            s = SWEEP_STEP
            utime.sleep(1)
        if pot_speed < SWEEP_MAX_LOW_LIMIT:
            pot_speed = SWEEP_MAX_LOW_LIMIT
        if d > pot_speed:
            d = pot_speed
            s = -SWEEP_STEP
            utime.sleep(0.2)
         
    else:
        d = pot_speed

    pwm_mos.duty_u16(d)  
    led.duty_u16(led_pwm_duty(d))
    
    gc.collect()
    utime.sleep_ms(SWEEP_STEP_INV)


