# Pressure Advance Calibration for RepRapFirmware
This is a tool for generating test gcode for calibrating Pressure Advance on 3D-printers running [RepRapFirmware](https://reprapfirmware.org/). For example used by the Duet controller board.

## How to use
1. Install [Python](https://www.python.org/) (this tool is tested with 3.7.0 under Windows)
2. Clone repository to a local folder
3. Navigate to folder using a terminal
4. Setup your filaments and printers in the end of the file pa_cal.py
5. Execute command  'python pa_cal.py'
6. *.gcode files to calibrate each filament are generated in a directory for each of your printer.
