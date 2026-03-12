import time
from enum import Enum

CRITICAL_BATTERY_THRESHOLD = 0.20


class Mode(Enum):
    DISARMED        = "DISARMED"
    HOVER           = "HOVER"
    WAYPOINT        = "WAYPOINT"
    RTH             = "RTH"
    EMERGENCY_LAND  = "EMERGENCY_LAND"
    LANDED          = "LANDED"
    STANDBY         = "STAND_BY"


class Drone:
    

    def __init__(self,battery_start_level,wind_speed,mode):
        self._battery = battery_start_level
        self._mode = mode     
       
        self._position = (50.1351, 50.5820, 0.0)
        self._log = []
        self._dist_m = 0
        self._wind_km_hr = wind_speed  # km/h
        self._drain_rate=0.1
        self._power_on=False
        self._gps=False
        self._satellites=0
        

    # ---------------- Core control ----------------

    def set_home(self, position):
       # self._home = (lat, lon, alt)
        self._position =  position
    def set_position(self,position):
        self._position = position 
    def power_on_drone(self):
        self._power_on=True
    def shutdown(self):
        self.power_on=False    
    def gps_lock(self):
        self._gps = True
        self._satellites=7
        self._log.append("GPS Locked")

    def start_mission(self):
        if not self._gps:
            raise RuntimeError("GPS not enabled")
        self._mode =Mode.WAYPOINT
        self._log.append("MISSION_STARTED")
    def initailize_battery(self,initial_battery_level):
        self._battery=initial_battery_level

    def set_battery_level(self, level):
        self._battery = level
        self._log.append(f"BATTERY={level:.2f}")

        # Simple simulated FC logic
        if self._battery < CRITICAL_BATTERY_THRESHOLD and self._mode == Mode.WAYPOINT:
            self._mode = Mode.RTH
            self._log.append("EMERGENCY_RETURN_TRIGGERED")
    
    def set_drone_mode_automatically(self):
       
        # Simple simulated FC logic
        if self._battery <= CRITICAL_BATTERY_THRESHOLD and self._mode ==  Mode.WAYPOINT:
            self._mode = Mode.RTH
            self._log.append("EMERGENCY_RETURN_TRIGGERED")

    def set_wind_speed(self, wind_speed):
        self._wind_km_hr = wind_speed
        self._log.append(f"wind speed={wind_speed:.2f}")

    def _drain(self, ticks: float = 1.0) -> None:
        #self._battery
        level= max(0.0, self._battery - self._drain_rate * ticks)          
        #self.set_drone_mode_automatically()
        self.set_battery_level(level)
    
    def simulate_battery_drain_to(self, max_ticks: int = 50):
        """battery drain until 100 ticks."""
        for i in range(1,max_ticks):
            #self._battery - self._drain_rate * 1
            time.sleep(5)  
            if self._battery<CRITICAL_BATTERY_THRESHOLD:
                break
                  
            self._drain()
    
    def update_simulation(self,position):
        """
        Advance simulation. Replace with your SIL step function to reach home.
        """
        self._position=position
        time.sleep(2)
        if self._mode == Mode.RTH:
            self._position = position
            self._mode = Mode.LANDED
            self._log.append("LANDING")

        elif self._mode == Mode.LANDED:
            self._mode = Mode.LANDED
            self._log.append("LANDED")

    # ---------------- Telemetry ----------------

    @property
    def battery_level(self):
        return self._battery

    @property
    def mode(self):
        return self._mode

    @property
    def home(self):
        return self._home

    @property
    def position(self):
        return self._position
    @property
    def distance(self):
        return self._dist_m
    
    @property
    def wind(self):
        return self._wind_km_hr
    
    @property
    def power(self):
        return self._power_on
    
    @property
    def gps(self):
        return self._gps
      

    @property
    def log(self):
        return self._log[:]

