from lakeshore import Model372, generic_instrument, Model372HeaterResistance, Model372HeaterOutputUnits
from lakeshore import Model372SampleHeaterOutputRange as sampleRange
import time
import traceback

LAKESHORE_WARMUP_MAX_VOLTAGE = 23
SAMPLE_HEATER_OUTPUT_RANGE = {
    0 : sampleRange.OFF,
    31.6 * 10 ** (-6) : sampleRange.RANGE_31_POINT_6_MICRO_AMPS,
    100 * 10 ** (-6) : sampleRange.RANGE_100_MICRO_AMPS,
    316 * 10 ** (-6) : sampleRange.RANGE_316_MICRO_AMPS,
    1 * 10 ** (-3) : sampleRange.RANGE_1_MILLI_AMP,
    3.16 * 10 ** (-3) : sampleRange.RANGE_3_POINT_16_MILLI_AMPS,
    10 * 10 ** (-3) : sampleRange.RANGE_10_MILLI_AMPS,
    31.6 * 10 ** (-3) : sampleRange.RANGE_31_POINT_6_MILLI_AMPS,
    100 * 10 ** (-3) : sampleRange.RANGE_100_MILLI_AMPS

    }


class lakeShoreCom:
    def __init__(self):
        self.updateTimer = time.perf_counter()
        self.updateTime = 3
        self.sensors = {}
        self.currentTemp = []
        self.currentRes = []
        self.ls = None
        self.isInit = False

        self.warmupHeaterInit = False
        self.warmupHeaterMaxCurrent = 0
        self.warmupHeaterSetCurrent = 0
        self.warmupHeaterSetPercent = 0
        self.warmupHeaterOn = False

        self.sampleHeaterInit = False
        self.sampleHeaterSetCurrent = 0
        self.sampleHeaterSetRange = SAMPLE_HEATER_OUTPUT_RANGE[0]
        self.sampleHeaterSetPercent = 0

        self.stillHeaterSetPercent = 0
        self.stillHeaterOn = False


    def pullValues(self):
        if self.ls == None:
            return False
        self.currentTemp = [self.ls.get_kelvin_reading(ii) for ii in self.sensors.values()]
        self.currentRes = [self.ls.get_resistance_reading(ii) for ii in self.sensors.values()]
        return True

    def update(self):
        if self.ls == None:
            try:
                self.ls = Model372(57600)
                self.isInit = True
            except generic_instrument.InstrumentException:
                return False

        if time.perf_counter() - self.updateTimer >= self.updateTime:
            self.updateTimer = time.perf_counter()
            self.currentTemp = [self.ls.get_kelvin_reading(ii) for ii in self.sensors.values()]
            self.currentRes = [self.ls.get_resistance_reading(ii) for ii in self.sensors.values()]
            return True
        return False

    def setupWarmupHeater(self, resistance : float, max_power : float, max_voltage = None):
        try:
            if max_voltage == None or\
                max_voltage > LAKESHORE_WARMUP_MAX_VOLTAGE:
                max_voltage = LAKESHORE_WARMUP_MAX_VOLTAGE

            power_limitted_current = (max_power/resistance)**(1/2)
            voltage_limitted_current = (max_voltage/resistance)

            max_current = max(power_limitted_current, voltage_limitted_current)
            resistance = Model372HeaterResistance.HEATER_25_OHM if resistance < 50 else Model372HeaterResistance.HEATER_50_OHM
            self.ls.setup_warmup_heater(resistance, max_current, Model372HeaterOutputUnits.CURRENT)
            self.warmupHeaterMaxCurrent = max_current
            self.warmupHeaterInit = True
            return True
        except (TypeError, generic_instrument.InstrumentException):            
            print(traceback.format_exc())

        self.warmupHeaterInit = False
        return False

    def setupSampleHeater(self, resistance : float):
        if resistance <= 2000:
            try:
                self.ls.setup_sample_heater(resistance, Model372HeaterOutputUnits.POWER)
                self.sampleHeaterInit = True
            except (TypeError, generic_instrument.InstrumentException):
                print(traceback.format_exc())
        self.sampleHeaterInit = False
        return False

    
    def setSampleHeaterOutputCurrent(self, current : float):
        if not self.sampleHeaterInit: return False
        current = min(current, list(SAMPLE_HEATER_OUTPUT_RANGE.keys())[-1])
        for rangeLimit in SAMPLE_HEATER_OUTPUT_RANGE:
            if current <= rangeLimit:
                break
        percent = current / rangeLimit * 100
        try:
            self.ls.set_heater_output_range(0, SAMPLE_HEATER_OUTPUT_RANGE[rangeLimit])
            self.ls.set_manual_output(0, percent)
        except (generic_instrument.InstrumentException):
            print(traceback.format_exc())
            return False
        self.sampleHeaterSetCurrent = current
        self.sampleHeaterSetRange = SAMPLE_HEATER_OUTPUT_RANGE[rangeLimit]
        self.sampleHeaterSetPercent = percent
        return True

    def setWarmupHeaterOutputCurrent(self, current : float):
        if not self.warmupHeaterInit: return False
        current = min(current, self.warmupHeaterMaxCurrent)
        percent = current / self.warmupHeaterMaxCurrent * 100
        try:
            self.ls.set_manual_output(1, percent)
            self.ls.set_heater_output_range(1, True)
        except (generic_instrument.InstrumentException):
            print(traceback.format_exc())
            return False
        self.warmupHeaterSetCurrent = current
        self.warmupHeaterSetPercent = percent
        self.warmupHeaterOn = True
        return True

    def setStillOutput(self, power : float):
        if power > 100: power = 100
        if power < 0 : power = 0
        try:
            self.ls.set_still_output(power)
            self.ls.set_heater_output_range(2, True)
        except (generic_instrument.InstrumentException):
            print(traceback.format_exc())
            return False
        self.stillHeaterSetPercent = power
        self.stillHeaterOn = True

        return True

    def stopWarmupHeater(self):
        try:
            self.ls.set_heater_output_range(1, False)
        except (generic_instrument.InstrumentException):
            print(traceback.format_exc())
            return False
        self.warmupHeaterOn = False
        return True
    def stopStillHeater(self):
        try:
            self.ls.set_heater_output_range(2, False)
        except (generic_instrument.InstrumentException):
            print(traceback.format_exc())
            return False
        self.stillHeaterOn = False
        return True
    def stopSampleHeater(self):
        try:
            self.ls.set_heater_output_range(0, sampleRange.OFF)
        except (generic_instrument.InstrumentException):
            print(traceback.format_exc())
            return False
        self.sampleHeaterSetRange = sampleRange.OFF
        return True

        







        
        
        


        

        


_lakeshore_com = lakeShoreCom()

def init(sensors : dict, warmupHeaterResistance = None, sampleHeaterSettings = None):
    try:
        _lakeshore_com.ls = Model372(57600)
    except generic_instrument.InstrumentException:
        _lakeshore_com.ls = None
        return False
    _lakeshore_com.sensors = sensors
    _lakeshore_com.currentTemp = [0] * len(sensors)
    _lakeshore_com.currentRes = [0] * len(sensors)
    _lakeshore_com.isInit = True

    if warmupHeaterResistance != None:
        _lakeshore_com.setup_warmup_heater(warmupHeaterResistance,
            )


    return True

def check_temperatures():

    # Success if the temperatures were successfully read.
    # Returns the current temperatures of all thermometers.
    return (_lakeshore_com.pullValues(), _lakeshore_com.currentTemp)

def check_temperature(p = None):
    if p == None:

        # Success if the temperatures were successfully read.
        # Returns the current temperatures of all thermometers.
        return check_temperatures()
    
    success, temperatures = check_temperatures()
    if hasattr(p, '__iter__'):
        returnTemperatures = {ii : temperatures[ii] for ii in p if ii in temperatures}
        success = success and (len(returnTemperatures) == len(p))

        # Success if requested temperatures were successfully updated. 
        # Returns the current values of the requested temperatures.
        return (success, returnTemperatures)

    returnTemperature = temperatures[p] if p in temperatures else -1
    success = success and returnTemperature != -1

    # Success if requested temperature was successfully updated.
    # Returns the requested temperature if the request was valid
    # Returns an error code if the request was invalid:
    #   -1 if the request was not valid
    return (success, returnTemperature)

def set_heater_power(heater, power = 100):
    pass




    
