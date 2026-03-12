This project implements an automated Software‑in‑the‑Loop (SIL) test for validating a drone’s Emergency Return‑to‑Home (RTH) behavior when the battery level drops below a critical threshold.

The test is fully automated using pytest, supports CSV‑based parametrization, and includes robust precondition checks, mission simulation, battery drain simulation, and final landing verification.

The main test case implemented is:

TC‑E‑005‑EXT — Emergency Return on Critical Battery

How to run the program:
run bat file in windows:
run_test.bat



The test loads battery and wind values from:


test_data/test_data.csv

Each row becomes one test execution.

RTHtestlog is generated to check the log of the test execution

There is also CI/CD run file with github/workflow folder

```
1. Power on drone
       ↓
2. Initialize battery (from CSV) + GPS lock + set HOME position
       ↓
3. Precondition checks
   - Battery ≥ 20%
   - Position == HOME
   - Distance == 0
   - Wind speed ≤ 35 km/h
       ↓
4. Start mission → assert WAYPOINT mode
       ↓
5. Fly to NEXT_POSITION
       ↓
6. Simulate battery drain to 19%
       ↓
7. Wait for RTH trigger (battery < 20%)
       ↓
8. Assert drone mode == RTH
       ↓
9. Simulate return to HOME
       ↓
10. Wait for LANDED mode
       ↓
11. Assert mode == LANDED
12. Assert position == HOME
```