import pytest
from conftest import *
import time

from poudel_tests.utils.util import *
from pathlib import Path

# ==============================================================================
# CONSTANTS
# ==============================================================================

CRITICAL_BATTERY_THRESHOLD  = 0.20       # Battery level (20%) that triggers RTH
TIMEOUT_BATTERY_DRAIN       = 60         # Max seconds to wait for battery to drain
HOME                        = (48.109, 11.290, 0.0)  # Home coordinates (Gilching, Munich)
MAX_WIND_SPEED              = 35         # Maximum allowable wind speed (km/h)
RTH_TIMEOUT                 = 60.0       # Max seconds to wait for drone to reach HOME after RTH
TEST_CASE_ID                = "TC-E-005-EXT"
NEXT_POSITION               = (60.109, 12.290, 10.0)  # simulated waypoint
TEST_DATA_FILE              ="test_data.csv"
TICKS                       =100 ##ticks for battery drain simulation


# Build absolute path to test_data.csv relative to this test file
BASE_DIR   = Path(__file__).parent
file_path  = BASE_DIR / "test_data" /TEST_DATA_FILE 

# ==============================================================================
# LOGGER & TEST DATA SETUP
# ==============================================================================

try:
    log = logger()  # Initialize logger from utils
    # Load parametrized test inputs (battery level, wind speed) from CSV
    test_params = load_params_from_csv(file_path)
except Exception as e:
     raise 

            
    
      
         


# ==============================================================================
# TEST CLASS
# ==============================================================================

@pytest.mark.parametrize(
    "input_battery_level, input_wind_speed",
    test_params   # Each row in CSV provides one (battery_level, wind_speed) pair
)
class TestEmergencyReturn():

    def test_TC_E_005_EXT(self, drone, input_battery_level, input_wind_speed):
        """
        TC-E-005-EXT: Emergency Return-to-Home (RTH) on Critical Battery
        ---------------------------------------------------------------
        Validates that the drone autonomously triggers RTH when battery
        drops below CRITICAL_BATTERY_THRESHOLD, returns to HOME, and lands.

        Steps:
          1. Power on drone and initialize with parametrized battery/wind values
          2. Lock GPS and set HOME position
          3. Verify all preconditions pass
          4. Start mission 
          5. Drain battery below critical threshold(by simulation)
          6. Assert drone switches to RTH mode automatically
          7. Wait for drone to return HOME and land
          8. Assert final mode is LANDED and position is HOME
        """
        try:
            #pre_conditions = Drone_Preconditions()
            log.info(f"\n\n-------------------------- {TEST_CASE_ID} | Battery={input_battery_level} | Wind={input_wind_speed} ------------------------------------\n\n")

            # ------------------------------------------------------------------
            # STEP 1: Drone Initialisation
            # ------------------------------------------------------------------
            
            # Power on the drone
            drone.power_on_drone()
            log.info(f"{TEST_CASE_ID} Drone powered on.")
            assert drone.power == True, \
                    f"Drone failed to power on. Actual status: {drone.power}"

            # Set battery to parametrized level from CSV
            drone.initailize_battery(input_battery_level)

            # Enable GPS and wait for satellite lock (>6 satellites)
            drone.gps_lock()
            log.info(f"{TEST_CASE_ID} GPS locked (>6 satellites).")
            assert drone.gps == True, \
                    f"GPS not enabled. Actual status: {drone.gps}"

                # Set drone starting position to HOME
            drone.set_position(HOME)
            log.info(f"{TEST_CASE_ID} Home position set: {HOME}")

                # Apply parametrized wind speed
            drone.set_wind_speed(input_wind_speed)
            log.info(f"{TEST_CASE_ID} Wind speed set: {drone.wind}")

            

            # ------------------------------------------------------------------
            # STEP 2: Precondition Validation
            # ------------------------------------------------------------------
            #pre_conditions.drone_preconditions(drone)
            assert drone.battery_level >= CRITICAL_BATTERY_THRESHOLD, \
                    f"Low Battery: precondition not met. Battery={drone.battery_level}"
            log.info(f"{TEST_CASE_ID} Precondition: Battery OK = {drone.battery_level}")

                # Check drone is at HOME position
            assert drone.position == HOME, \
                    f"HOME location mismatch. Actual={drone.position}, Expected={HOME}"
            log.info(f"{TEST_CASE_ID} Precondition: Position OK = {drone.position}")

                # Check distance counter is reset to zero
            assert drone.distance == 0, \
                    f"Distance not zero. Actual={drone.distance}"
            log.info(f"{TEST_CASE_ID} Precondition: Distance OK = {drone.distance}")

                # Check wind speed is within safe limits
            assert drone.wind <= MAX_WIND_SPEED, \
                    f"Wind speed {drone.wind} exceeds max {MAX_WIND_SPEED}"
            log.info(f"{TEST_CASE_ID} Precondition: Wind speed OK = {drone.wind}")

            # ------------------------------------------------------------------
            # STEP 3: Start Mission & Fly to Target Waypoint
            # ------------------------------------------------------------------
            drone.start_mission()
            log.info(f"{TEST_CASE_ID} Mission started.")
            assert drone.mode == Mode.WAYPOINT, \
                f"Expected {Mode.WAYPOINT}, actual mode: {drone.mode}"
            log.info(f"{TEST_CASE_ID} Drone in WAYPOINT mode. Battery={drone.battery_level}")

            # Move drone to next waypoint in simulation
            drone.update_simulation(NEXT_POSITION)
            log.info(f"{TEST_CASE_ID} Drone moved to {NEXT_POSITION}. Battery={drone.battery_level}")

            # Drain battery to 10% to trigger critical battery event
            drone.simulate_battery_drain_to(10)

            # ------------------------------------------------------------------
            # STEP 4: Wait for Critical Battery Detection (triggers RTH)
            # ------------------------------------------------------------------
            start_time = time.time()
            log.info(f"{TEST_CASE_ID} Waiting for battery to drain below critical threshold...")

            while True:
                # RTH should trigger once battery drops below threshold
                if drone.battery_level < CRITICAL_BATTERY_THRESHOLD:
                    log.info(f"{TEST_CASE_ID} Critical battery detected: {drone.battery_level}")
                    break

                # Safety timeout — exit loop if drain takes too long
                if time.time() - start_time >= TIMEOUT_BATTERY_DRAIN:
                    log.warning(f"{TEST_CASE_ID} Battery drain timeout reached.")
                    break

                time.sleep(0.1)  # Polling interval

            # ------------------------------------------------------------------
            # STEP 5: Assert Drone Switched to RTH Mode
            # ------------------------------------------------------------------
            assert drone.mode == Mode.RTH, (
                f"Mode mismatch — expected {Mode.RTH}, got '{drone.mode}'. "
                f"Battery: {drone.battery_level}"
            )
            log.info(f"{TEST_CASE_ID} RTH mode confirmed. Battery={drone.battery_level}")

            # ------------------------------------------------------------------
            # STEP 6: Wait for Drone to Return HOME and Land
            # ------------------------------------------------------------------
            log.info(f"{TEST_CASE_ID} Waiting for drone to return HOME and land...")
            drone.update_simulation(HOME)  # Simulate drone flying back to HOME

            start_time = time.time()
            while True:
                # Exit loop when drone has landed
                if drone.mode == Mode.LANDED:
                    log.info(f"{TEST_CASE_ID} LANDED mode detected. Battery={drone.battery_level}")
                    break

                # Safety timeout — exit loop if landing takes too long
                if time.time() - start_time >= RTH_TIMEOUT:
                    log.warning(f"{TEST_CASE_ID} RTH timeout reached.")
                    break

            # ------------------------------------------------------------------
            # STEP 7: Final Assertions — Mode and Position
            # ------------------------------------------------------------------
            # Verify drone is in LANDED mode
            assert drone.mode == Mode.LANDED, (
                f"Mode mismatch — expected {Mode.LANDED}, got '{drone.mode}'. "
                f"Battery: {drone.battery_level}"
            )
            log.info(f"{TEST_CASE_ID} Drone landed successfully. Mode={drone.mode}")

            # Verify drone returned to HOME coordinates
            assert drone.position == HOME, (
                f"Position mismatch — expected {HOME}, got '{drone.position}'. "
                f"Battery: {drone.battery_level}"
            )
            log.info(f"{TEST_CASE_ID} Drone position verified: {drone.position}")

        # ----------------------------------------------------------------------
        # ERROR HANDLING
        # ----------------------------------------------------------------------
        except AssertionError as e:
            log.error(f"{TEST_CASE_ID} Test Failed {e}")
            raise  # Re-raise so pytest marks test as FAILED

        except Exception as e:
            log.error(f"{TEST_CASE_ID} Unexpected error: {e}")
            raise  # Re-raise so pytest marks test as ERROR

        finally:
            # Always runs — log test end regardless of pass/fail
            log.info(f"{TEST_CASE_ID} Test execution ended.")