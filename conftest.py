import pytest
from poudel_tests.utils.drone_simulator import Drone  # Drone SIL
from poudel_tests.utils.drone_simulator import Mode


@pytest.fixture
def drone():
    battery_start_level=0.90
    wind_speed=20
    mode=Mode.STANDBY
    v = Drone(battery_start_level,wind_speed,mode)
    yield v
    v.shutdown()



