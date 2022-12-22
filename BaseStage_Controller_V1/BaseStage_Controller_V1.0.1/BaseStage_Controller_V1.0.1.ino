/* ********************************************************************************************************************
                                 ELD2222 Base Stage Controller
                       NEMA17  XYZ stepper stage with temperature and suction control
                
                LION/ELD
                Peter Numberi
                29/09/2022
                Firmware version; 1.0
                
                Hardware:
                - Arduino Mega 2560
                - ST Powerstep02 stepper driver board (3x stacked as X-NUCLEO-IHM03A1 board) in daisy chain configuration.
                - Power supply, SMPS 24Vdc 6.5 Amps 2x, 1x for  XYZ stepper motors/drivers & 1x for temperature control actor (firerods/TEC) + Arduino.
                - Watlow Firerod (24V/30Watt, 1/8 inch) as heatng element controlled via WPM357 MOSFET board.
                - 1x as TEC ()element controlled via single channel MOSFET board.
                - 1x Thomas 1410 diaphragm suction pump.
                - Device Control via USB/Serial commands (Terminal GUI and final use a Python GUI).
                - XYZ steppers step with 25600 steps per (motor shaft) revolution.
                - Stage spindle has a pitch of 2mm/rev ==> 2mm = 2000 um ==> 2000/25600 = 78 nanometer/step (theoritical).
                      Due to motor cogging, irreggular friction and stepper driver drive current inaccuraccies, accraccy is aprox 250-350 nanometer (worst case 4-5 microsteps off) while giving correct position in steps.

                FRONT PANEL LED INDICATION
                - PWR led (BLUE, Flashes when no power is available), also serial feedback regarding PSU voltage in case of no or lower voltage.
                - ACTOR LED (BLUE) TURNS ON when particular actor/output is active, e.g. when heater is on the HEATER led turn ON.
                - RUNMODE LED (BLUE): Continous ON=RUN, OFF=STOPMODE, ON/OFF flashing = RUNMODE ON and PIDMODE = OFF  (no temp control but XYZ steppers can be driven).
                - TEC/PELTIER LED (BLUE) has s slower PWN ON/OFF cycle of about 3 HZ, therefore the LED is visibly ON flashing during the ON period of the PWM.
                - The ERROR LED (RED) always flashes at 2 Hz when an error condition occurs (fast flash), when starting with no power (switch powered off or no power avail.) error flashes at 0.5 Hz (slow flash).
                
                

***********************************************************************************************************************
                                  serial command list
                                  
             - Com port settings: 115200/8/1/N
             - For testing, some terminal programs (HTERM/TERMITE) or use Arduino IDE "monitor"

                                    {COMMAND]: EXPLANATION          

              
            

               Single character generic commands
             - [i]: Get info/help on command set
             - [r]: Reset Arduino and stepper driver HW (does not reset values stored eeprom)   
             - [d]: Factory defaults/restore, this commands resets the eeprom values to hardcoded/initial values
             - [c]: Get the stepper driver (XYZ driver hardware) status
             - [l]: List parameters (current program parameters stored in NVM/Eeprom)
             
             Sequence of data parameters/settings of response from command [l]:             
             1)  STEPPER  X-STAGE MAX SPD
             2)  STEPPER  Y-STAGE MAX SPD
             3)  STEPPER  Z-STAGE MAX SPD
             4)  STEPPER ACCELERATION
             5)  STEPPER DECELERATION
             6)  TEMP. CONTROL SETPOINT
             7)  TEMP. CONTROL DEADBAND
             8)  PID Kp HEAT
             9)  PID Ki HEAT
             10) PID Kd HEAT
             11) PID Kp COOL
             12) PID Ki COOL
             13) PID Kd COOL
                  
             
             - [z]: Zero stages: Step motion FWD/REV till limit switches are engaged, then move back untill limit switches are disengaged en set stepper (internal accumulator) positions to 0.
             - [h]: Home the stages to 0/reference positions set by zero routine.
             - [n]: RUNMODE ==> RUN;  all actors/outputs engaged and coupled to logic process (mainly PID).
             - [p]: RUNMODE ==> STOP; all actors/outputs disengaged from logic process. 
             - [x]: STOP X/Y/Z stages at once irrespective of their current state.    
           

                Multi chararacter GET commands

                
              - [gid]: Get device ID (Device Type + Firmware version)  
              - [ga]:  Get stepper acceleration
              - [gd]:  Get stepper deceleration
                 
              - [go]: Get output (actor) state: This gives 3 data parameters:
                                      - HEATER state (0-255, where 0= OFF and value 1-255 = PWM min. of 1 and max. 255)
                                      - COOLER state (0-255, where 0= OFF and value 1-255 = PWM min. of 1 and max. 255)
                                      - SUCTION (pump) state  0=OFF and 1=ON
                                   
                                      
              - [gb]: Get stepper driver (hardware) status (gets sixteen (16) parameters)

                 State per bit (derived from status register word, see ST Powerstep01 manual 11.1.28 (page 71): 
                 
                 MOT_STALL_A  (bit 15)
                 MOT_STALL_B  (bit 14)     
                 MOT_OCD      (bit 13)
                 MOT_TH_A     (bit 12)   
                 MOT_TH_B     (bit 11)    
                 MOT_UVLO_ADC (bit 10)  
                 MOT_UVLO     (bit 9)
                 MOT_STCK     (bit 8)
                 MOT_CMD_ERR  (bit 7)
                 MOT_STA_A    (bit 6)    
                 MOT_STA_B    (bit 5)
                 MOT_DIR      (bit 4)
                 MOT_SW_EVN   (bit 3)
                 MOT_SW_F     (bit 2)
                 MOT_BUSY     (bit 1)
                 MOT_HIZ      (bit 0)

              - [gc]: Get the stepper driver (XYZ hardware) configuration ==> see Powerstep01 manual item 11.1 (page 51)
              use decimal as address

              - [ge]: Get error state, 1 byte (0-255 value), each bit represents a flag.
                  High/1 = bit set, LO/0 = bit not set.
              

                            Error conditions:
                        - NO POWER                                                  (bit 0) ==> RED LED WILL NOT FLASH, ONLY BLUE POWER FLASH
                        - ESTOP (emergency switch) enabled (pushed)                 (bit 1)
                        - No Stepper Driver comms or power not switched on          (bit 2)
                        - Thermocouple not connected/defective                      (bit 3)
                        - Heater response timeout => detected when PID is active    (bit 4)
                        - TEC response timeout => detected when PID is active       (bit 5)
                        - Stepper response timeout => detected when zero-ing        (bit 6)
                        - RTD not connected/defective/out of range                  (bit 7)
                        - Reserved                                                  (bit 8)
                        - Reserved                                                  (bit 9)
                        - Reserved                                                  (bit 10)
                        - Reserved                                                  (bit 11)
                        - Reserved                                                  (bit 12)
                        - Reserved                                                  (bit 13)
                        - Reserved                                                  (bit 14)
                        - Reserved                                                  (bit 15)
    

              - [gp[XYZ]]: Get stepper motor current position (steps from 0). e.g.:  gpx  ==> returns data in steps.
              - [gs[XYZ]]: Get stepper motor current speed (steps/sec).    e.g.:  gsx  ==> returns data in steps.
              - [gt]:Get stage temperature, in degrees Celsius.        e.g.:  gt   ==> returns temp in degrees C   
              - [gl]:Get limit switch state;responds with six states in following order:
              - [gid]: Get ID, respond with ID of Base stage controller

                        - 1) X-STAGE LSH
                        - 2) X-STAGE LSM
                        - 2) X-STAGE numeric end position
                        
                        - 3) Y-STAGE LSH
                        - 4) Y-STAGE LSM
                        - 4) Y-STAGE numeric end position
                        
                        - 5) Z-STAGE LSH
                        - 6) Z-STAGE LSM
                        - 7) Z-STAGE numeric end position
                                          

                Multi chararacter SET commands 
             
                Steppers:
              - [sa]: Set acceleration rate of motors, e.g: sa225 = set accel of motors to 225 (in steps per sec). 
              - [sd]: Set deceleration rate of motors, e.g: sd225 = set decel of motors to 225 (in steps per sec).
              - [ss]: Set run/top speed of motors, e.g: ss225 = set topspeed of motors 225,(in steps/sec ).
              - [sp[xyz]]: Set and goto position, e.g: sp1000 = stepper goto position 1000 steps/uM from 0 point (in steps or uM)
              - [sv[xyz]]: Velocity control, stepper[xyz] wil be set at a fixed constont speed until zero or mark limit is reached
                e.g.: 
                svx400  ==> manual velocity xstage 400 steps/sec in FWD direction
                svx-400 ==> manual velocity xstage 400 steps/sec in REV direction
                svz100  ==> manual velocity zstage 100 steps/sec in FWD direction
                                                   
             
                Temp. Control:
              - [sb]: Set temperature deadband for PID temperature control (in degrees C x 100) ==> sb220 = set tep. deadband to 2.2 deg. C.
              - [st]: Set temperature setpoint, e.g: st2510 = set temperature for PID control to 25.1 deg. C (value in deg. C x100)

                Suction:
              - [su]: Set suction pump state ON/OFF  ==> 0=OFF, 1=ON, ==> SU1 = ON, SU0 = OFF

                Temperature Offset:
              - [sf]: Set (Thermocouple) temperature offset, sending [so] will start temp. compensation, this takes aprox 40-45 seconds after this temp is compensated by RTD and added to eeprom

               Force Actors/heaters (only possible in stopmode)
               - [fc]: Force cooler  ON/ON,    ==> 0-OFF, 1=ON
               - [fh]: Force heater  ON/OFF,   ==> 0-OFF, 1=ON

              Force PIDMODE (run and stopmode)
               - [fp]: Force PIDMODE ON/OFF,   ==> 0=OFF, 1=ON

               
              

              ---------------------------      hardware component sources    ------------------------------------------------
              - Arduino Mega2560 microcontroller: 
              https://store.arduino.cc/products/arduino-mega-2560-rev3
              
              - Powerstep stepper driver board:
              https://www.st.com/en/ecosystems/x-nucleo-ihm03a1.html

              - Heater element:
              https://www.watlow.com/products/heaters/cartridge-insertion-heaters/miniature-cartridge-heaters  ==> C1A-9502 dia. 1/8 x 1" 24V-30W - 12" lead 

              - TEC (Peltier) module:
              https://www.cuidevices.com/product/resource/pdf/cp40.pdf (CP40236) ==> 8.6V/4A , 21.8W, 20x20 mm

              - Suction Pump:
              https://www.gardnerdenver.com/en-us/thomas/diaphragm-pumps-compressors/1410-series ==> 1410D or 1410V BLDC (14100211)


              - TODO:
              - Determine if suction needs throttling and pressure sense feedback
              - Double stage peltier/TEC setup ==> will do seperate unit dev/test at ELD
              - Split up acc/dec values for XYZ steppers
              - Mega2560, 
              
              
              
              

**************************************************************************************
************************************************************************************* */

#include "Ponoor_PowerSTEP01Library.h"      // library required for driver board with voltage and current mode
#include <Adafruit_MAX31865.h>              // Library for PT100 sensor board
#include "PID_v1.h"                         // PID control specific library
#include <Arduino.h>                        //
#include <Wire.h>                           //
#include <math.h>                           //
#include <EEPROM.h>                         // eeprom lib,  used to store variables in non volatile memory (NVM)
#include <SPI.h>                            // library required for SPI comms with motor driver board and encoder

// Pin definitions for the X-NUCLEO-IHM03A1 stepper driver connected to an Arduino mega (Atmega 2560)
#define nCS_PIN             10              // ==> n Chip Select pin
#define STCK_PIN            9               // ==> STUCK  pin
#define nSTBY_nRESET_PIN    8               // ==> n Standby pin
#define nBUSY_PIN           4               // ==> driver busy pin

// Stepper motor limit switches (switch) pin define
#define LSU_X_PIN           39              // LIMIT SWITCH PIN - OK
#define LSD_X_PIN           37              // LIMIT SWITCH PIN - OK

#define LSU_Y_PIN           49              // LIMIT SWITCH PIN -
#define LSD_Y_PIN           43              // LIMIT SWITCH PIN -

#define LSU_Z_PIN           47              // LIMIT SWITCH PIN 
#define LSD_Z_PIN           41              // LIMIT SWITCH PIN

// Indicator LEDS pin define
#define PWR_LED             24              // HEATER LED PIN
#define ERR_LED             27              // ERROR  LED PIN
#define HTR_LED             31              // HEATER LED PIN
#define CLR_LED             35              // HEATER LED PIN
#define XSTAGE_LED          23              // XSTAGE MOTOR LED PIN
#define YSTAGE_LED          25              // YSTAGE MOTOR LED PIN
#define ZSTAGE_LED          33              // ZSTAGE MOTOR LED PIN
#define RUNMODE_LED         29              // LOGIC/RUN LED PIN

// ACTORS (WPM357 CH1 = closest to input HDR, CH3 closest so PSU side) CLR FET board is located on heatsink with DCDC converter for TEC
// SWA EDC & SUC 45 <-> 44
#define ACT_EDC             44              // External Device Control pin connected to mosfet board (WPM357 -- CH1)
#define ACT_SUC             45              // Suction pin connected to mosfet board (WPM357 -- CH3)
#define ACT_HTR             46              // Heater pin connected to mosfet board (WPM357 -- CH2)
#define ACT_CLR             18              // Cooler pin connected to mosfet board

#define XSTAGE_DIR           0              // STEPPER MOTOR DIRECTION 
#define YSTAGE_DIR           0              // STEPPER MOTOR DIRECTION 
#define ZSTAGE_DIR           1              // STEPPER MOTOR DIRECTION

#define XSTAGE_ENABLE        1              // STEPPER MOTOR/DRIVER ACTIVE ==> 0 = NOT ACTIVE, 1 = ACTIVE
#define YSTAGE_ENABLE        1              // STEPPER MOTOR/DRIVER ACTIVE ==> 0 = NOT ACTIVE, 1 = ACTIVE
#define ZSTAGE_ENABLE        0              // STEPPER MOTOR/DRIVER ACTIVE ==> 0 = NOT ACTIVE, 1 = ACTIVE

//#define stage_um_per_rev    10000         // sets the stage count per revolution in micro-meters 
//#define stage_steps_per_rev 25600         // sets the stage count per revolution in stepper steps 

#define stage_pos_units     0               // Position unit (position in steps or uM, 0=>steps from zero pos. &  1=> uM from zero pos.)
#define stage_endpos_micron 10000000        // Maximum position from zero in micron 
#define stage_endpos_steps  1200000        // Maximum position from zero in step

// Thermocouple ADC input 
#define OS_13_BIT           64 
#define OS_14_BIT           256
#define STEPS_13_BIT        8192    
#define STEPS_14_BIT        16384 
#define PWR_PIN             65              // Power Check PIN (ADC
#define PSU_MOT             66              // ADC pin for power voltage supply motor.
#define PSU_TCO             67              // ADC pin for power supply voltage temp. control) 
#define TC_PIN              68              // Thermocouple PIN (ADC-A15)
#define VREF_PIN            69              // ADC VREF DEVICE (LM4040AIZ) PIN (2500mV) 

// Test & Debug Pin                          
#define TPD_PIN             19              // Generic test pin for scope debugging (54 / A0)

// NVM (EEPROM) locations
#define NVM_CHK_ADR         10              // checkval NVM address
#define NVM_DEC_ADR         20              // stepper down ramp (deceleration) NVM address
#define NVM_ACC_ADR         30              // stepper up ramp (acceleration) NVM address
#define NVM_SPD_X_ADR       40              // absolute  top speed NVM address
#define NVM_SPD_Y_ADR       50              // absolute  top speed NVM address
#define NVM_SPD_Z_ADR       60              // absolute  top speed NVM address
#define NVM_MSPD_ADR        70              // microstep top speed NVM address
#define NVM_TSP_ADR         80              // Temperature setpoint NVM address
#define NVM_TDB_ADR         90              // Temperature deadband NVM address
#define NVM_TOS_ADR         100             // Temperature offset NVM address


// MAX 31865 PT100 specific defines:
// Use software SPI: CS, DI, DO, CLK
Adafruit_MAX31865 thermo = Adafruit_MAX31865(14, 17, 15, 16); // mega2560 pinning
// use hardware SPI, just pass in the CS pin
//Adafruit_MAX31865 thermo = Adafruit_MAX31865(10);
// The value of the Rref resistor. Use 430.0 for PT100 and 4300.0 for PT1000
#define RREF      430.0
// The 'nominal' 0-degrees-C resistance of the sensor
// 100.0 for PT100, 1000.0 for PT1000
#define RNOMINAL  100.0

// *****  ON/OFF switches *********
int DBG_MODE                    = 0;        // Debug mode switch, DBG_MODE:  ==> 0=OFF, 1=PRINT-OUT, 2=PLOTTER
bool RUNMODE                    = 0;        // RUNMODE = 0 ==> SENSORS ENABLED, ACTORS DISABLED, RUNMODE = 1 ==> SENSORS ENABLED, ACTORS ENABLED
bool PIDMODE                    = 0;        // PIDMODE = 0 ==> CV_HEAT & CV_COOL forced to 0, PIDMODE = 1 ==> normal PID output control
//bool BYPASS_ZEROSTAGE         = 0;         
 // Bypass zero stage option before run ==> 0= OFF,  1= ON
bool SetManualLimits            = 1;        // Bypass zero stage option before run ==> 0= OFF,  1= ON

// **************************************  constants ******************************************************************************

char DeviceType[] = {"Base Stage Controller"};
const int  FW_Version           = 10;       // Firmware version /10
const bool ZERO_ON_INIT         = 0;        // Always ZERO stage on startup ==> 0=OFF, 1=ON
const bool CHK_OFS_ON_INIT      = 0;        // Check Temp. offset on init, 0=OFF, 1=ON
const bool motor_safe_start     = 1;        // motor safe start switch, 0=OFF, 1=ON (motor will not start untill all condition are met)
const bool motor_DRV_ENA        = 1;        // motor ENABLE, 0=OFF, 1=ON // motor disable switch
const bool MOTOR_DIR_SET        = 1;        // Motor direction, 1 = normal, 0 = reverse
const bool stepper_current_mode = 0;        // switch between current/voltage control modes (0=voltage mode, 1=current)
const int SafeStart_PASS_VAL    = 10;       // Amount of OK readings needed for safe start pass
const int SEN_INIT_TIME         = 10;       // Init time for sensor(s) in seconds
const int PID_SAMPLETIME        = 275;      // PID loop sampletime in mSecs
const long TCR_INTVAL           = 1;        // Thermocouple read interval in millisecs

const long UPD_PID_INTVAL     = 275;            // update PID interval in msecs -- 275 mS (3.6 Hz)
const long UPD_ACT_INTVAL     = 275;            // update actor interval in msecs --  275 mS (3.6 Hz)
const long UPD_TEC_INTVAL     = 275;            // update PID interval in msecs -- 275 mS (3.6 Hz)
const long UPD_DBG_INTVAL     = 1000;           // debug interval in msecs -- 1000 mS (1Hz)
const long UPD_MOT_INTVAL     = 10;             // update motor interval in msecs -- 10 mS (100 Hz)
const long UPD_PLT_INTVAL     = 30000;          // plotter interval in msecs -- 30000 mS ==> 30 secs
const long UPD_RTD_INTVAL     = 100;            // RTD temp sensor read interval in msecs  ==> 100 = 10Hz (!max 16Hz for MAX31865)
const long UPD_SIG_INTVAL     = 250;            // ERR LED FLASH INTERVAL (flash speed in msecs)

const int ADC_ZERO_OFFSET     = 0;              // Offset to zero ADC in ADC steps
const int ADC_mV_OFFSET       = 0;              // Offset in mV for 0-5000 mV range, (default = 0 mV)
const int TC_mV_OFFSET        = 0;              // Thermocouple mV value offset
const int TC_BaseVoltage      = 1233;           // Thermocouple base voltage (offset for main temp calculation formula), default 1250 


const int TC_FIL_GAIN         = 10;             // IIR type filter, 1=off, >1 is filter on with gain
const int TC_OS_SIZE          = OS_14_BIT;      // ADC oversampling batch size, 64=13 bit @ 832 uS , 256=14 bit @ 3328 uS 
const int MAX_PID_TEMP        = 25000;          // max temperature that can be set voor temp. PID control in deg C x10 so e.g. 2500 = 250.0 deg C
const int TEC_PWR_INT         = 250;            // interval for slow PWM of TEC module in mSecs (250)
const float MAX_TC_OFS        = 0;              // Max. Thermocouple offset

const int THR_GAIN            = 100;            // Throttle gain/scaler in % (100 = 100%)
const int MOT_DRV_DLAY        = 100;            // Pre motor drive delay in 100 mS loops
const int max_microstep_spd   = 550;            // Max micro step speed, when larger driver does 200 steps/rev ==> 10000 st/sec = 3.9 mm/sec   
const float max_stepper_speed = 500.00;         // max speed of stepper (steps/sec) ==> 2560 st/sec = 0.39 mm /sec 
const float min_stepper_speed = 0.005;          // Min stepper speed (steps/sec) 
const int HOMING_STEP_SPD     = 400;            // speed when homing in steps/sec in run mode
const float MAX_LIN_SPD       = 800.00;         // Maximum lineair speed in um/sec (e.g 1200 = 1200 uM/sec)
const float MOT_ZERO_SPD      = 20000;            // Stepper motor speed when zero ing stages to end point/limits


// Temperature PID control params/settings 
const double KP_HEAT          = 40.00;           // Kp: proportional tuning parameter for temperature
const double KI_HEAT          = 2.0;             // Ki: integral tuning parameter for temperature
const double KD_HEAT          = 0.02;            // Kd: derivative tuning parameter for temperature
const int GAIN_HTR            = 100;             // PWM scaler for HEATER actor (0-100%), eg: 50 = 50% of PWM value applied to [OUT_HEAT]
const int MAX_PWM_HTR         = 250;             // limit for clipping max PWM 
const double OFS_HTR          = 0;

const double KP_COOL          = 40.00;           // Kp: proportional tuning parameter for temperature
const double KI_COOL          = 2.0;             // Ki: integral tuning parameter for temperature
const double KD_COOL          = 0.02;            // Kd: derivative tuning parameter for temperature
const int GAIN_TEC            = 100;             // PWM scaler for HEATER actor (0-100%), eg: 50 = 50% of PWM value applied to [OUT_HEAT]
const int MAX_PWM_TEC         = 240;             // limit for clipping max PWM in case of overheating the firerod at 36V (overvoltage use). 
const double OFS_TEC          = 0;               // Base/zero level for TEC power 
const float RTD_T_OFFSET      = 0;               // RTD (PT100) temperature offset compensation value

const int SLOW_SPD_THR        = 1750;            // slow speed threshold in steps/sec ==> lower than this speed, drive method will switch to slow speed
const int MAX_JOG_STEP_SIZE   = 18;              // Maximum jog step size, for slow speed, step size @ 100 Hz (default 17), 17 ==> 1700 steps/sec @ 100 Hz update rate
const float MAX_SS_SPD        = 56500.00;        // Max Steps/Sec speed
const float MIN_SS_SPD        = 100.00;          // slowest possible speed, 1 step per iteration @ 100 Hz ==> 100 steps/sec

const long X_MAN_ENDPOS       = 627500;           // manual end position
const long Y_MAN_ENDPOS       = 659500;           // manual end position
const long X_CENTER_POS       = 627500;
const long Y_CENTER_POS       = 659500;
const long Z_MAN_ENDPOS       = -50000;          // manual end position

volatile double RXD_TEMP_VAL  = 0.00;            // Temporary value to prevent data entry spikes on plotter screen..
volatile double PV_TEMP       = 21.0;            // Process Value (PV) temperature (in deg C)  => 2 decimal rounding and use point as decimal separator
volatile double SP_TEMP       = 21.0;            // Temperature setpoint(SP) [values 0-100.00] => 2 decimal rounding and use point as decimal separator
volatile double DB_TEMP       = 0.00;            // DEADBAND temperature (in deg C)  => 2 decimal rounding and use point as decimal separator
double SP_HEAT                = 0;               // Temperature setpoint(SP_TEMP)- deadband (DB_TEMP) [values 0-100.00] => 2 decimal rounding and use point as decimal separator
double SP_COOL                = 0;               // Temperature setpoint(SP_TEMP)- deadband (DB_TEMP) [values 0-100.00] => 2 decimal rounding and use point as decimal separator
double CV_HEAT                = 0.0;             // Command value (CV) temperature(in deg C)  => 2 decimal rounding and use point as decimal separator
double CV_COOL                = 0.0;             // Command value (CV) temperature(in deg C)  => 2 decimal rounding and use point as decimal separator
int CV_TEC                    = 0;               // Command value (CV) temperature(in deg C)  => 2 decimal rounding and use point as decimal separator


// ERROR STATUS BITS:
int GLOBAL_ERR           = 0;                  // Hold global Error state ==> 16 bits

bool PWR_ERR             = 0;                  // HOLDS PWR ERROR, BIT 0 in GLOBAL ERROR
bool ESTOP_SET           = 0;                  // HOLDS ESTOP ERROR, BIT 1 in GLOBAL ERROR
bool RTD_ERR             = 0;                  // HOLDS RTD ERROR, BIT 2 in GLOBAL ERROR
bool TC_ERR              = 0;                  // HOLDS Thermocouple ERROR, BIT 3 in GLOBAL ERROR
bool ZERO_ERR            = 0;                  // HOLDS PWR ERROR, BIT 4 in GLOBAL ERROR
bool MOT_ERR             = 0;                  // HOLDS motor/steper ERROR, BIT 5 in GLOBAL ERROR
bool HTR_ERR             = 0;                  // HOLDS RES06 ERROR, BIT 6 in GLOBAL ERROR
bool TEC_ERR             = 0;                  // HOLDS RES07 ERROR, BIT 7 in GLOBAL ERROR
bool RES08_ERR           = 0;                  // HOLDS RES08 ERROR, BIT 8 in GLOBAL ERROR
bool RES09_ERR           = 0;                  // HOLDS RES09 ERROR, BIT 9 in GLOBAL ERROR
bool RES10_ERR           = 0;                  // HOLDS RES10 ERROR, BIT 10 in GLOBAL ERROR
bool RES11_ERR           = 0;                  // HOLDS RES11 ERROR, BIT 11 in GLOBAL ERROR
bool RES12_ERR           = 0;                  // HOLDS RES12 ERROR, BIT 12 in GLOBAL ERROR
bool RES13_ERR           = 0;                  // HOLDS RES13 ERROR, BIT 13 in GLOBAL ERROR
bool RES14_ERR           = 0;                  // HOLDS RES14 ERROR, BIT 14 in GLOBAL ERROR
bool RES15_ERR           = 0;                  // HOLDS RES15 ERROR, BIT 15 in GLOBAL ERROR


//stepper action variables
int ESTOP_CNT         = 0;                  // Hold number of ESTOPS done
bool TEC_ACT          = 0;                  // TEC ACTIVE flag

int FORCE_HTR = 0;                          // FORCE VALUE HEATER ==> 0-255
int FORCE_CLR = 0;                          // FORCE VALUE COOLER ==> 0-240

bool SET_VELO_X =0;                         // Set velocity command flag ; 0=DONE, 1=COMMAND ACTIVE
bool SET_VELO_Y =0;                         // Set velocity command flag ; 0=DONE, 1=COMMAND ACTIVE
bool SET_VELO_Z =0;                         // Set velocity command flag ; 0=DONE, 1=COMMAND ACTIVE

bool XSTAGE_LSU = 0;                        // limit switch up xstage
bool YSTAGE_LSU = 0;                        // limit switch up ystage
bool ZSTAGE_LSU = 0;                        // limit switch up zstage

bool XSTAGE_LSD = 0;                        // limit switch up xstage
bool YSTAGE_LSD = 0;                        // limit switch up xstage
bool ZSTAGE_LSD = 0;                        // limit switch up xstage

bool X_LSU_FLAG = 0;                        // limit switch up xstage
bool Y_LSU_FLAG = 0;                        // limit switch up xstage
bool Z_LSU_FLAG = 0;                        // limit switch up xstage

bool X_LSD_FLAG = 0;                        // limit switch up xstage
bool Y_LSD_FLAG = 0;                        // limit switch up xstage
bool Z_LSD_FLAG = 0;                        // limit switch up xstage

int X_APR_STATE = 0;                        // 0 = NO ACTION, 1 = COMMAND SEND, 2=RUN STARTED, 3=APPROACH, 4=MOTION COMPLETED
int Y_APR_STATE = 0;                        // 0 = NO ACTION, 1 = COMMAND SEND, 2=RUN STARTED, 3=APPROACH, 4=MOTION COMPLETED
int Z_APR_STATE = 0;                        // 0 = NO ACTION, 1 = COMMAND SEND, 2=RUN STARTED, 3=APPROACH, 4=MOTION COMPLETED 

bool HTR_STATE = 0;                         // Holds ON/OFF state of actor PIN
bool CLR_STATE = 0;                         // Holds ON/OFF state of actor PIN

int INIT_X_STAGE = 0;                       // Flag for holding initialisation state (stage has been zeroed to limit switch), 0 = no init, 1 = initialised
int INIT_Y_STAGE = 0;                       // Flag for holding initialisation state (stage has been zeroed to limit switch), 0 = no init, 1 = initialised
int INIT_Z_STAGE = 0;                       // Flag for holding initialisation state (stage has been zeroed to limit switch), 0 = no init, 1 = initialised


bool GOTO_X_FLAG = 0;                       // flag for holding goto command issued for specific stage
bool GOTO_Y_FLAG = 0;                       // flag for holding goto command issued for specific stage
bool GOTO_Z_FLAG = 0;                       // flag for holding goto command issued for specific stage

int INI_X_CNT = 0;                          // Init Counter Xstage
int INI_Y_CNT = 0;                          // Init Counter Ystage
int INI_Z_CNT = 0;                          // Init Counter Zstage

bool X_INIT_DONE = 0;                       // Init done flag, 0 = no init done, 1 = init done
bool Y_INIT_DONE = 0;                       // Init done flag, 0 = no init done, 1 = init done
bool Z_INIT_DONE = 0;                       // Init done flag, 0 = no init done, 1 = init done

float JOG_STEP_SIZE_X = 1;                  // holds stepsize value for slow speed jog motion 
float JOG_STEP_SIZE_Y = 1;                  // holds stepsize value for slow speed jog motion 
float JOG_STEP_SIZE_Z = 1;                  // holds stepsize value for slow speed jog motion 

//float TOP_SPD = 50.5;                     // generic stepper top speed in steps/sec
float TOP_SPD_X = 25600;                     // generic stepper top speed in steps/sec
float TOP_SPD_Y = 25600;                     // generic stepper top speed in steps/sec
float TOP_SPD_Z = 25600;                     // generic stepper top speed in steps/sec

int LIN_X_SPD = 0;                          // linear speed of stage
int LIN_Y_SPD = 0;                          // linear speed of stage
int LIN_Z_SPD = 0;                          // linear speed of stage

int MAX_STEP_ACCEL = 1000;                  // stepper max step speed acceleration
int MAX_STEP_DECEL = 1000;                  // stepper max step speed deceleration

int USTP_SPD = 1200;                        // microstep speed
int STEP_ACCEL = 600;                       // stepper step speed acceleration
int STEP_DECEL = 600;                       // stepper step speed deceleration
int CONV_SPD = 0;                           // converted motor speed ==> coverts uM/sec speed to steps/cycle speed
long MOVE_TMR = 0;                          // Timer value holds the moving time during a GOTO/SET POS command [sp]
bool MOTOR_DIR = 1;                         // Holds motor direction , either 1 or 0
int DBG_CNT = 0;                            // used for debug interval count/timer in mSecs
bool RESET_TO_ZERO = 0;                     // reset to zero flag
bool HOMING_TO_ZERO = 0;                    // home to zero flag
bool MOVE_TMR_DONE = 1;                     // Flag for move timer
int PSU_MOT_VAL = 0;                        // power supply motor ADC value
int PSU_TCO_VAL  = 0;                       // power supply temp controller ADC value
bool RUN_STATE = 0;                         // Holds state for RUN led signaling
bool SUCTIONMODE = 0;                       // Holds suction mode state (suction air pump), 0=OFF, 1=ON
float VELOCITY_X_CMD = 0;                   // Holds velocity command stage X
float VELOCITY_Y_CMD = 0;                   // Holds velocity command stage Y
float VELOCITY_Z_CMD = 0;                   // Holds velocity command stage Z


// ST POWERSTEP STATUS BITS (Powerstep01 manual page 71)
bool MOT_STALL_A  = 0;                      // holds bitvalue of motor status register
bool MOT_STALL_B  = 0;                      // holds bitvalue of motor status register
bool MOT_OCD      = 0;                      // holds bitvalue of motor status register
bool MOT_TH_A     = 0;                      // holds bitvalue of motor status register
bool MOT_TH_B     = 0;                      // holds bitvalue of motor status register
bool MOT_UVLO_ADC = 0;                      // holds bitvalue of motor status register
bool MOT_UVLO     = 0;                      // holds bitvalue of motor status register
bool MOT_STCK     = 0;                      // holds bitvalue of motor status register
bool MOT_CMD_ERR  = 0;                      // holds bitvalue of motor status register
bool MOT_STA_A    = 0;                      // holds bitvalue of motor status register
bool MOT_STA_B    = 0;                      // holds bitvalue of motor status register
bool MOT_DIR      = 0;                      // holds bitvalue of motor status register
bool MOT_SW_EVN   = 0;                      // holds bitvalue of motor status register
bool MOT_SW_F     = 0;                      // holds bitvalue of motor status register
bool MOT_BUSY     = 0;                      // holds bitvalue of motor status register
bool MOT_HIZ      = 0;                      // holds bitvalue of motor status register

// PT100
uint16_t rtd            = 0;                // RTD(PT100) readout variable
float ratio             = 0;                // RTD(PT100) readout variable
float RTD_TEMP          = 0;                // RTD(PT100) readout variable

float MOVE_AVG_SPD      = 0;                // stores average speed of a [sp] move 
float CUR_MOT_SPD       = 0;                // STORES CURRENT MOTOR SPEED
float CUR_MOT_SPD_X     = 0;                // STORES CURRENT MOTOR SPEED
float CUR_MOT_SPD_Y     = 0;                // STORES CURRENT MOTOR SPEED
float CUR_MOT_SPD_Z     = 0;                // STORES CURRENT MOTOR SPEED

float PSU_CHK_VOLTAGE     = 0;
float LIN_SPD           = 0;                // STORES Lineair/axial speed of stage
long DELTA_POS_MOT      = 0;                // Holds stepper position difference new-old pos
int DRIVER_STATUS       = 0;                // STORES STAtus READOUT FROM st DRIVER BOARD
int XSTAGE_STATUS       = 0;                // STORES STATUS READOUT FROM ST DRIVER BOARD
int YSTAGE_STATUS       = 0;                // STORES STATUS READOUT FROM ST DRIVER BOARD
int ZSTAGE_STATUS       = 0;                // STORES STATUS READOUT FROM ST DRIVER BOARD
int ERR_LEDSTATE        = 0;                // Holds the state of error LED
bool TPD_PINSTATE       = 0;                // Holds the state of TEST pin
float ADC_INP_mV        = 0;                // Holds converted value to mV
long TC_INP_mV          = 0;                // Holds converted value to mV
long STEPPER_POS_ACCUM  = 0;                // Stepper internal position accumulator
long ADC_CENTER_ACCUM   = 0;                // Accumulator for ADC centering routine
int MOT_DRV_DEL_CNT     = 0;                // Motor driver delay count
int ACT_STATE           = 0;                // (Bit state)
int ERR_STATE           = 0;                // (Bit state)
int DRIVER_CFG          = 0;                // Holds stepper driver config state
int STEPPER_CNT         = 0;                // Holds the number of steppers active ()

bool SPEED_MODE_X       = 1;                // Holds speed mode, 0=LOW SPEED, 1=NORMAL SPEED 
bool SPEED_MODE_Y       = 1;                // Holds speed mode, 0=LOW SPEED, 1=NORMAL SPEED 
bool SPEED_MODE_Z       = 1;                // Holds speed mode, 0=LOW SPEED, 1=NORMAL SPEED 

int STR_LEN             = 0;                // String Length var
long ZeroStage_Timeout  = 0;                // Zero ing stage timeout counter

// Eeprom VARS
int NVM_CHECKVAL        = 0;                // NVM is written checkval

//float MOT_JOG_STEP_SIZE = 200;            // Stepper motor move stepsize per iteration when push button is pressed (UP/DOWN)


int ZERO_DONE           = 0;                // Flag to block all goto untill a zero is done
int RXD_SET_VAL         = 0;


float TC_TEMP_CAL = 0;                      // Calculated thermocouple temp
long TC_TEMP_RAW  = 0;                      // Thermocouple ADC value ()

const int VREG_FIL_GAIN   = 31;             // IIR Filter gain 
long VREF_RAW         = 0;                  // LM4040 raw 10 bit ADC value (around 512-513 ish)
long  VREF_OS_ACC     = 0;                  // LM4040 oversampling accumulator value
float CUR_VREF        = 0;                  // LM4040 oversampled decimated value (13 or 14 bit ADC value)
float OLD_VREF        = 0;                  // Used in IIR filter
float FIL_VREF        = 0;                  // Used in IIR filter
float VREF_OSV        = 0;                  // Used in VREF sampler

// serial RXD variables
char rx_byte          = 0;                  // used in the serial read routine
String CMD_STR        = "";                 // used in the serial read routine
char CMD_CHAR         = 0;                  // used in the serial read routine
int CMD_byte          = 0;                  // used in the serial read routine
String rx_str         = "";                 // used in the serial read routine
int InitRun           = 0;                  // initrun var to check for a first run (empty eeprom) 
char rx_arr[10];                            // array for storing the serial RXD chars from GUI/PC
int rx_index          = 0;                  // rx pos/index for array 
long SER_RXD_VAL      = 0;                  // received RXD value

// ****** Thermocouple variables 
int TC_INP_RAW        = 0;                  // Thermocouple raw ADC input (10 bit)
int TC_INP_OSV        = 0;                  // Thermocouple ADC OVERSAMPLED value
long TC_INP_FIL       = 4300;               // Thermocouple filtered value, used IIR filter, preloaded to value (4350) which matches 21.0 Degcrees C
long TC_INP_OLD       = 4300;               // Thermocouple old value used IIR filter, preloaded to value (4350) which matches 21.0 Degcrees C
int TC_OS_CNT         = 0;                  // counts used for oversampling / decimation
long TC_OS_ACC        = 0;                  // oversampling accumulator
float OS_TEMP         = 0;                  // Thermocouple offset temperature ==> set manually or via init

// RTD variables
const int RTD_FIL_GAIN    = 9;              // IIR filter gain, ==> > 1 is filter is ON
float RTD_TEMP_RAW        = 0;              // RTD temp unfiltered
float RTD_TEMP_FIL        = 0;              // RTD temp filtered
float RTD_TEMP_OLD        = 0;              // RTD temp old value
bool  CHK_RTD             = 0;              // CHECK RTD FLAG
bool PWR_FLASH            = 0;              // used for power error signaling
//bool RTD_ERR            = 0;


// TIMER ISR variables 
volatile long MSEC_CNT    = 0;                     // holds msec count (generic msec timer)
volatile long UPD_MOV_TMR = 0;                     // holds timer value of current move  (for timed moves)         
volatile long UPD_CPB_CNT = 0;                     // check push button interval counter timer
volatile long UPD_PID_CNT = 0;                     // PID control loop interval counter timer
volatile long UPD_ACT_CNT = 0;                     // PID control loop interval counter timer
volatile long UPD_DBG_CNT = 0;                     // debug interval counter/timer
volatile long UPD_MOT_CNT = 0;                     // update driver counter/timer
volatile long UPD_PLT_CNT = 0;                     // update plotter counter/timer
volatile long REVO_TMR    = 0;                     // stepper revolution timer
volatile long UPD_TCR_CNT = 0;                     // update read Thermocouple temp sensor counter/timer
volatile long UPD_RTD_CNT = 0;                     // update read RTD temp sensor counter/timer
volatile long UPD_TEC_TMR = 0;                     // TEC/PELTIER ON TIME Timer
volatile long UPD_TEC_CNT = 0;                     // Timer for TEC/Peltier ON/OF period (4Hz slow PWM)
volatile long UPD_SIG_CNT = 0;                     // Counter/timer for err flash 
volatile long MOVE_TMR_X  = 0;                     // move timer (mSecs) for Xstage 
volatile long MOVE_TMR_Y  = 0;                     // move timer (mSecs) for Ystage 
volatile long MOVE_TMR_Z  = 0;                     // move timer (mSecs) for Zstage 
long uptime = 0;                                   // holds device runtime in seconds from startup

int DRIVE_DIR    = 0;                              // Holds drive direction state
int THR_VALUE    = 0;                              // Throttle value
int MIN_THR_UP   = 0;                              // MIN THR THRESHOLD up
int MIN_THR_DN   = 0;                              // MIN THR THRESHOLD down
int PLT_MTR_THR  = 0;                              // Plotter motor throttle (-25K to +25 K)

long Target_Position_X    = 0;                     // target position during goto move
long Target_Position_Y    = 0;                     // target position during goto move
long Target_Position_Z    = 0;                     // target position during goto move
long Target_Position      = 0;                     // target position during goto move

long TARGET_DIST_X        = 0;
long TARGET_DIST_Y        = 0;
long TARGET_DIST_Z        = 0;

long END_POS_X            = 0;                     // Holds stage end position (mark) in steps from 0 point, this value is set in ZeroStage()
long END_POS_Y            = 0;                     // Holds stage end position (mark) in steps from 0 point, this value is set in ZeroStage()
long END_POS_Z            = 0;                     // Holds stage end position (mark) in steps from 0 point, this value is set in ZeroStage()

long CUR_POS_MOT = 0;                              // max pos of motor when end point lim sw has been triggered
long OLD_POS_MOT = 0;                              // max pos of motor when end point lim sw has been triggered

long CUR_POS_MOT_X = 0;                            // holds current position for speed calculation
long CUR_POS_MOT_Y = 0;                            // holds current position for speed calculation
long CUR_POS_MOT_Z = 0;                            // holds current position for speed calculation
long OLD_POS_MOT_X = 0;                            // holds old position for speed calculation
long OLD_POS_MOT_Y = 0;                            // holds old position for speed calculation
long OLD_POS_MOT_Z = 0;                            // holds old position for speed calculation

float SET_SPD_X = 2560;
float SET_SPD_Y = 2560;
float SET_SPD_Z = 2560;


// powerSTEP library instance, parameters are distance from the end of a daisy-chain
powerSTEP xstage(0, nCS_PIN, nSTBY_nRESET_PIN);    // create driver instance for stage control via driver board
powerSTEP ystage(1, nCS_PIN, nSTBY_nRESET_PIN);    // create driver instance for stage control via driver board
powerSTEP zstage(2, nCS_PIN, nSTBY_nRESET_PIN);    // create driver instance for stage control via driver board

// create PID control instances (1 for heating and 1 for cooling)
PID HEAT_PID(&PV_TEMP, &CV_HEAT, &SP_HEAT, KP_HEAT, KI_HEAT, KD_HEAT,P_ON_E, DIRECT);   // create PID instance for heater temp control
PID COOL_PID(&PV_TEMP, &CV_COOL, &SP_COOL, KP_COOL, KI_COOL, KD_COOL,P_ON_E, REVERSE);  // create PID instance for cooler temp control

// ***********************************************  resetFunc   *****************************************************************************************************
// resets the Arduino
void(* resetFunc) (void) = 0;                    // declare reset fuction at address 0, this will soft reset the MCU (eeprom NOT erased!)
// ---   end reset function


// ******************************************************************************************************************************************************************
//                                                               SETUP
//  - Runs once to setup the hardware and load parameters/settings
//  - Will pause if an error occurs in driver setup/comms so error will need to be found for program to continue
//  - 
//
// ******************************************************************************************************************************************************************
void setup()
{ 
  Serial.begin(115200);                       // Start serial, 115200 bps/8/N/1

  delay(50);                                  // wait for serial init

  if(DBG_MODE < 2)                            // plotter disabled, print out debug info
  {
     Serial.println("");
     Serial.print("BaseStage Controller V"); // Values come from init values were variables are declared and set
     Serial.print(float(FW_Version/10,1));
     Serial.println(" starting...");
  }

  // Prepare pins
  pinMode(nSTBY_nRESET_PIN, OUTPUT);          // config I/O of Mega2560
  pinMode(nCS_PIN, OUTPUT);                   // config I/O of Mega2560
  pinMode(MOSI, OUTPUT);                      // config I/O of Mega2560
  pinMode(MISO, INPUT);                       // config I/O of Mega2560
  pinMode(SCK, OUTPUT);                       // config I/O of Mega2560

  // GPIO
  pinMode(TPD_PIN, OUTPUT);                   // config I/O of Mega2560
  pinMode(PWR_LED, OUTPUT);                   // config I/O of Mega2560
  pinMode(ERR_LED, OUTPUT);                   // config I/O of Mega2560
  pinMode(HTR_LED, OUTPUT);                   // config I/O of Mega2560
  pinMode(CLR_LED, OUTPUT);                   // config I/O of Mega2560
  pinMode(XSTAGE_LED, OUTPUT);                // config I/O of Mega2560
  pinMode(YSTAGE_LED, OUTPUT);                // config I/O of Mega2560
  pinMode(ZSTAGE_LED, OUTPUT);                // config I/O of Mega2560
  pinMode(RUNMODE_LED, OUTPUT);               // config I/O of Mega2560
  
  pinMode(ACT_HTR, OUTPUT);                   // config I/O of Mega2560
  pinMode(ACT_CLR, OUTPUT);                   // config I/O of Mega2560
  pinMode(ACT_SUC, OUTPUT);                   // config I/O of Mega2560
  pinMode(ACT_EDC, OUTPUT);                   // config I/O of Mega2560  

  pinMode(LSU_X_PIN, INPUT_PULLUP);           // config I/O of Mega2560
  pinMode(LSD_X_PIN, INPUT_PULLUP);           // config I/O of Mega2560
  
  pinMode(LSU_Y_PIN, INPUT_PULLUP);           // config I/O of Mega2560
  pinMode(LSD_Y_PIN, INPUT_PULLUP);           // config I/O of Mega2560
  
  pinMode(LSU_Z_PIN, INPUT_PULLUP);           // config I/O of Mega2560
  pinMode(LSD_Z_PIN, INPUT_PULLUP);           // config I/O of Mega2560


  // Init ACTORS in LOWW/OFF STATE
  digitalWrite(PWR_LED, HIGH);                // INIT PIN to correct state
  digitalWrite(ACT_HTR, LOW);                 // INIT PIN to correct state
  digitalWrite(ACT_CLR, LOW);                 // INIT PIN to correct state
  digitalWrite(ACT_SUC, LOW);                 // INIT PIN to correct state
  digitalWrite(ACT_EDC, LOW);                 // INIT PIN to correct state
  
 
  // Reset powerSTEP and set CS
  digitalWrite(nSTBY_nRESET_PIN, HIGH);       // INIT PIN to correct state
  digitalWrite(nSTBY_nRESET_PIN, LOW);        // INIT PIN to correct state
  digitalWrite(nSTBY_nRESET_PIN, HIGH);       // INIT PIN to correct state
  digitalWrite(nCS_PIN, HIGH);                // INIT PIN to correct state

  STEPPER_CNT = XSTAGE_ENABLE + YSTAGE_ENABLE + ZSTAGE_ENABLE; // mostly XY or XYZ usage so should be 2 or 3


  // ***********  NVM read/write parameter setup ******************************************************************
 
  NVM_CHECKVAL = EEPROM.read(NVM_CHK_ADR);        // Location of NVM_CHECKVAL = 2
  
  if(NVM_CHECKVAL == 2)                           // eeprom has been programmed previously get parameters from NVM
  {
     if(DBG_MODE == 1)                            // plotter disabled, print out debug info
     {
        Serial.println("");
        Serial.println("Initializing parameter values from eeprom...");   // feedback to user
     }
    
     EEPROM.get(NVM_SPD_X_ADR,TOP_SPD_X);         // GET stepper motor top speed setting from NVM    
     EEPROM.get(NVM_SPD_Y_ADR,TOP_SPD_Y);         // GET stepper motor top speed setting from NVM    
     EEPROM.get(NVM_SPD_Z_ADR,TOP_SPD_Z);         // GET stepper motor top speed setting from NVM
     EEPROM.get(NVM_MSPD_ADR,USTP_SPD);           // GET stepper microstep top speed setting from NVM
     EEPROM.get(NVM_DEC_ADR,STEP_DECEL);          // GET stepper motor deceleration setting from NVM
     EEPROM.get(NVM_ACC_ADR,STEP_ACCEL);          // GET stepper motor acceleration setting from NVM
     EEPROM.get(NVM_TSP_ADR,SP_TEMP);             // GET PID temperature setpoint setting from NVM
     EEPROM.get(NVM_TDB_ADR,DB_TEMP);             // GET PID deadband setting from NVM
     EEPROM.get(NVM_TOS_ADR,OS_TEMP);             // GET PID deadband setting from NVM

     SP_HEAT = double(SP_TEMP - DB_TEMP);         // re-calculate deadband adjusted Temperature setpoint for PID task
     SP_COOL = double(SP_TEMP + DB_TEMP);         // re-calculate deadband adjusted Temperature setpoint for PID task


      // speed note , speed reolves in 1750 step/se steps, s0 1750/3500/5250

      // top speed Xstage
      if(TOP_SPD_X < SLOW_SPD_THR) // lower than aprox 1750 steps/sec
      {
          SPEED_MODE_X = 0;
          JOG_STEP_SIZE_X = float(TOP_SPD_X) / 116; // ==> / 100 since  
          
          if (JOG_STEP_SIZE_X < 1)
          {
            JOG_STEP_SIZE_X = 1;                    // clipper lower range
          }
      }
      else
      {
          SPEED_MODE_X = 1;
          SET_SPD_X = TOP_SPD_X / 170;              // convert to steps/sec
      }
  
       // top speed Ystage
      if(TOP_SPD_Y < SLOW_SPD_THR)                  // lower than aprox 1750 steps/sec
      {
          SPEED_MODE_Y = 0;
          JOG_STEP_SIZE_Y = TOP_SPD_Y / 116;        // ==> / 100 since  
          
          if (JOG_STEP_SIZE_Y < 1)
          {
            JOG_STEP_SIZE_Y = 1;                    // clipper lower range
          }
      }
      else
      {
          SPEED_MODE_Y = 1;
          SET_SPD_Y = TOP_SPD_Y / 170;              // convert to steps/sec
      }


       // top speed Ystage
      if(TOP_SPD_Z < SLOW_SPD_THR)                  // lower than aprox 1750 steps/sec
      {
          SPEED_MODE_Z = 0;
          JOG_STEP_SIZE_Z = TOP_SPD_Z / 116;        // ==> / 100 since  
          
          if (JOG_STEP_SIZE_Z < 1) 
          {
            JOG_STEP_SIZE_Z = 1;                    // clip lower range
          }
      }
      else
      {
          SPEED_MODE_Z = 1;
          SET_SPD_Z = TOP_SPD_Z / 170;              // convert to steps/sec
      }
     

      if(DBG_MODE == 1)                             // plotter disabled, print out debug info
      {
         Serial.print("SP_TEMP: ");                 // Feedback for GUI
         Serial.println(SP_TEMP);                   // Setpoint temp
         
         Serial.print("DB_TEMP: ");                 // Feedback for GUI
         Serial.println(DB_TEMP);                   // Deadband temp
         
         Serial.print("STEP_ACCEL: ");              // Feedback for GUI
         Serial.println(STEP_ACCEL);                // stepper acceleration
         
         Serial.print("STEP_DECEL: ");              // Feedback for GUI
         Serial.println(STEP_DECEL);                // stepper deceleration
         
         Serial.print("USTP_SPD: ");                // Feedback for GUI
         Serial.println(USTP_SPD);                  // Setpoint temp         
         
         Serial.print("TOP_SPD_X: ");               // Feedback for GUI
         Serial.println(TOP_SPD_X);                 // 
         Serial.print("TOP_SPD_Y: ");               // Feedback for GUI
         Serial.println(TOP_SPD_Y);                 // 
         Serial.print("TOP_SPD_Z: ");               // Feedback for GUI
         Serial.println(TOP_SPD_Z);                 // 

         Serial.print("SPEED_MODE_X: ");            // Feedback for GUI
         Serial.println(SPEED_MODE_X);              // 
         Serial.print("SPEED_MODE_Y: ");            // Feedback for GUI
         Serial.println(SPEED_MODE_Y);              // 
         Serial.print("SPEED_MODE_Z: ");            // Feedback for GUI
         Serial.println(SPEED_MODE_Z);              // 

         Serial.print("JOG_STEP_SIZE_X: ");         // Feedback for GUI
         Serial.println(JOG_STEP_SIZE_X);           // 
         Serial.print("JOG_STEP_SIZE_Y: ");         // Feedback for GUI
         Serial.println(JOG_STEP_SIZE_Y);           // 
         Serial.print("JOG_STEP_SIZE_Z: ");         // Feedback for GUI
         Serial.println(JOG_STEP_SIZE_Z);           //                  
      }          
  }
  else // NVM not programmed ==> do initial value NVM programming
  {
     if(DBG_MODE == 1)                            // plotter disabled, print out debug info
     {
        Serial.println("");
        Serial.println("Writing initial parameter values into eeprom..."); // Values come from init values were variables are declared and set
     }
  
     NVM_CHECKVAL = 2;                            // Set NVM checkval 

     SP_HEAT = double(SP_TEMP - DB_TEMP);         // re-calculate deadband adjusted Temperature setpoint for PID heating
     SP_COOL = double(SP_TEMP + DB_TEMP);         // re-calculate deadband adjusted Temperature setpoint for PID cooling    

     SET_SPD_X = TOP_SPD_X / 170;                 // convert to steps/sec
     SET_SPD_Y = TOP_SPD_Y / 170;                 // convert to steps/sec
     SET_SPD_Z = TOP_SPD_Z / 170;                 // convert to steps/sec
    
     
     EEPROM.write(NVM_CHK_ADR, NVM_CHECKVAL);     // NVM_CHECKVAL is set into NVM 
     delay(10);                                   // wait for NVM action to complete
     EEPROM.put(NVM_SPD_X_ADR,TOP_SPD_X);         // PUT stepper motor top speed setting into NVM
     delay(10); // wait for action to complete
     EEPROM.put(NVM_SPD_Y_ADR,TOP_SPD_Y);         // PUT stepper motor top speed setting into NVM
     delay(10); // wait for action to complete
     EEPROM.put(NVM_SPD_Z_ADR,TOP_SPD_Z);         // PUT stepper motor top speed setting into NVM
     delay(10); // wait for action to complete
     EEPROM.put(NVM_MSPD_ADR,USTP_SPD);           // PUT stepper microstep speed setting into NVM
     delay(10); // wait for action to complete
     EEPROM.put(NVM_DEC_ADR,STEP_DECEL);          // PUT stepper motor deceleration setting into NVM
     delay(10); // wait for action to complete
     EEPROM.put(NVM_ACC_ADR,STEP_ACCEL);          // PUT stepper motor acceleration setting into NVM
     delay(10); // wait for action to complete
     EEPROM.put(NVM_TSP_ADR,SP_TEMP);             // PUT PID temperature setpoint setting into NVM
     delay(10); // wait for action to complete
     EEPROM.put(NVM_TDB_ADR,DB_TEMP);             // PUT PID deadband setting into NVM
     delay(10); // wait for action to complete
     EEPROM.put(NVM_TOS_ADR,OS_TEMP);             // PUT PID deadband setting into NVM
     delay(10); // wait for action to complete
     
  }  
  

 // ***********  setup and initialize timer1 registers of Arduino Mega for task scheduling via timers (incremented in ISR) ******************************************************************  
  noInterrupts();                           // disable all interrupts
  TCCR1A = 0;                               // direct register setting ==> 0
  TCCR1B = 0;                               // direct register setting ==> 0

  TCNT1 = 65474;                            // preload timer 65536-16MHz/256/2 (Hz) into register ==> will trigger every 1 mSec
  TCCR1B |= (1 << CS12);                    // 256 (prescaler) 
  TIMSK1 |= (1 << TOIE1);                   // enable timer overflow interrupt
  interrupts();                             // enable all interrupts 
 // end interrupt setup...

  delay(10);                                // wait for action to complete
 
  // RTD/PT100 board starup 
  thermo.begin(MAX31865_4WIRE);             // set to 2WIRE or 4WIRE as necessary
 
 // Start SPI comms
  SPI.begin();                              // start SPI comms
  SPI.setDataMode(SPI_MODE3);               // set SPI data mode
  delay(10);                                // Insert delay of 10 mSecs

  // Configure powerSTEP boards
  xstage.SPIPortConnect(&SPI);              // give library the SPI port 
  ystage.SPIPortConnect(&SPI);              // give library the SPI port  
  zstage.SPIPortConnect(&SPI);              // give library the SPI port 
  
  xstage.configSyncPin(BUSY_PIN, 0);        // use SYNC/nBUSY pin as nBUSY, 
                                            // thus syncSteps (2nd paramater) does nothing
  ystage.configSyncPin(BUSY_PIN, 0);        // use SYNC/nBUSY pin as nBUSY, 
                                            // thus syncSteps (2nd paramater) does nothing
  zstage.configSyncPin(BUSY_PIN, 0);        // use SYNC/nBUSY pin as nBUSY, 
                                            // thus syncSteps (2nd paramater) does nothing

  delay(25);                                // Insert delay of 25 mSecs

  XSTAGE_STATUS = 0;                        // Init to 0
  YSTAGE_STATUS = 0;                        // Init to 0
  ZSTAGE_STATUS = 0;                        // Init to 0

  XSTAGE_STATUS = xstage.getStatus();       // clears error flags
  YSTAGE_STATUS = ystage.getStatus();       // clears error flags
  ZSTAGE_STATUS = zstage.getStatus();       // clears error flags

  if(DBG_MODE == 1)                          // only print when plotter is off
  {     
    Serial.print("");                       // spacer
    Serial.print("XSTAGE_STATUS:");         // status feedback
    Serial.println(XSTAGE_STATUS);          // status feedback
    Serial.print("YSTAGE_STATUS:");         // status feedback
    Serial.println(YSTAGE_STATUS);          // status feedback
    Serial.print("ZSTAGE_STATUS:");         // status feedback
    Serial.println(ZSTAGE_STATUS);          // status feedback
  }    


  // Power/PSU status check and signaling
  PSU_CHK_VOLTAGE  = (analogRead(PWR_PIN)) * 25.22;      // 24.24 Vdc = aprox 961 ADC steps

  while(PSU_CHK_VOLTAGE < 9000)
  {
     PSU_CHK_VOLTAGE  = (analogRead(PWR_PIN)) * 25.22;      // 24.24 Vdc = aprox 961 ADC steps
     PWR_ERR = 1;  
     Serial.print("No power detected, PSU Voltage (mV): ");        // status feedback
     Serial.println(PSU_CHK_VOLTAGE); 
     ERR_LEDSTATE = !ERR_LEDSTATE;           // Toggle, LED STATE 
     digitalWrite(PWR_LED, ERR_LEDSTATE);    //  Override pin state, for debugging purposes
     
     delay(500);
  }

  Serial.print("PSU PASS (mV): "); 
  Serial.println(PSU_CHK_VOLTAGE,0); 

   PWR_ERR = 0;
   digitalWrite(PWR_LED, HIGH);               // PWR LED ON

   PSU_MOT_VAL  = (analogRead(PSU_MOT));              // check voltage stepper motor PSU 
   PSU_TCO_VAL  = (analogRead(PSU_TCO));              // check voltage temp. control PSU 
   

   while((PSU_MOT_VAL < 200) && (PSU_TCO_VAL < 200))      // check voltage of power supply motor and power supply temp control
   {
      PSU_MOT_VAL  = (analogRead(PSU_MOT));              // check voltage stepper motor PSU ==> ADC conv. mV/step
      PSU_TCO_VAL  = (analogRead(PSU_TCO));              // check voltage temp. control PSU ==> ADC conv. mV/step

      Serial.println("ESTOP ENABLED!!");         // status feedback     
      ERR_LEDSTATE = !ERR_LEDSTATE;           // Toggle, LED STATE 
      digitalWrite(ERR_LED, ERR_LEDSTATE);    //  Override pin state, for debugging purposes
      ESTOP_SET = 1;                          // set error flag high

      delay(500);
   }

   Serial.println("ESTOP PASS...");         // status feedback     

   ESTOP_SET = 0;
   digitalWrite(ERR_LED, LOW);              // ERR LED OFF
   

   XSTAGE_STATUS = xstage.getStatus();       // clears error flags when status is read
   YSTAGE_STATUS = ystage.getStatus();       // clears error flags when status is read
   ZSTAGE_STATUS = zstage.getStatus();       // clears error flags when status is read
  
 
  while((!XSTAGE_STATUS)&&(!YSTAGE_STATUS)&&(!ZSTAGE_STATUS)&&(motor_safe_start)) // check if stepper drive board/controller is powered up ()
  {
    XSTAGE_STATUS = xstage.getStatus();       // clears error flags when status is read
    YSTAGE_STATUS = ystage.getStatus();       // clears error flags when status is read
    ZSTAGE_STATUS = zstage.getStatus();       // clears error flags when status is read

    if((!XSTAGE_STATUS) || (!YSTAGE_STATUS) || (!ZSTAGE_STATUS))
    {      
      Serial.println("");                     // spacer
      Serial.print("XSTAGE_STATUS:");         // status feedback
      Serial.println(XSTAGE_STATUS);          // status feedback
      Serial.print("YSTAGE_STATUS:");         // status feedback
      Serial.println(YSTAGE_STATUS);          // status feedback
      Serial.print("ZSTAGE_STATUS:");         // status feedback
      Serial.println(ZSTAGE_STATUS);          // status feedback
      Serial.print("");                       // spacer
      Serial.println("Stepper driver(s) not online....");        // status feedback
      ERR_LEDSTATE = !ERR_LEDSTATE;           // Toggle, LED STATE 
      digitalWrite(ERR_LED, ERR_LEDSTATE);    //  Override pin state, for debugging purposes
      digitalWrite(PWR_LED, LOW);                // INIT PIN to correct state
      delay(1000);
    }
    else
    {
      digitalWrite(ERR_LED, LOW);           //  Override pin state, for debugging purposes
      digitalWrite(PWR_LED, HIGH);                // INIT PIN to correct state
     
      break;                                //  If available/online break out of error loop and continue setup
    }    
  }  

  Serial.println("DRIVER CHECK PASS...");         // status feedback     

  xstage.configStepMode(STEP_FS_128);       // full step divider, full steps = STEP_FS,  // options: 1, 1/2, 1/4, 1/8, 1/16, 1/32, 1/64, 1/128
  ystage.configStepMode(STEP_FS_128);       // full step divider, full steps = STEP_FS,  // options: 1, 1/2, 1/4, 1/8, 1/16, 1/32, 1/64, 1/128
  zstage.configStepMode(STEP_FS_128);       // full step divider, full steps = STEP_FS,  // options: 1, 1/2, 1/4, 1/8, 1/16, 1/32, 1/64, 1/128
  
  xstage.setMinSpeed(1);                    // max speed in units of full steps/s  //driver.setMinSpeed(min_stepper_speed);  // max speed in units of full steps/s    
  ystage.setMinSpeed(1);                    // max speed in units of full steps/s  //driver.setMinSpeed(min_stepper_speed);  // max speed in units of full steps/s       
  zstage.setMinSpeed(1);                    // max speed in units of full steps/s  //driver.setMinSpeed(min_stepper_speed);  // max speed in units of full steps/s
                                       
  xstage.setMaxSpeed(SET_SPD_X);    // max speed in units of full steps/s 
  ystage.setMaxSpeed(SET_SPD_Y);    // max speed in units of full steps/s 
  zstage.setMaxSpeed(SET_SPD_Z);    // max speed in units of full steps/s 
  
  xstage.setFullSpeed(max_microstep_spd);   // full steps/s threshold for disabling microstepping
  ystage.setFullSpeed(max_microstep_spd);   // full steps/s threshold for disabling microstepping
  zstage.setFullSpeed(max_microstep_spd);   // full steps/s threshold for disabling microstepping
 
  xstage.setAcc(STEP_ACCEL);                // full steps/s^2 acceleration
  ystage.setAcc(STEP_ACCEL);                // full steps/s^2 acceleration
  zstage.setAcc(STEP_ACCEL);                // full steps/s^2 acceleration
  
  xstage.setDec(STEP_DECEL);                // full steps/s^2 deceleration
  ystage.setDec(STEP_DECEL);                // full steps/s^2 deceleration
  zstage.setDec(STEP_DECEL);                // full steps/s^2 deceleration
  
  xstage.setSlewRate(SR_980V_us);           // faster may give more torque (but also EM noise),
                                            // options are: 114, 220, 400, 520, 790, 980(V/us)
  ystage.setSlewRate(SR_980V_us);           // faster may give more torque (but also EM noise),
                                            // options are: 114, 220, 400, 520, 790, 980(V/us)
  zstage.setSlewRate(SR_980V_us);           // faster may give more torque (but also EM noise),
                                            // options are: 114, 220, 400, 520, 790, 980(V/us)
                                            
  xstage.setOCThreshold(2);                 // over-current threshold for the 2.8A NEMA23 motor
  ystage.setOCThreshold(2);                 // over-current threshold for the 2.8A NEMA23 motor
  zstage.setOCThreshold(2);                 // over-current threshold for the 2.8A NEMA23 motor
                                             // used in testing. If your motor stops working for
                                             // no apparent reason, it's probably this. Start low
                                             // and increase until it doesn't trip, then maybe
                                             // add one to avoid misfires. Can prevent catastrophic
                                             // failures caused by shorts
                            
  xstage.setOCShutdown(OC_SD_ENABLE);        // shutdown motor bridge on over-current event
  ystage.setOCShutdown(OC_SD_ENABLE);        // shutdown motor bridge on over-current event
  zstage.setOCShutdown(OC_SD_ENABLE);        // shutdown motor bridge on over-current event
                                             // to protect against permanant damage


  xstage.setPWMFreq(PWM_DIV_1, PWM_MUL_1);    // 16MHz*0.75/(512*1) = 23.4375kHz 
  ystage.setPWMFreq(PWM_DIV_1, PWM_MUL_1);    // 16MHz*0.75/(512*1) = 23.4375kHz 
  zstage.setPWMFreq(PWM_DIV_1, PWM_MUL_1);    // 16MHz*0.75/(512*1) = 23.4375kHz 
  
  //xstage.setPWMFreq(PWM_DIV_2, PWM_MUL_0_75); // 16MHz*0.75/(512*1) = 23.4375kHz ==> audible whine
  //ystage.setPWMFreq(PWM_DIV_2, PWM_MUL_0_75); // 16MHz*0.75/(512*1) = 23.4375kHz ==> audible whine
  //zstage.setPWMFreq(PWM_DIV_2, PWM_MUL_0_75); // 16MHz*0.75/(512*1) = 23.4375kHz ==> audible whine
  
                                              // power is supplied to stepper phases as a sin wave,  
                                              // frequency is set by two PWM modulators,
                                              // Fpwm = Fosc*m/(512*N), N and m are set by DIV and MUL,
                                              // options: DIV: 1, 2, 3, 4, 5, 6, 7, 
                                              // MUL: 0.625, 0.75, 0.875, 1, 1.25, 1.5, 1.75, 2
                            
  xstage.setVoltageComp(VS_COMP_DISABLE);     // no compensation for variation in Vs as
  ystage.setVoltageComp(VS_COMP_DISABLE);     // no compensation for variation in Vs as
  zstage.setVoltageComp(VS_COMP_DISABLE);     // no compensation for variation in Vs as
                                              // ADC voltage divider is not populated
                                          
  xstage.setSwitchMode(SW_USER);              // switch doesn't trigger stop, status can be read.
  ystage.setSwitchMode(SW_USER);              // switch doesn't trigger stop, status can be read.
  zstage.setSwitchMode(SW_USER);              // switch doesn't trigger stop, status can be read.
                                              // SW_HARD_STOP: TP1 causes hard stop on connection 
                                              // to GND, you get stuck on switch after homing
                                      
  xstage.setOscMode(INT_16MHZ);  // 16MHz internal oscillator as clock source
  ystage.setOscMode(INT_16MHZ);  // 16MHz internal oscillator as clock source
  zstage.setOscMode(INT_16MHZ);  // 16MHz internal oscillator as clock source

  // KVAL registers set the power to the motor by adjusting the PWM duty cycle,
  // use a value between 0-255 where 0 = no power, 255 = full power.
  // Start low and monitor the motor temperature until you find a safe balance
  // between power and temperature. Only use what you need
  
  xstage.setRunKVAL(64);           // voltage mode compensation for run 
  xstage.setAccKVAL(64);           // voltage mode compensation for acc 
  xstage.setDecKVAL(64);           // voltage mode compensation for dec 
  xstage.setHoldKVAL(32);          // voltage mode compensation for hold 
  
  ystage.setRunKVAL(64);           // voltage mode compensation for run 
  ystage.setAccKVAL(64);           // voltage mode compensation for acc 
  ystage.setDecKVAL(64);           // voltage mode compensation for dec 
  ystage.setHoldKVAL(32);          // voltage mode compensation for hold 

  zstage.setRunKVAL(64);           // voltage mode compensation for run 
  zstage.setAccKVAL(64);           // voltage mode compensation for acc 
  zstage.setDecKVAL(64);           // voltage mode compensation for dec 
  zstage.setHoldKVAL(32);          // voltage mode compensation for hold 


  xstage.setAccTVAL(32);           // torqval for current mode setup
  xstage.setDecTVAL(32);           // torqval for current mode setup
  xstage.setRunTVAL(32);           // torqval for current mode setup
  xstage.setHoldTVAL(0);           // torqval for current mode setup

  ystage.setAccTVAL(32);           // torqval for current mode setup
  ystage.setDecTVAL(32);           // torqval for current mode setup
  ystage.setRunTVAL(32);           // torqval for current mode setup
  ystage.setHoldTVAL(0);           // torqval for current mode setup

  zstage.setAccTVAL(32);           // torqval for current mode setup
  zstage.setDecTVAL(32);           // torqval for current mode setup
  zstage.setRunTVAL(32);           // torqval for current mode setup
  zstage.setHoldTVAL(0);           // torqval for current mode setup
    

  xstage.setParam(ALARM_EN, 0x8F); // disable ADC UVLO (divider not populated),
  ystage.setParam(ALARM_EN, 0x8F); // disable ADC UVLO (divider not populated),
  zstage.setParam(ALARM_EN, 0x8F); // disable ADC UVLO (divider not populated),
                                   // disable stall detection (not configured),
                                   // disable switch (not using as hard stop)

  xstage.getStatus();              // get status from driver board, this get clears error flags
  ystage.getStatus();              // get status from driver board, this get clears error flags
  zstage.getStatus();              // get status from driver board, this get clears error flags

  delay(25);                       // Insert delay of 10 mSecs
  
  //xstage.softHiZ();              // soft HiZ
  //ystage.softHiZ();              // soft HiZ
  //zstage.softHiZ();              // soft HiZ
 
 
  // select stepper drive mode for higher RPM >120 RPM use current mode
  if(stepper_current_mode)
  {
     xstage.setCurrentMode();             // put driver into current mode
     ystage.setCurrentMode();             // put driver into current mode
     zstage.setCurrentMode();             // put driver into current mode
  }
  else
  {
     xstage.setVoltageMode();             // put driver into voltage mode
     ystage.setVoltageMode();             // put driver into voltage mode
     zstage.setVoltageMode();             // put driver into voltage mode
  }

  xstage.setLoSpdOpt(1); // set low speed optimization for GOTO motion approach
  ystage.setLoSpdOpt(1); // set low speed optimization for GOTO motion approach
  zstage.setLoSpdOpt(1); // set low speed optimization for GOTO motion approach

 
  //xstage.softStop();                               // soft stop prevents errors in the next operation
  //ystage.softStop();                               // soft stop prevents errors in the next operation
  //zstage.softStop();                               // soft stop prevents errors in the next operation

  HEAT_PID.SetSampleTime(PID_SAMPLETIME);            // sets the sampletime of the PID in msecs  (typical 200-100)
  COOL_PID.SetSampleTime(PID_SAMPLETIME);            // sets the sampletime of the PID in msecs  (typical 200-100)
  
  HEAT_PID.SetMode(AUTOMATIC);                       // Set temperature PID  controller to auto and start
  COOL_PID.SetMode(AUTOMATIC);                       // Set temperature PID  controller to auto and start

  if(DBG_MODE == 2)                                  // Init plotter with keys/labels for dataplot
  {
    Serial.begin(115200);                            // Init serial comms with 115K2/8/N/1
    delay(100);   
    //Serial.println("SV_TMP:,PV_TMP:,CV_HEAT:,CV_TEC:,X_SPD:,Y_SPD:,Z_SPD:,");                // Legend/Keys for plotter/chart
    Serial.println("SV_TMP:,PV_TMP:,CV_HEAT:,CV_COOL:,X_SPD:,Y_SPD:,Z_SPD:,");                // Legend/Keys for plotter/chart
    delay(500);                                      // wait 500 mS before commencing otherwise labels will contain sensor data
  } 
  
  delay(50);

  if(SetManualLimits)
  {
    END_POS_X = X_MAN_ENDPOS;                // Holds stage end position (mark) in steps from 0 point, this value is set in ZeroStage()
    END_POS_Y = Y_MAN_ENDPOS;                // Holds stage end position (mark) in steps from 0 point, this value is set in ZeroStage()
    END_POS_Z = Z_MAN_ENDPOS;                // Holds stage end position (mark) in steps from 0 point, this value is set in ZeroStage()                      

    X_INIT_DONE = 1;         // testing only, commnent out for application
    Y_INIT_DONE = 1;         // testing only, commnent out for application
    Z_INIT_DONE = 1;         // testing only, commnent out for application
  }

  if(CHK_OFS_ON_INIT)
  {
      //SET_TEMP_OFFSET();                           // set Thermocouple temp. reading offset
  }
  
  if(DBG_MODE < 2)                                  // only printout when not in plot mode
  {
    Serial.println("");                                                // spacer
    Serial.println("Initialization done, starting control tasks...");  // end of init & start of main loop message
    Serial.println("");                                                // spacer
  }     
  
} // end setup


//************************************************************  UpdateStepper  *******************************************************************************************
// 
// - Reads out position in steps from reference (via  inbuild accumulator)
// - When equal position does not equal target position a goto move is initiated
// - stepper motor actions ar overuled by limit switch, stop/stopmode command or Estop
// - 
// ***********************************************************************************************************************************************************************
void UpdateStepper()  // 
{
  if(UPD_MOT_CNT > UPD_MOT_INTVAL)             // motor update interval check
  {

     XSTAGE_LSU = digitalRead(LSU_X_PIN);             // read state limit switch
     YSTAGE_LSU = digitalRead(LSU_Y_PIN);             // read state limit switch 
     ZSTAGE_LSU = digitalRead(LSU_Z_PIN);             // read state limit switch

     XSTAGE_LSD = digitalRead(LSD_X_PIN);             // read state limit switch
     YSTAGE_LSD = digitalRead(LSD_Y_PIN);             // read state limit switch
     ZSTAGE_LSD = digitalRead(LSD_Z_PIN);             // read state limit switch   

     // TPD_PINSTATE = !TPD_PINSTATE;                    // Toggle, LED STATE 
     // digitalWrite(TPD_PIN, TPD_PINSTATE);             // Override pin state, for debugging purposes
  
     if(XSTAGE_ENABLE)
     {
       CUR_POS_MOT_X = xstage.getPos();          // get position of stepper (via internal step accumulator)
       CUR_MOT_SPD_X = float(OLD_POS_MOT_X - CUR_POS_MOT_X) * float(1000 / UPD_MOT_INTVAL);
       OLD_POS_MOT_X = CUR_POS_MOT_X;           // get position of stepper (via internal step accumulator)
     }
     else
     {
       CUR_POS_MOT_X = 0;
       CUR_MOT_SPD_X = 0;
       OLD_POS_MOT_X = 0;
     }
  
     if(YSTAGE_ENABLE)
     {
       CUR_POS_MOT_Y = ystage.getPos();          // get position of stepper (via internal step accumulator)
       CUR_MOT_SPD_Y = float(OLD_POS_MOT_Y - CUR_POS_MOT_Y) * float(1000 / UPD_MOT_INTVAL); 
       OLD_POS_MOT_Y = CUR_POS_MOT_Y;           // get position of stepper (via internal step accumulator)
     }
     else
     {
       CUR_POS_MOT_Y = 0;
       CUR_MOT_SPD_Y = 0;
       OLD_POS_MOT_Y = 0;
     }

     if(ZSTAGE_ENABLE)
     {
       CUR_POS_MOT_Z = zstage.getPos();          // get position of stepper (via internal step accumulator)
       CUR_MOT_SPD_Z = float(OLD_POS_MOT_Z - CUR_POS_MOT_Z) * float(1000 / UPD_MOT_INTVAL); 
       OLD_POS_MOT_Z = CUR_POS_MOT_Z;           // get position of stepper (via internal step accumulator)  
     }
     else
     {
       CUR_POS_MOT_Z = 0;
       CUR_MOT_SPD_Z = 0;
       OLD_POS_MOT_Z = 0;
     }


     // XSTAGE LIMIT CORRECTION
     if(XSTAGE_ENABLE) // only check limit when stage is available
     {
          // Xstage end point (limit switch) check and corrective action
          if(XSTAGE_DIR == 0 && ((CUR_POS_MOT_X > END_POS_X) || (CUR_POS_MOT_X < 0))) // check in POSITIVE range
          {
              //Serial.print("POS- LIMIT X: ");     // status feedback, only for debug  
              //Serial.println(CUR_POS_MOT_X);      // status feedback, only for debug 
              // xstage.softStop();                 // STOP stage      
              GOTO_X_FLAG       = 0;
              SET_VELO_X        = 0;  
              VELOCITY_X_CMD    = 0;             
             
              if(CUR_POS_MOT_X > END_POS_X)
              { 
                 // xstage.softStop();                // STOP stage 
                 // while(xstage.busyCheck());        // wait untill driver is not busy anymore      
                  xstage.goTo(END_POS_X);             // execute goto      
              }
        
              if(CUR_POS_MOT_X < 0)
              {
                 // xstage.softStop();                  // STOP stage 
                 // while(xstage.busyCheck());          // wait untill driver is not busy anymore   
                  xstage.goTo(0);                       // execute goto      
              } 
             
          }    
      
      
          // Xstage end point (limit switch) check and corrective action
          if(XSTAGE_DIR == 1 && ((CUR_POS_MOT_X > 0) || (CUR_POS_MOT_X < END_POS_X))) // check in NEGATIVE range
          {
              //Serial.print("POS+ LIMIT X: ");     // status feedback, only for debug  
              //Serial.println(CUR_POS_MOT_X);      // status feedback, only for debug 
              
             // xstage.softStop();                  // STOP stage      
              GOTO_X_FLAG       = 0;
              SET_VELO_X        = 0;  
              VELOCITY_X_CMD    = 0;
              
              //while(xstage.busyCheck());            // wait untill driver is not busy anymore 
             
              if(CUR_POS_MOT_X < END_POS_X)
              {
                  xstage.goTo(END_POS_X);       // execute goto      
              }
    
              if(CUR_POS_MOT_X > 0)
              {
                  xstage.goTo(0);               // execute goto      
              } 
           
           } // end - if(XSTAGE_DIR == 1 && ((CUR_POS_MOT_X < 0) || (CUR_POS_MOT_X > END_POS_X))) // check in POSITIVE range

      }  // end -  if(XSTAGE_ENABLE)


     // YSTAGE LIMIT CORRECTION
     if(YSTAGE_ENABLE) // only check limit when stage is available
     {
          // Ystage end point (limit switch) check and corrective action
          if(YSTAGE_DIR == 0 && ((CUR_POS_MOT_Y > END_POS_Y) || (CUR_POS_MOT_Y < 0))) // check in POSITIVE range
          {
              //Serial.print("POS- LIMIT Y: ");     // status feedback, only for debug  
              //Serial.println(CUR_POS_MOT_Y);     // status feedback, only for debug 
              
             // ystage.softStop();                 // STOP stage      
              GOTO_Y_FLAG       = 0;
              SET_VELO_Y        = 0;  
              VELOCITY_Y_CMD    = 0;
              
              //while(ystage.busyCheck());         // wait untill driver is not busy anymore 
             
              if(CUR_POS_MOT_Y > END_POS_Y)
              {
                  ystage.goTo(END_POS_Y);        // execute goto      
              }
        
              if(CUR_POS_MOT_Y < 0)
              {
                  ystage.goTo(0);                // execute goto      
              } 
              
              //while(ystage.busyCheck());         // wait untill driver is not busy anymore  
              //ystage.setMaxSpeed(TOP_SPD_X);     // top speed in units of full steps/s   
          }    
      
      
          // Ystage end point (limit switch) check and corrective action
          if(YSTAGE_DIR ==1 && ((CUR_POS_MOT_Y > 0) || (CUR_POS_MOT_Y < END_POS_Y))) // check in NEGATIVE range
          {
             // Serial.print("POS+ LIMIT Y: ");      // status feedback, only for debug  
             // Serial.println(CUR_POS_MOT_Y);       // status feedback, only for debug 
              
             // ystage.softStop();                   // STOP stage      
              GOTO_Y_FLAG       = 0;
              SET_VELO_Y        = 0;  
              VELOCITY_Y_CMD    = 0;
              
              while(ystage.busyCheck());            // wait untill driver is not busy anymore 
             
              if(CUR_POS_MOT_Y < END_POS_Y)
              {
                  ystage.goTo(END_POS_Y);       // execute goto      
              }
    
              if(CUR_POS_MOT_Y > 0)
              {
                  ystage.goTo(0);               // execute goto      
              }           
              
           
           } // end - if(YSTAGE_DIR == 1 && ((CUR_POS_MOT_Y < 0) || (CUR_POS_MOT_Y > END_POS_Y))) // check in POSITIVE range

      }  // end -  if(YSTAGE_ENABLE)



     // ZSTAGE LIMIT CORRECTION
     if(ZSTAGE_ENABLE) // only check limit when stage is available
     {
          // Zstage end point (limit switch) check and corrective action
          if(ZSTAGE_DIR == 0 && ((CUR_POS_MOT_Z > END_POS_Z) || (CUR_POS_MOT_Z < 0))) // check in POSITIVE range
          {
              //Serial.print("POS- LIMIT Z: ");    // status feedback, only for debug  
              //Serial.println(CUR_POS_MOT_Z);     // status feedback, only for debug 
              
              // zstage.softStop();                 // STOP stage      
              GOTO_Z_FLAG       = 0;
              SET_VELO_Z        = 0;  
              VELOCITY_Z_CMD    = 0;
              
              // while(zstage.busyCheck());         // wait untill driver is not busy anymore 
             
              if(CUR_POS_MOT_Z > END_POS_Z)
              {
                  zstage.goTo(END_POS_Z);        // execute goto      
              }
        
              if(CUR_POS_MOT_Z < 0)
              {
                  zstage.goTo(0);                // execute goto      
              } 
              
              //while(zstage.busyCheck());         // wait untill driver is not busy anymore  
              //zstage.setMaxSpeed(TOP_SPD_Z);     // top speed in units of full steps/s   
          }    
      
      
          // Zstage end point (limit switch) check and corrective action
          if(ZSTAGE_DIR == 1 && ((CUR_POS_MOT_Z < END_POS_Z) || (CUR_POS_MOT_Z > 0))) // check in NEGATIVE range
          {
              // Serial.print("POS+ LIMIT Z: ");      // status feedback, only for debug  
              // Serial.println(CUR_POS_MOT_Z);      // status feedback, only for debug 
              
              // zstage.softStop();                  // STOP stage      
              GOTO_Z_FLAG       = 0;
              SET_VELO_Z        = 0;  
              VELOCITY_Z_CMD    = 0;
              
              //while(zstage.busyCheck());        // wait untill driver is not busy anymore 
        
              if(ZSTAGE_DIR == 1)
              {
                  if(CUR_POS_MOT_Z < END_POS_Z)
                  {
                      zstage.goTo(END_POS_Z);       // execute goto      
                  }
        
                  if(CUR_POS_MOT_Z > 0)
                  {
                      zstage.goTo(0);               // execute goto      
                  }           
              } 
           
           } // end - if(ZSTAGE_DIR == 1 && ((CUR_POS_MOT_Z < 0) || (CUR_POS_MOT_Z > END_POS_Z))) // check in POSITIVE range

     }  // end -  if(ZSTAGE_ENABLE) 
    
     
     // -----------------   STOP motor(s) when RUNMODE is in STOP  ------------------------------------------------
     if(RUNMODE == 0)                           // stop motor if runmode is zero
     {
        if((CUR_MOT_SPD_X > 0) && (XSTAGE_ENABLE == 1))
        {
           xstage.softStop();                   // STOP stage
        }
  
        if((CUR_MOT_SPD_Y > 0) && (YSTAGE_ENABLE == 1))
        {
           ystage.softStop();                   // STOP stage
        }
  
        if((CUR_MOT_SPD_Z > 0) && (ZSTAGE_ENABLE == 1))
        {
           zstage.softStop();                   // STOP stage
        }  
       
         GOTO_X_FLAG = 0;                       // RESET GOTO flag   
         GOTO_Y_FLAG = 0;                       // RESET GOTO flag   
         GOTO_Z_FLAG = 0;                       // RESET GOTO flag  
          
         //GOTO_TARGET = 0;                     // RESET GOTO flag 
         Target_Position_X = 0;                 // RESET value 
         Target_Position_Y = 0;                 // RESET value 
         Target_Position_Z = 0;                 // RESET value 
         
         VELOCITY_X_CMD = 0;                    // RESET value 
         VELOCITY_Y_CMD = 0;                    // RESET value 
         VELOCITY_Z_CMD = 0;                    // RESET value 
     }    


   //  ---------------------     GOTO motion X/Y/Z  ---------------------------------

   
     //  X-STAGE - NORMAL SPEED GOTO
     if((Target_Position_X != CUR_POS_MOT_X) && (GOTO_X_FLAG == 1) && (XSTAGE_ENABLE == 1) )  // check current vs target position ==> not equal then do a goto command
     {  
        //  X-STAGE - NORMAL SPEED GOTO
        if(SPEED_MODE_X == 1)
        {
            if(xstage.busyCheck()!= 1)
            {  
                //xstage.setMaxSpeed(TOP_SPD);                  // top speed in units of full steps/s 
                xstage.goTo(Target_Position_X);                 // execute goto
                GOTO_X_FLAG = 0;
                VELOCITY_X_CMD = 0;
            }             
        }

        
        //  X-STAGE - SLOWSPEED GOTO
        if((SPEED_MODE_X == 0) && (GOTO_X_FLAG == 1))
        {
            TARGET_DIST_X = CUR_POS_MOT_X - Target_Position_X; // in steps
            
            //Serial.print("TDX: ");                             // status feedback, only for debug  
            //Serial.println(TARGET_DIST_X);                     // status feedback, only for debug            

            if((TARGET_DIST_X > 25) && (X_APR_STATE == 1)) 
            {
               xstage.run(REV, JOG_STEP_SIZE_X);
               X_APR_STATE = 2; 
               //Serial.print("APP CHANGE: ");                    // status feedback, only for debug  
               //Serial.println(X_APR_STATE);                     // status feedback, only for debug 
            }

            if((TARGET_DIST_X < -25) && (X_APR_STATE == 1)) 
            {
               xstage.run(FWD, JOG_STEP_SIZE_X);
               X_APR_STATE = 2;  
               //Serial.print("APP CHANGE: ");                    // status feedback, only for debug  
               //Serial.println(X_APR_STATE);                     // status feedback, only for debug  
            }

            if((TARGET_DIST_X > 2) && (TARGET_DIST_X < 25) && (X_APR_STATE == 2)) 
            {
               xstage.softStop(); 
               X_APR_STATE = 3; 
               //Serial.print("APP CHANGE: ");                    // status feedback, only for debug  
               //Serial.println(X_APR_STATE);                     // status feedback, only for debug 
            }

            if((TARGET_DIST_X > -25) && (TARGET_DIST_X < 2) && (X_APR_STATE == 2)) 
            {
               xstage.softStop(); 
               X_APR_STATE = 3; 
               //Serial.print("APP CHANGE: ");                      // status feedback, only for debug  
               //Serial.println(X_APR_STATE);                       // status feedback, only for debug  
            }


            if((TARGET_DIST_X > 0) && (X_APR_STATE == 3))
            {   
               while(xstage.busyCheck());                         // wait untill driver is not busy anymore
               xstage.move(REV, 1); 

               if (TARGET_DIST_X == 1)
               {                 
                   X_APR_STATE = 4;  
                   //Serial.print("APP CHANGE: ");                  // status feedback, only for debug  
                   //Serial.println(X_APR_STATE);                   // status feedback, only for debug 
                   GOTO_X_FLAG == 0;
                   //Serial.println("TARGET_DIST_X = 0, stepper stopped...");         // status feedback
                   //Serial.println(MOVE_TMR_X);                    // status feedback
               }
            }

            if((TARGET_DIST_X < 0) && (X_APR_STATE == 3))
            {   
               while(xstage.busyCheck());                         // wait untill driver is not busy anymore
               xstage.move(FWD, 1); 
  
               if(TARGET_DIST_X == -1)
               {                  
                   X_APR_STATE = 4; 
                   //Serial.print("APP CHANGE: ");                   // status feedback, only for debug  
                   //Serial.println(X_APR_STATE);                    // status feedback, only for debug 
                   GOTO_X_FLAG == 0;
                   //Serial.println("TARGET_DIST_X = 0, stepper stopped...");         // status feedback
                   //Serial.println(MOVE_TMR_X);         // status feedback 
               }             
            }   
            
        }   // if((SPEED_MODE == 0) && (GOTO_X_FLAG == 1))    
        
     }      // if((Target_Position_X != CUR_POS_MOT_X) && (GOTO_X_FLAG == 1))




     //  Y-STAGE - NORMAL SPEED GOTO
     if((Target_Position_Y != CUR_POS_MOT_Y) && (GOTO_Y_FLAG == 1) && (YSTAGE_ENABLE == 1) )  // check current vs target position ==> not equal then do a goto command
     {                  

        //  Y-STAGE - NORMAL SPEED GOTO
        if(SPEED_MODE_Y == 1)
        {
            if(ystage.busyCheck()!= 1)
            {  
                //ystage.setMaxSpeed(TOP_SPD);                  // top speed in units of full steps/s 
                ystage.goTo(Target_Position_Y);                 // execute goto
                GOTO_Y_FLAG = 0;
                VELOCITY_Y_CMD = 0;                
            }             
        }

        
        //  Y-STAGE - SLOWSPEED GOTO
        if((SPEED_MODE_Y == 0) && (GOTO_Y_FLAG == 1))
        {
            TARGET_DIST_Y = CUR_POS_MOT_Y - Target_Position_Y; // in steps

            
            //Serial.print("TDY: ");                             // status feedback, only for debug 
            //Serial.println(TARGET_DIST_Y);                     // status feedback, only for debug        
  
            ERR_LEDSTATE = !ERR_LEDSTATE;                      // Toggle, LED STATE 
            digitalWrite(TPD_PIN, ERR_LEDSTATE);               //  Override pin state, for debugging purposes  

            if((TARGET_DIST_Y > 25) && (Y_APR_STATE == 1)) 
            {
               ystage.run(REV, JOG_STEP_SIZE_Y);
               Y_APR_STATE = 2; 
               //Serial.print("APP CHANGE: ");                    // status feedback, only for debug  
               //Serial.println(Y_APR_STATE);                     // status feedback, only for debug 
            }

            if((TARGET_DIST_Y < -25) && (Y_APR_STATE == 1)) 
            {
               ystage.run(FWD, JOG_STEP_SIZE_Y);
               Y_APR_STATE = 2;  
               //Serial.print("APP CHANGE: ");                    // status feedback, only for debug  
               //Serial.println(Y_APR_STATE);                     // status feedback, only for debug  
            }

            if((TARGET_DIST_Y > 2) && (TARGET_DIST_Y < 25) && (Y_APR_STATE == 2)) 
            {
               ystage.softStop(); 
               Y_APR_STATE = 3; 
               //Serial.print("APP CHANGE: ");                    // status feedback, only for debug  
               //Serial.println(Y_APR_STATE);                     // status feedback, only for debug 
            }

            if((TARGET_DIST_Y > -25) && (TARGET_DIST_Y < 2) && (Y_APR_STATE == 2)) 
            {
               ystage.softStop(); 
               Y_APR_STATE = 3; 
               //Serial.print("APP CHANGE: ");                    // status feedback, only for debug  
               //Serial.println(Y_APR_STATE);                     // status feedback, only for debug  
            }


            if((TARGET_DIST_Y > 0) && (Y_APR_STATE == 3))
            {   
               while(ystage.busyCheck());                       // wait untill driver is not busy anymore
               ystage.move(REV, 1); 

               if (TARGET_DIST_Y == 1)
               {                 
                   Y_APR_STATE = 4;  
                   //Serial.print("APP CHANGE: ");                 // status feedback, only for debug  
                   //Serial.println(Y_APR_STATE);                  // status feedback, only for debug 
                   GOTO_Y_FLAG == 0;
                   //Serial.println("TARGET_DIST_Y = 0, stepper stopped...");         // status feedback
                   //Serial.println(MOVE_TMR_Y);                    // status feedback
               }
            }

            if((TARGET_DIST_Y < 0) && (Y_APR_STATE == 3))
            {   
               while(ystage.busyCheck());                         // wait untill driver is not busy anymore
               ystage.move(FWD, 1); 
  
               if(TARGET_DIST_Y == -1)
               {                  
                   Y_APR_STATE = 4; 
                   //Serial.print("APP CHANGE: ");                  // status feedback, only for debug  
                   //Serial.println(Y_APR_STATE);                   // status feedback, only for debug 
                   GOTO_Y_FLAG == 0;
                   //Serial.println("TARGET_DIST_Y = 0, stepper stopped...");         // status feedback
                   //Serial.println(MOVE_TMR_Y);         // status feedback 
               }             
            }   
            
        }   // if((SPEED_MODE == 0) && (GOTO_Y_FLAG == 1))    
        
     }    // if((Target_Position_Y != CUR_POS_MOT_Y) && (GOTO_Y_FLAG == 1))




       //  Z-STAGE - NORMAL SPEED GOTO
     if((Target_Position_Z != CUR_POS_MOT_Z) && (GOTO_Z_FLAG == 1) && (ZSTAGE_ENABLE == 1) )  // check current vs target position ==> not equal then do a goto command
     {                  

        //  X-STAGE - NORMAL SPEED GOTO
        if(SPEED_MODE_Z == 1)
        {
            if(zstage.busyCheck()!= 1)
            {  
                //zstage.setMaxSpeed(TOP_SPD_Z);                  // top speed in units of full steps/s 
                zstage.goTo(Target_Position_Z);               // execute goto
                GOTO_Z_FLAG = 0;
                VELOCITY_Z_CMD = 0;
            }             
        }

        
        //  Z-STAGE - SLOWSPEED GOTO
        if((SPEED_MODE_Z == 0) && (GOTO_Z_FLAG == 1))
        {
            TARGET_DIST_Z = CUR_POS_MOT_Z - Target_Position_Z; // in steps
            
            //Serial.print("TDZ: ");                             // status feedback, only for debug 
            //Serial.println(TARGET_DIST_Z);                     // status feedback, only for debug 
  
            ERR_LEDSTATE = !ERR_LEDSTATE;                  // Toggle, LED STATE 
            digitalWrite(TPD_PIN, ERR_LEDSTATE);           //  Override pin state, for debugging purposes  

            if((TARGET_DIST_Z > 25) && (Z_APR_STATE == 1)) 
            {
               zstage.run(REV, JOG_STEP_SIZE_Z);
               Z_APR_STATE = 2; 
               //Serial.print("APP CHANGE: ");                     // status feedback, only for debug  
               //Serial.println(Z_APR_STATE);                     // status feedback, only for debug 
            }

            if(TARGET_DIST_Z < -25 && ((Z_APR_STATE == 1))) 
            {
               zstage.run(FWD, JOG_STEP_SIZE_Z);
               Z_APR_STATE = 2;  
               //Serial.print("APP CHANGE: ");                     // status feedback, only for debug  
               //Serial.println(Z_APR_STATE);                     // status feedback, only for debug  
            }

            if((TARGET_DIST_Z > 2) && (TARGET_DIST_Z < 25) && (Z_APR_STATE == 2)) 
            {
               zstage.softStop(); 
               Z_APR_STATE = 3; 
               //Serial.print("APP CHANGE: ");                     // status feedback, only for debug  
               //Serial.println(Z_APR_STATE);                     // status feedback, only for debug 
            }

            if((TARGET_DIST_Z > -25) && (TARGET_DIST_Z < 2) && (Z_APR_STATE == 2)) 
            {
               zstage.softStop(); 
               Z_APR_STATE = 3; 
               //Serial.print("APP CHANGE: ");                     // status feedback, only for debug  
               //Serial.println(Z_APR_STATE);                     // status feedback, only for debug  
            }


            if((TARGET_DIST_Z > 0) && (Z_APR_STATE == 3))
            {   
               while(zstage.busyCheck());                  // wait untill driver is not busy anymore
               zstage.move(REV, 1); 

               if (TARGET_DIST_Z == 1)
               {                 
                   Z_APR_STATE = 4;  
                   //Serial.print("APP CHANGE: ");                     // status feedback, only for debug  
                   //Serial.println(Z_APR_STATE);                     // status feedback, only for debug 
                   GOTO_Z_FLAG == 0;
                   //Serial.println("TARGET_DIST_Z = 0, stepper stopped...");         // status feedback
                   //Serial.println(MOVE_TMR_Z);         // status feedback
               }
            }

            if((TARGET_DIST_Z < 0) && (Z_APR_STATE == 3))
            {   
               while(zstage.busyCheck());                  // wait untill driver is not busy anymore
               zstage.move(FWD, 1); 
  
               if (TARGET_DIST_Z == -1)
               {                  
                   Z_APR_STATE = 4; 
                   //Serial.print("APP CHANGE: ");                     // status feedback, only for debug  
                   //Serial.println(Z_APR_STATE);                     // status feedback, only for debug 
                   GOTO_Z_FLAG == 0;
                   //Serial.println("TARGET_DIST_Z = 0, stepper stopped...");         // status feedback
                   //Serial.println(MOVE_TMR_Z);         // status feedback 
               }             
            }   
            
        }   // if((SPEED_MODE == 0) && (GOTO_Z_FLAG == 1))    
        
     } // if((Target_Position_Z != CUR_POS_MOT_Z) && (GOTO_Z_FLAG == 1))


      // LEDS/SIGNALING
      if(CUR_MOT_SPD_X == 0)
      {
        digitalWrite(XSTAGE_LED, LOW);                  //  TURN ON MOTOR LED
      }
      else
      {
        digitalWrite(XSTAGE_LED, HIGH);                 //  TURN ON MOTOR LED
      }
  
      if(CUR_MOT_SPD_Y == 0)
      {
        digitalWrite(YSTAGE_LED, LOW);                  //  TURN ON MOTOR LED
      }
      else
      {
        digitalWrite(YSTAGE_LED, HIGH);                 //  TURN ON MOTOR LED
      }
  
      if(CUR_MOT_SPD_Z == 0)
      {
        digitalWrite(ZSTAGE_LED, LOW);                  //  TURN ON MOTOR LED
      }
      else
      {
        digitalWrite(ZSTAGE_LED, HIGH);                 //  TURN ON MOTOR LED
      }
  
       UPD_MOT_CNT = 0;
     
       //TPD_PINSTATE = !TPD_PINSTATE;                  // Toggle, LED STATE 
       //digitalWrite(TPD_PIN, TPD_PINSTATE);           //  Override pin state, for debugging purposes
  }   
}





//************************************************************  ZERO STAGE  *******************************************************************************************
// - Moves stage until upper limit switch is closed then stop.
// - The stage then moves back down to open switch up.
// - When switch has opened up, stepper motor position accumulator is reset to 0. 
// - Stage is then driven to the home position (0).
// - All "HOMING" moves after zero-ing will always go to '0' position and not move till limit switch closes.
// ********************************************************************************************************************************************************************

void ZeroStage()                                // Usually only called once per startup
{   
   if(DBG_MODE < 2)                             // only print when plotter is off
   {
      Serial.println("Zero-ing stages...");     // status feedback
   }   

    xstage.getStatus();              // get status from driver board, this get clears error flags
    ystage.getStatus();              // get status from driver board, this get clears error flags
    zstage.getStatus();              // get status from driver board, this get clears error flags

    xstage.setMaxSpeed(SET_SPD_X);    // max speed in units of full steps/s 
    ystage.setMaxSpeed(SET_SPD_Y);    // max speed in units of full steps/s 
    zstage.setMaxSpeed(SET_SPD_Z);    // max speed in units of full steps/s 

    delay(10);

    // ZERO and MARK STAGES 

    // ----------------   ZERO and MARK Y-STAGE   --------------------------------
      if(YSTAGE_ENABLE)
      {
          while((!Y_INIT_DONE))
          {    
              if(INIT_Y_STAGE == 0)
              {
                  if(YSTAGE_DIR == 0)
                  {
                      while(ystage.busyCheck());                  // board not busy check
                      ystage.run(REV,MOT_ZERO_SPD);
                      INIT_Y_STAGE = 1;
                      //Serial.println("STATE CHANGE to 1");       // status feedback, only for debug  
                  }
                  else
                  {
                      while(ystage.busyCheck());                  // board not busy check
                      ystage.run(FWD,MOT_ZERO_SPD);
                      INIT_Y_STAGE = 1;   
                      //Serial.println("STATE CHANGE to 1");       // status feedback, only for debug 
                  }

                  digitalWrite(YSTAGE_LED, HIGH);          //  TURN ON MOTOR LED      
               }    
    
              YSTAGE_LSU = digitalRead(LSU_Y_PIN);  // check state of limit switch
              YSTAGE_LSD = digitalRead(LSD_Y_PIN);  // check state of limit switch
              
              //Serial.print("XSTAGE_LSU: ");             // status feedback, only for debug  
              //Serial.println(XSTAGE_LSU);               // status feedback, only for debug   
              //Serial.print("XSTAGE_LSD: ");             // status feedback, only for debug  
              //Serial.println(XSTAGE_LSD);               // status feedback, only for debug   
               
              delay(10);
    
    
              if((YSTAGE_LSU == 1) && (INIT_Y_STAGE == 1))
              {
                INI_Y_CNT++;
               
                //Serial.print("INI_X_CNT: ");             // status feedback, only for debug  
                //Serial.println(INI_X_CNT);               // status feedback, only for debug 
    
                if(INI_Y_CNT > 3 &&  (INIT_Y_STAGE == 1) )
                {
                    ystage.softStop();                     // Limit switch engaged, STOP stage
                    
                    INIT_Y_STAGE = 2;
                    //Serial.println("STATE CHANGE to 2");   // status feedback, only for debug 
                    
    
                    if(YSTAGE_DIR == 0)
                    {
                      ystage.move(FWD,MOT_ZERO_SPD);  
                      while(ystage.busyCheck());                    // board not busy check 
                      ystage.resetPos();

                      if(SetManualLimits == 0)
                      {
                          while(ystage.busyCheck());                    // board not busy check 
                          ystage.run(FWD,MOT_ZERO_SPD);
                          INIT_Y_STAGE = 3; 
                      }
                      else
                      {
                          Y_INIT_DONE  = 1;
                          INIT_Y_STAGE = 0; 
                      }
                     
                    }
                    else
                    {
                      ystage.move(REV,MOT_ZERO_SPD); 
                      while(ystage.busyCheck());                    // board not busy check 
                      ystage.resetPos(); 

                      if(SetManualLimits == 0)
                      {
                        while(ystage.busyCheck());                    // board not busy check 
                        ystage.run(REV,MOT_ZERO_SPD);
                        INIT_Y_STAGE = 3; 
                      }
                      else
                      {
                          Y_INIT_DONE  = 1;
                          INIT_Y_STAGE = 0; 
                      }
                      
                    } 

                    ystage.move(FWD, Y_CENTER_POS);
                    while(ystage.busyCheck());
                   // Serial.println("STATE CHANGE to 3");             // status feedback, only for debug  
                    
                    INI_Y_CNT  =0;            
                }
              }
              else
              {
                  if((YSTAGE_LSU == 0) && (INIT_Y_STAGE == 1))
                  {
                    INI_Y_CNT  = 0;     // reset accumulator count
                  }
              }

             
                 
    
              if((YSTAGE_LSD == 1) && (INIT_Y_STAGE == 3) && (SetManualLimits == 0))
              {
                  INI_Y_CNT++;
      
                  if(INI_Y_CNT > 3 && (INIT_Y_STAGE == 3) )
                  {
                      ystage.softStop();                     // Limit switch engaged, STOP stage
                      
                      INIT_Y_STAGE = 4;                               // increment stage
    
                     //Serial.println("STATE CHANGE to 4");          // status feedback, only for debug
      
                      if(YSTAGE_DIR == 0)
                      {
                        ystage.move(REV,MOT_ZERO_SPD);  
                        while(ystage.busyCheck());                    // board not busy check 
                        END_POS_Y =  ystage.getPos();  
                        while(ystage.busyCheck());                    // board not busy check 
                        ystage.goTo(Y_CENTER_POS);
                        while(ystage.busyCheck());
                      }
                      else
                      {
                        ystage.move(FWD,MOT_ZERO_SPD);  
                        while(ystage.busyCheck());                    // board not busy check 
                        END_POS_Y =  ystage.getPos(); 
                        while(ystage.busyCheck());                    // board not busy check 
                        ystage.goTo(Y_CENTER_POS);  // Move to center);
                        while(ystage.busyCheck());
                      } 
                      
                      INIT_Y_STAGE = 5; 
                      
                      //Serial.println("STATE CHANGE to 5");          // status feedback, only for debug 
                  
                      Y_INIT_DONE  = 1;
                      INI_Y_CNT    = 0; 
                      INIT_Y_STAGE = 0;                 
                  }
               }
               else
               {
                  if((YSTAGE_LSD == 0) && (INIT_Y_STAGE == 3))
                  {
                    INI_Y_CNT = 0;     //   reset                    
                  }
               }
                                      
           }
           
          Serial.print("ENDPOS Y: ");                       // status feedback, only for debug  
          Serial.println(END_POS_Y);                        // status feedback, only for debug  
          //Serial.println("ZERO-MARK Y done...");            // status feedback, only for debug 
          while(ystage.busyCheck());                    // board not busy check 
          digitalWrite(YSTAGE_LED, LOW);                    //  TURN OFF MOTOR LED
      
      
      }   // if(XSTAGE_ENABLE)
      else // in case no stage set flag hi
      {
        Y_INIT_DONE = 1;
        while(ystage.busyCheck());                    // board not busy check 
        digitalWrite(YSTAGE_LED, LOW);                      //  TURN OFF MOTOR LED
      } 


      // ----------------   ZERO and MARK X-STAGE   --------------------------------
      if(XSTAGE_ENABLE)
      {
          while((!X_INIT_DONE))
          {    
              if(INIT_X_STAGE == 0)
              {
                  if(XSTAGE_DIR == 0)
                  {
                      while(xstage.busyCheck());                  // board not busy check
                      xstage.run(REV,MOT_ZERO_SPD);
                      INIT_X_STAGE = 1;
                      //Serial.print("Motor zero speed X :");
                      //Serial.println(MOT_ZERO_SPD);       // status feedback, only for debug  
                  }
                  else
                  {
                      while(xstage.busyCheck());                  // board not busy check
                      xstage.run(FWD,MOT_ZERO_SPD);
                      INIT_X_STAGE = 1;   
                      //Serial.println("STATE CHANGE to 1");       // status feedback, only for debug 
                  }

                  digitalWrite(XSTAGE_LED, HIGH);          //  TURN ON MOTOR LED      
               }    
    
              XSTAGE_LSU = digitalRead(LSU_X_PIN);  // check state of limit switch
              XSTAGE_LSD = digitalRead(LSD_X_PIN);  // check state of limit switch
              
              //Serial.print("XSTAGE_LSU: ");             // status feedback, only for debug  
              //Serial.println(XSTAGE_LSU);               // status feedback, only for debug   
              //Serial.print("XSTAGE_LSD: ");             // status feedback, only for debug  
              //Serial.println(XSTAGE_LSD);               // status feedback, only for debug   
               
              delay(10);
    
              if((XSTAGE_LSU == 1) && (INIT_X_STAGE == 1))
              {
                INI_X_CNT++;
               
                //Serial.print("INI_X_CNT: ");             // status feedback, only for debug  
                //Serial.println(INI_X_CNT);               // status feedback, only for debug 
    
                if(INI_X_CNT > 3 &&  (INIT_X_STAGE == 1) )
                {
                    xstage.softStop();                     // Limit switch engaged, STOP stage
                    
                    INIT_X_STAGE = 2;
                    //Serial.println("STATE CHANGE to 2");   // status feedback, only for debug 
                    
    
                    if(XSTAGE_DIR == 0)
                    {
                      xstage.move(FWD,MOT_ZERO_SPD);  
                      while(xstage.busyCheck());                    // board not busy check 
                      xstage.resetPos();

                      if(SetManualLimits == 0)
                      {
                          while(xstage.busyCheck());                    // board not busy check 
                          xstage.run(FWD,MOT_ZERO_SPD);
                          INIT_X_STAGE = 3; 
                      }
                      else
                      {
                          X_INIT_DONE  = 1;
                          INIT_X_STAGE = 0; 
                      }
                     
                    }
                    else
                    {
                      xstage.move(REV,MOT_ZERO_SPD); 
                      while(xstage.busyCheck());                    // board not busy check 
                      xstage.resetPos(); 

                      if(SetManualLimits == 0)
                      {
                        while(xstage.busyCheck());                    // board not busy check 
                        xstage.run(REV,MOT_ZERO_SPD);
                        INIT_X_STAGE = 3; 
                      }
                      else
                      {
                          X_INIT_DONE  = 1;
                          INIT_X_STAGE = 0; 
                      }
                      
                    } 
    
                    xstage.move(FWD, X_CENTER_POS);
                    while(xstage.busyCheck());
                   // Serial.println("STATE CHANGE to 3");             // status feedback, only for debug  
                    
                    INI_X_CNT  =0;            
                }
              }
              else
              {
                  if((XSTAGE_LSU == 0) && (INIT_X_STAGE == 1))
                  {
                    INI_X_CNT  = 0;     // reset accumulator count
                  }
              }

             
                 
    
              if((XSTAGE_LSD == 1) && (INIT_X_STAGE == 3) && (SetManualLimits == 0))
              {
                  INI_X_CNT++;
      
                  if(INI_X_CNT > 3 && (INIT_X_STAGE == 3) )
                  {
                      xstage.softStop();                     // Limit switch engaged, STOP stage
                      
                      INIT_X_STAGE = 4;                               // increment stage
    
                     //Serial.println("STATE CHANGE to 4");          // status feedback, only for debug
      
                      if(XSTAGE_DIR == 0)
                      {
                        xstage.move(REV,MOT_ZERO_SPD);  
                        while(xstage.busyCheck());                    // board not busy check 
                        END_POS_X =  xstage.getPos();  
                        while(xstage.busyCheck());                    // board not busy check 
                        xstage.goTo(X_CENTER_POS);
                        while(xstage.busyCheck());
                      }
                      else
                      {
                        xstage.move(FWD,MOT_ZERO_SPD);  
                        while(xstage.busyCheck());                    // board not busy check 
                        END_POS_X =  xstage.getPos(); 
                        while(xstage.busyCheck());                    // board not busy check 
                        xstage.goTo(X_CENTER_POS);
                        while(xstage.busyCheck());
                      } 
                      
                      INIT_X_STAGE = 5; 
                      
                      //Serial.println("STATE CHANGE to 5");          // status feedback, only for debug 
                  
                      X_INIT_DONE  = 1;
                      INI_X_CNT    = 0; 
                      INIT_X_STAGE = 0;                 
                  }
               }
               else
               {
                  if((XSTAGE_LSD == 0) && (INIT_X_STAGE == 3))
                  {
                    INI_X_CNT = 0;     //   reset                    
                  }
               }
                                      
           }
           
          Serial.print("ENDPOS X: ");                       // status feedback, only for debug  
          Serial.println(END_POS_X);                        // status feedback, only for debug  
          //Serial.println("ZERO-MARK X done...");            // status feedback, only for debug 
          while(xstage.busyCheck());                    // board not busy check 
          digitalWrite(XSTAGE_LED, LOW);                    //  TURN OFF MOTOR LED
      
      
      }   // if(XSTAGE_ENABLE)
      else // in case no stage set flag hi
      {
        X_INIT_DONE = 1;
        while(xstage.busyCheck());                    // board not busy check 
        digitalWrite(XSTAGE_LED, LOW);                      //  TURN OFF MOTOR LED
      } 

   // ----------------   ZERO and MARK Z-STAGE   --------------------------------
  if(ZSTAGE_ENABLE)
  {
      while((!Z_INIT_DONE))
      {    
          if(INIT_Z_STAGE == 0)
          {
              if(ZSTAGE_DIR == 0)
              {
                  while(zstage.busyCheck());                  // board not busy check
                  zstage.run(REV,MOT_ZERO_SPD);
                  INIT_Z_STAGE = 1;
                  //Serial.println("STATE CHANGE to 1");       // status feedback, only for debug  
              }
              else
              {
                  while(zstage.busyCheck());                  // board not busy check
                  zstage.run(FWD,MOT_ZERO_SPD);
                  INIT_Z_STAGE = 1;   
                  //Serial.println("STATE CHANGE to 1");       // status feedback, only for debug 
              }

              digitalWrite(ZSTAGE_LED, HIGH);          //  TURN ON MOTOR LED      
           }    

          ZSTAGE_LSU = digitalRead(LSU_Z_PIN);  // check state of limit switch
          ZSTAGE_LSD = digitalRead(LSD_Z_PIN);  // check state of limit switch
          
          //Serial.print("XSTAGE_LSU: ");             // status feedback, only for debug  
          //Serial.println(XSTAGE_LSU);               // status feedback, only for debug   
          //Serial.print("XSTAGE_LSD: ");             // status feedback, only for debug  
          //Serial.println(XSTAGE_LSD);               // status feedback, only for debug   
           
          //delay(50);


          if((ZSTAGE_LSU == 1) && (INIT_Z_STAGE == 1))
          {
            INI_Z_CNT++;
           
            //Serial.print("INI_X_CNT: ");             // status feedback, only for debug  
            //Serial.println(INI_X_CNT);               // status feedback, only for debug 

            if(INI_Z_CNT > 3 &&  (INIT_Z_STAGE == 1) )
            {
                zstage.softStop();                     // Limit switch engaged, STOP stage
                
                INIT_Z_STAGE = 2;
                //Serial.println("STATE CHANGE to 2");   // status feedback, only for debug 
                

                if(ZSTAGE_DIR == 0)
                {
                  zstage.move(FWD,MOT_ZERO_SPD);  
                  while(zstage.busyCheck());                    // board not busy check 
                  zstage.resetPos();

                  if(SetManualLimits == 0)
                  {
                      while(zstage.busyCheck());                    // board not busy check 
                      zstage.run(FWD,MOT_ZERO_SPD);
                      INIT_Z_STAGE = 3; 
                  }
                  else
                  {
                      Z_INIT_DONE  = 1;
                      INIT_Z_STAGE = 0; 
                  }
                 
                }
                else
                {
                  zstage.move(REV,MOT_ZERO_SPD); 
                  while(zstage.busyCheck());                    // board not busy check 
                  zstage.resetPos(); 

                  if(SetManualLimits == 0)
                  {
                    while(zstage.busyCheck());                    // board not busy check 
                    zstage.run(REV,MOT_ZERO_SPD);
                    INIT_Z_STAGE = 3; 
                  }
                  else
                  {
                      Z_INIT_DONE  = 1;
                      INIT_Z_STAGE = 0; 
                  }
                  
                } 

               // Serial.println("STATE CHANGE to 3");             // status feedback, only for debug  
                
                INI_Z_CNT  =0;            
            }
          }
          else
          {
              if((ZSTAGE_LSU == 0) && (INIT_Z_STAGE == 1))
              {
                INI_Z_CNT  = 0;     // reset accumulator count
              }
          }

         
             

          if((ZSTAGE_LSD == 1) && (INIT_Z_STAGE == 3) && (SetManualLimits == 0))
          {
              INI_Z_CNT++;
  
              if(INI_Z_CNT > 3 && (INIT_Z_STAGE == 3) )
              {
                  zstage.softStop();                     // Limit switch engaged, STOP stage
                  
                  INIT_Z_STAGE = 4;                               // increment stage

                 //Serial.println("STATE CHANGE to 4");          // status feedback, only for debug
  
                  if(ZSTAGE_DIR == 0)
                  {
                    zstage.move(REV,MOT_ZERO_SPD);  
                    while(zstage.busyCheck());                    // board not busy check 
                    END_POS_Z =  zstage.getPos();  
                    while(zstage.busyCheck());                    // board not busy check 
                    zstage.goTo(0);
                  }
                  else
                  {
                    zstage.move(FWD,MOT_ZERO_SPD);  
                    while(zstage.busyCheck());                    // board not busy check 
                    END_POS_Z =  zstage.getPos(); 
                    while(zstage.busyCheck());                    // board not busy check 
                    zstage.goTo(0);
                  } 
                  
                  INIT_Z_STAGE = 5; 
                  
                  //Serial.println("STATE CHANGE to 5");          // status feedback, only for debug 
              
                  Z_INIT_DONE  = 1;
                  INI_Z_CNT    = 0; 
                  INIT_Z_STAGE = 0;                 
              }
           }
           else
           {
              if((ZSTAGE_LSD == 0) && (INIT_Z_STAGE == 3))
              {
                INI_Z_CNT = 0;     //   reset                    
              }
           }
                                  
       }
       
      Serial.print("ENDPOS Z: ");                       // status feedback, only for debug  
      Serial.println(END_POS_Z);                        // status feedback, only for debug  
      //Serial.println("ZERO-MARK Z done...");          // status feedback, only for debug 
      while(zstage.busyCheck());                        // board not busy check 
      digitalWrite(ZSTAGE_LED, LOW);                    //  TURN OFF MOTOR LED
  
  
  }   // if(XSTAGE_ENABLE)
  else // in case no stage set flag hi
  {
    Z_INIT_DONE = 1;
    while(zstage.busyCheck());                          // board not busy check 
    digitalWrite(ZSTAGE_LED, LOW);                      //  TURN OFF MOTOR LED
  }    
      


   xstage.setMaxSpeed(SET_SPD_X);    // max speed in units of full steps/s 
   ystage.setMaxSpeed(SET_SPD_Y);    // max speed in units of full steps/s 
   zstage.setMaxSpeed(SET_SPD_Z);    // max speed in units of full steps/s    


   xstage.getStatus();              // get status from driver board, this get clears error flags
   ystage.getStatus();              // get status from driver board, this get clears error flags
   zstage.getStatus();              // get status from driver board, this get clears error flags

   if(DBG_MODE == 1)                                    // only print when plotter is off
   {
      Serial.println();                                 // status feedback
      Serial.println("Zero-ing stages completed...");   // status feedback
   }    
    
}// end ZeroStage



// *********************************************************   SET_TEMP_OFFSET      ***************************************************************************************
//
//  - Initialize thermocouple and PT100
//  - Fill up oversample Thermocouple ADC oversample accumulator with values
//  - Warm up IIR filter and cycle to settle readings 
//  - PT100 & TC read 256x
//  - Use averaged PT100 readings of ambient temperature to determine offset of Thermocouple
//  - Calculate difference of both temps and insert this value into the OS_TEMP (temp offset) value and store into eeprom
// ***********************************************************************************************************************************************************************
void SET_TEMP_OFFSET() //  1 time call from setup
{
  int CYC_CNT         = 0;
  int SAMPLE_INTERVAL = 25;
  CHK_RTD             = 1;
  UPD_TCR_CNT         = TCR_INTVAL + 1;
  UPD_RTD_CNT         = UPD_RTD_INTVAL + 1;
  MSEC_CNT            = 0;
  RTD_ERR             = 0;
    

  if(DBG_MODE == 1) // only printout when not in plot mode
  {
    Serial.print("start thermocouple offset compensation, time marker (mSec): ");        // start stopwatch (in msecs)
    Serial.println(MSEC_CNT);          // send requested data 
  }
  
  while((CYC_CNT < TC_OS_SIZE) && (RTD_ERR == 0))
  {
    ReadTemperature(); 
    //delay(35);  
    CYC_CNT++;   
    //UPD_TCR_CNT = TCR_INTVAL + 1;
    //UPD_RTD_CNT = UPD_RTD_INTVAL + 1;
    UPD_TCR_CNT = UPD_TCR_CNT - SAMPLE_INTERVAL;
    UPD_RTD_CNT = UPD_TCR_CNT - SAMPLE_INTERVAL;
  }  

  if(DBG_MODE < 2) // only printout when not in plot mode
  {
      Serial.print("TC_TEMP_CAL: ");        // send requested data 
      Serial.println(TC_TEMP_CAL);          // send requested data 
      Serial.print("RTD_TEMP_FIL: ");   // send requested data 
      Serial.println(RTD_TEMP_FIL);     // send requested data  
  }  

  if((RTD_TEMP_FIL > 250.00) || (RTD_TEMP_FIL < 0.00))
  {
      RTD_ERR = 1;      // RTD temperature out of range/ sensor break ==> SET ERR FLAG HIGH
  }
  else
  {
      RTD_ERR = 0;     // RTD temperature in of range so RESET error
  }
  

  if((RTD_TEMP_FIL > 18.00) && (RTD_TEMP_FIL < 24.00) && (RTD_ERR == 0))
  {
     OS_TEMP = float(RTD_TEMP_FIL - TC_TEMP_CAL);            // determine difference btween two sensors
     Serial.println();         
     Serial.print("OS_TEMP: ");        // send requested data 
     Serial.println(OS_TEMP);          // 
     Serial.print("saving offset to eeprom... ");        // send requested data 
     EEPROM.put(NVM_TOS_ADR,OS_TEMP);             // PUT PID deadband setting into NVM
     delay(10); // wait for action to complete
  }
  else
  {
    if(DBG_MODE == 1) // only printout when not in plot mode
    {
       Serial.print("Ambient temperature out of range, aborting save to NVM action...");        // send requested data   
    }
    
  }  
  
  if(DBG_MODE == 1) // only printout when not in plot mode
  {
      Serial.print("End thermocouple offset compensation, time marker (mSec): ");         // stop stopwatch (in msecs)
      Serial.println(MSEC_CNT);          // send requested data
  }

  CHK_RTD = 0;
  UPD_TCR_CNT = 0;
  
} //end SET_TEMP_OFFSET()


// *********************************************************   ReadTemperature      ***************************************************************************************
//  - K-type Thermocouple readout via AD8495 breakout board
//  - Breakout board generates analog voltage compatible with Arduino 0-5V ADC range ==> connected to A15 of Atmega2560
//  - ADC is read at 1Khz/10bit resolution, oversampled 64x for 13 bit resolution with aprox 15 Hz update rate (noisy enviroment so active dithering signal injection not required)
//  - After oversampling of ADC input, data is filtered via IIR filter with variable gain and assigned to [ADC_INP_mV]
//  - Temperature formula: Temp. (in deg. C) = (ADC_INP_mV - 1250) / 5 ,  e.g.: if voltage from AD8495 module is 1500mV (1.5 Vdc), temperature is (1500 - 1250) / 5 = 50°C
//  Note: [1250] value needs modification via a constant to set value range 1245-1265 range (in ELD2123 is about 1263-ish)
// ***********************************************************************************************************************************************************************
void ReadTemperature() // 1 Khz update rate
{
  if(UPD_TCR_CNT >= TCR_INTVAL)                   // update check ==> jumps into routine every 1 mSec
  {
    VREF_RAW = (analogRead(VREF_PIN));            // read the adc input pin connected to breakout board
    
    TC_TEMP_RAW = (analogRead(TC_PIN))- ADC_ZERO_OFFSET;        // read the adc input pin connected to breakout board
  
    TC_OS_ACC = TC_OS_ACC + TC_TEMP_RAW;          // add raw ADC val to adc accumulator value

    FIL_VREF = float((OLD_VREF * VREG_FIL_GAIN) + VREF_RAW) / float(VREG_FIL_GAIN + 1);
    
    OLD_VREF = FIL_VREF;                    // set old value to current value

    VREF_OS_ACC = VREF_OS_ACC + FIL_VREF;         // oversample VREF ADC value
  
    TC_OS_CNT++;                                  // increase oversample counter
   
    if(TC_OS_CNT >= TC_OS_SIZE)                   // oversampling size has been met.
    {

      if(TC_OS_SIZE == 64)
      {
         TC_INP_OSV = (TC_OS_ACC >> 3);              // 13 bit option, shift right 3 pos for 64x oversampling,  change TC_OS_SIZE to 64  
         VREF_OSV   =  float(VREF_OS_ACC >> 3);
         TC_INP_OSV = TC_INP_OSV / VREF_OSV * 4096;
      }

      if(TC_OS_SIZE == 256)
      {
        TC_INP_OSV = (TC_OS_ACC >> 4);              // 14 bit option, shift right 4 pos for 256x oversampling,  change TC_OS_SIZE to 256 
        VREF_OSV   =  float(VREF_OS_ACC >> 4);
        TC_INP_OSV = TC_INP_OSV / VREF_OSV * 8192;
      }

      // IIR filtering, gain of 1 = filter OFF, values above 1 filtering gain is active.
      TC_INP_FIL = ((TC_INP_OLD * TC_FIL_GAIN) + TC_INP_OSV) / (TC_FIL_GAIN + 1);
      TC_INP_FIL =  TC_INP_FIL + OS_TEMP;
      TC_INP_OLD = TC_INP_FIL;                    // set old value to current value
     

      if(TC_OS_SIZE == 64) // oversamping for 13 bit ADC  value (8192 ADC steps)
      {
        
        ADC_INP_mV = float((TC_INP_FIL * 5000.00) / 8192.00) + ADC_mV_OFFSET;      // temp. value in mV (0-5000 mV) going into the ADC
      }

      if(TC_OS_SIZE == 256) // oversamping for 14 bit ADC  value (16384 ADC steps)
      {
        ADC_INP_mV = float((TC_INP_FIL * 5000.00) / 16384.00) + ADC_mV_OFFSET;      // temp. value in mV (0-5000 mV) going into the ADC
      }       
      
      // TC_INP_mV = (ADC_INP_mV * 5) -12500 + TC_mV_OFFSET ;            // temp. value value in deg. C
      
      // TC_TEMP_CAL = float((ADC_INP_mV - TC_BaseVoltage)/ 5);          // Assign temperature to PV_TEMP var for use in PID control function
      
      TC_TEMP_CAL = double((ADC_INP_mV - TC_BaseVoltage) / float(5.00));      // 4.965V is the open circuit ADC voltage
      
      PV_TEMP = float(TC_TEMP_CAL) + OS_TEMP; 

     
      if(PV_TEMP > 650.00)        // check if sensor is still connected ==> When no sensor connected temp is always around 740 deg C
      {
        TC_ERR = 1;               // SET temp error flag 
      }
      else
      {
         TC_ERR = 0;              // reset temp error flag
      }
      
      TC_OS_CNT = 0;              // reset oversampling sample counter        
      TC_OS_ACC = 0;              // set oversample accumulator to 0  
      VREF_OS_ACC = 0;            // set oversample accumulator to 0  
    
    }// end OS covert to temp
    
    UPD_TCR_CNT = 0;              // reset update thermocouple read counter to 0
  }  // end cnt/int



  if((UPD_RTD_CNT > UPD_RTD_INTVAL) && (CHK_RTD == 1)) // do an RTD (PT100) temp. sense conversion
  {
    // PT100  readout
    rtd = thermo.readRTD();
    ratio = rtd;
    ratio /= 32768;
    RTD_TEMP = thermo.temperature(RNOMINAL, RREF);  
    RTD_TEMP_RAW = RTD_TEMP +  RTD_T_OFFSET; 

    RTD_TEMP_FIL = ((RTD_TEMP_OLD * RTD_FIL_GAIN) + RTD_TEMP_RAW) / (RTD_FIL_GAIN + 1);

    RTD_TEMP_OLD = RTD_TEMP_FIL;

    UPD_RTD_CNT = 0;  
  }

  
} // end ReadTemperature


// *****************************************   CheckSerialRXD      *****************************************************************************************************
// - Checks incoming command bytes from PC/USB comms
// - ACK/echo in case of an OK command
// - NOACK / * in case of bad command
// *********************************************************************************************************************************************************************
void CheckSerialRXD()
{
   while(Serial.available())                        // is a character available?
   {    
      rx_byte = Serial.read();                     // get the character
      
          if(rx_byte != '\n')
          {
            // a character of the string was received
            rx_str += rx_byte;
            rx_arr[rx_index] = rx_byte;
            rx_index++;
          }
          else // newline detected, start parsing the string
          {
              //Serial.println();                   // debug only , uncomment for debug
              //Serial.print("GUI CMD: ");          // debug only , uncomment for debug
              //Serial.println(rx_str);             // debug only , uncomment for debug
            
              switch(rx_arr[0])
              {   
                  case 'i': // info / help / show list
                     Serial.println();
                     Serial.println("  ***************************************************    HELP  ************************************************************************ ");
                     Serial.println("");   
                     Serial.println(" - NOTE 1: SERIAL BAUD SETTINGS: 115200/8/N/1 ");
                     
                     // Single char commands
                     Serial.println("  ********** Single char commands ******** ");
                     Serial.println(" - [i]: Info");  
                     Serial.println(" - [c]: Show stepper driver board configuration."); 
                     Serial.println(" - [l]: List parameters.");                                                                                                          // 
                     Serial.println(" - [d]: Defaults/restore, this commands resets the controller values (in eeprom) to initial values.");                               // 
                     Serial.println(" - [r]: Reset controller (Arduino) and stepper driver HW (does not reset eeprom)."); 
                     Serial.println(" - [n]: Put controller (Arduino) in runmode ==> runmode: inputs active & outputs are activated."); 
                     Serial.println(" - [p]: Put controller (Arduino) in stopmode ==> stopmode: inputs active & outputs deactivated."); 
                     Serial.println(" - [z]: Zero stage till top limit switch is closed , then move xxx steps down untill till limit switch is open and set positions to 0.");
                     Serial.println(" - [x]: Stop all stage(s) at once.");  
                   
                     // multi char:  GET commands
                     Serial.println("  ********** GET commands ******** ");
                     Serial.println(" - [ga]: Get actors state.");                                          // ON/OFF states   
                     Serial.println(" - [gb]: Get the stepper driver (hardware) status.");                  // internal state (use powerstep01 manual for register address )
                     Serial.println(" - [gc]: Get the stepper driver (hardware) configuration parameter."); // internal state (need powerstep manual )
                     Serial.println(" - [ge]: Get error state.");                                           // 0 or 1 states ==> global or bitstate .... TBD PN
                     Serial.println(" - [gp[xyz]]: Get stepper motor stage position.");                     // in uM/steps
                     Serial.println(" - [gs[xyz]]: Get stepper motor speed.");                              // in uM/steps
                     Serial.println(" - [gt]: Get temperature setpoint (deg C.).");                         // in Deg. C
                     Serial.println(" - [gb]: Get temperature deadband (deg C.).");                         // in Deg. C
                        
                    
                     // multi char: SET commands
                     Serial.println("  ********** SET commands ******** ");
                     Serial.println(" - [ss]: Set run/top speed of motors, e.g: ss225 = set top speed of motors to 225.");                          // 
                     Serial.println(" - [sa]: Set acceleration rate of motors, e.g: sa1225 = set accel of motors to 1225 (steps/sec).");            // 
                     Serial.println(" - [sd]: Set deceleration rate of motors, e.g: sd1225 = set decel of motors to 1225 (steps/uM).");             // 
                     Serial.println(" - [sp[xyz]]: Set and goto position, e.g: spy1000 = stepper y goto position 1000 steps from 0 point.");
                     Serial.println(" - [sh]: Set stages to goto home (goto to 0 position).");                                                      // 
                     Serial.println(" - [st]: Set temperature, e.g: st251 = set temperature for PID control to 25.1 deg C (value in deg C x10).");  // 
                     Serial.println(" - [sb]: Set temp deadband, e.g: sb22 = set deadband for PID control to 2.2 deg C (value in deg C x10).");     // 
                     Serial.println(" - [sr]: Set Respone/debug mode, e.g:serial comms (debug mode) ==>  0=OFF / 1=DEBUG / 2=PLOTTER");             //      
                     Serial.println(" - [sv]: Set vacuum/suction pump ==>  0=OFF / 1=ON ");                                                         //  
                     Serial.println(" - [sv]: Set vacuum/suction pump ==>  0=OFF / 1=ON ");                                                         //                             
                  break;

                
                  case 'c':                               // Get stepper driver hardware status
                    Serial.println();                     // spacer
                    Serial.println("c OK ");              // reply ACK to GUI
                    //while(xstage.busyCheck());          // board not busy check
                    DRIVER_STATUS = xstage.getStatus();   // reading status clears error flags in driver board
                    Serial.println(DRIVER_STATUS);        // Send data out
                    //while(ystage.busyCheck());          // board not busy check
                    DRIVER_STATUS = ystage.getStatus();   // reading status clears error flags in driver board
                    Serial.println(DRIVER_STATUS);        // Send data out
                    //while(zstage.busyCheck());          // board not busy check
                    DRIVER_STATUS = zstage.getStatus();   // reading status clears error flags in driver board
                    Serial.println(DRIVER_STATUS);        // Send data out
                  break;

                
                  
                  case 'l':                           // List parameters
                    Serial.println();                 // spacer
                    Serial.println("l OK ");          // reply ACK to GUI
                    Serial.println(TOP_SPD_X);        // List stepper motor top speed 
                    Serial.println(TOP_SPD_Y);        // List stepper motor top speed 
                    Serial.println(TOP_SPD_Z);        // List stepper motor top speed 
                    Serial.println(STEP_ACCEL);       // List stepper motor acceleration
                    Serial.println(STEP_DECEL);       // List stepper motor deceleration 
                    
                    Serial.println(SP_TEMP);          // List PID setpoint temperature 
                    Serial.println(DB_TEMP);          // List PID deadband temperature 
                    
                    Serial.println(KP_HEAT);          // List PID proportional parameter
                    Serial.println(KI_HEAT);          // List PID intergral parameter
                    Serial.println(KD_HEAT);          // List PID derivative parameter
                    
                    Serial.println(KP_COOL);          // List PID proportional parameter
                    Serial.println(KI_COOL);          // List PID intergral parameter
                    Serial.println(KD_COOL);          // List PID derivative parameter
                  break;

                  case 'd':                           // default MCU, reverts Arduino controller to default settings 
                    Serial.println();                 // spacer
                    Serial.println("d OK ");          // reply ACK to GUI
                    //while(xstage.busyCheck());      // board not busy check
                    xstage.resetDev();                // Reset stepper driver board
                    //while(ystage.busyCheck());      // board not busy check
                    ystage.resetDev();                // Reset stepper driver board
                    //while(zstage.busyCheck());      // board not busy check
                    zstage.resetDev();                // Reset stepper driver board
                    EEPROM.write(NVM_CHK_ADR, 0);     // NVM_CHK_ADR = 0 is empty, 1 = written 
                    delay(50);                        // wait before resetting Arduino
                    resetFunc();                      // call reset, this will reboot the Arduino (all RAM will be lost), will then restart and params will revert to default values from setup constants and defines
                  break;   

                  case 'r':                           // r = reset controller, small r, resets the Arduino but no NVM erase
                    Serial.println();                 // spacer
                    Serial.println("r OK ");          // reply ACK to GUI
                   // while(xstage.busyCheck());      // board not busy check
                    xstage.resetDev();                // Reset stepper driver board
                    delay(50);                        // wait before resetting Arduino
                    //while(ystage.busyCheck());      // board not busy check
                    ystage.resetDev();                // Reset stepper driver board
                    delay(50);                        // wait before resetting Arduino
                    //while(zstage.busyCheck());      // board not busy check
                    zstage.resetDev();                // Reset stepper driver board
                    delay(50);                        // wait before resetting Arduino
                    resetFunc();                      // call MCU reset, this will reboot the Arduino (all RAM will be lost).
                  break;   

                  case 'n':                               // n ==> RUNMODE: RUN
                    Serial.println();                     // spacer
                    Serial.println("n OK ");              // reply ACK to GUI
                    
                    RUNMODE = 1;                          // RUNMODE = RUN

                    FORCE_CLR = 0;                        // Reset force Cooler value

                    FORCE_HTR = 0;                        // Reset force Heater value 

                    HEAT_PID.SetMode(AUTOMATIC);          // Set temperature PID  controller to auto and start
                    COOL_PID.SetMode(AUTOMATIC);          // Set temperature PID  controller to auto and start
  
                    //while(xstage.busyCheck());          // board not busy check
                    DRIVER_STATUS = xstage.getStatus();   // reading status clears error flags in driver board
                    //Serial.println(DRIVER_STATUS);      // Send data out
                    //while(ystage.busyCheck());          // board not busy check
                    DRIVER_STATUS = ystage.getStatus();   // reading status clears error flags in driver board
                    //Serial.println(DRIVER_STATUS);      // Send data out
                    //while(zstage.busyCheck());          // board not busy check
                    DRIVER_STATUS = zstage.getStatus();   // reading status clears error flags in driver board
                    //Serial.println(DRIVER_STATUS);      // Send data out
                    
                   if(DBG_MODE == 2)                      // Init plotter with keys/labels for dataplot
                    {
                      delay(10);                         
                      Serial.println("SV_TMP:,PV_TMP:,CV_HEAT:,CV_COOL:,X_SPD:,Y_SPD:,Z_SPD:,");                // Legend/Keys for plotter/chart
                      delay(10);                                      // wait 500 mS before commencing otherwise labels will contain sensor data
                    }
                  
                  break;   

                  case 'p':                           // n ==> RUNMODE: STOP
                    Serial.println();                 // spacer
                    Serial.println("p OK ");          // reply ACK to GUI                    
                    
                    RUNMODE = 0;                      // RUNMODE STOP

                    HEAT_PID.SetMode(MANUAL);         // Set temperature PID  controller to auto and start
                    COOL_PID.SetMode(MANUAL);         // Set temperature PID  controller to auto and start
                    
                    if(HOMING_TO_ZERO)                // if stage is homing, abort homing move and reset flag;  
                    {
                      HOMING_TO_ZERO = 0;             // RESET HOMING flag
                    }                   

                    GOTO_X_FLAG = 0;                  // Reset GOTO flag   
                    GOTO_Y_FLAG = 0;                  // Reset GOTO flag   
                    GOTO_Z_FLAG = 0;                  // Reset GOTO flag
                       
                    //GOTO_TARGET = 0;                // Reset GOTO flag   
                    
                    //while(xstage.busyCheck());      // board not busy check
                    xstage.softStop();                // STOP command
                    // while(ystage.busyCheck());     // board not busy check
                    ystage.softStop();                // STOP command
                    // while(zstage.busyCheck());     // board not busy check
                    zstage.softStop();                // STOP command

                    if(DBG_MODE == 2)                                  // Init plotter with keys/labels for dataplot
                    {
                      delay(10);   
                      //Serial.println("SV_TMP:,PV_TMP:,CV_HEAT:,CV_TEC:,X_SPD:,Y_SPD:,Z_SPD:,");                // Legend/Keys for plotter/chart
                      Serial.println("SV_TMP:,PV_TMP:,CV_HEAT:,CV_COOL:,X_SPD:,Y_SPD:,Z_SPD:,");                // Legend/Keys for plotter/chart
                      delay(10);                                      // wait 500 mS before commencing otherwise labels will contain sensor data
                    }
                  break;   
                  

                 case 'h':                                            // Home
                    Serial.println();                                 // Spacer
                    Serial.println("h OK ");                          // reply ACK to GUI
                    //HOMING_TO_ZERO = 1;                             // Set homing flag high


                   if(XSTAGE_ENABLE)    // XSTAGE    
                   {
                       // while(xstage.busyCheck());                      // wait until driver is not busy anymore
                      xstage.softStop();                                // soft stop prevents errors in the next operation
                      xstage.setMaxSpeed(HOMING_STEP_SPD);              // set speed to Homing speed (fixed)
                      GOTO_X_FLAG = 0;
                      
                      if(CUR_POS_MOT_X != 0)
                      {
                          while(xstage.busyCheck());
                          digitalWrite(XSTAGE_LED, HIGH);                //  TURN ON MOTOR LED     
                          xstage.goTo(END_POS_X);                                // Goto home position
                      }
                   }
                   

                   if(YSTAGE_ENABLE)      // YSTAGE     
                   {
                       // while(xstage.busyCheck());                      // wait until driver is not busy anymore
                      ystage.softStop();                                // soft stop prevents errors in the next operation
                      ystage.setMaxSpeed(HOMING_STEP_SPD);              // set speed to Homing speed (fixed)
                      GOTO_Y_FLAG = 0;
                      
                      if(CUR_POS_MOT_Y != 0)
                      {
                          while(ystage.busyCheck());
                          digitalWrite(YSTAGE_LED, HIGH);                //  TURN ON MOTOR LED     
                          ystage.goTo(END_POS_Y);                                // Goto home position
                      }
                   }
                   

                   if(ZSTAGE_ENABLE)     // ZSTAGE       
                   {
                       // while(xstage.busyCheck());                      // wait until driver is not busy anymore
                      zstage.softStop();                                // soft stop prevents errors in the next operation
                      zstage.setMaxSpeed(HOMING_STEP_SPD);              // set speed to Homing speed (fixed)
                      GOTO_Z_FLAG = 0;
                      
                      if(CUR_POS_MOT_Z != 0)
                      {
                          while(zstage.busyCheck());
                          digitalWrite(ZSTAGE_LED, HIGH);                //  TURN ON MOTOR LED     
                          zstage.goTo(END_POS_Z);                                // Goto home position
                      }
                   }


                   if(XSTAGE_ENABLE)    // XSTAGE    
                   {
                      while(xstage.busyCheck());
                      xstage.setMaxSpeed(SET_SPD_X);                      // max speed in units of full steps/s 
                      xstage.getStatus();                                 // get status from driver board, this get clears error flags
                   }


                   if(YSTAGE_ENABLE)    // YSTAGE    
                   {
                      while(ystage.busyCheck());
                      ystage.setMaxSpeed(SET_SPD_Y);                      // max speed in units of full steps/s 
                      ystage.getStatus();                                 // get status from driver board, this get clears error flags
                   }

                   if(ZSTAGE_ENABLE)    // ZSTAGE    
                   {
                      while(zstage.busyCheck());
                      zstage.setMaxSpeed(SET_SPD_Z);                      // max speed in units of full steps/s 
                      zstage.getStatus();                                 // get status from driver board, this get clears error flags
                   }                   
                    //HOMING_TO_ZERO = 0;                               // set homing flag to zero
                  break;                  

                  case 'x':                           // abort/stop current move (applies to all motors, if moving)
                    Serial.println();                 // spacer
                    Serial.println("x OK ");          // reply ACK to GUI

                    if(HOMING_TO_ZERO)                // if stage is homing, abort homing move and reset flag;  
                    {
                      HOMING_TO_ZERO = 0;             // RESET HOMING flag
                    }                    

                    GOTO_X_FLAG = 0;                  // RESET GOTO flag   
                    GOTO_Y_FLAG = 0;                  // RESET GOTO flag   
                    GOTO_Z_FLAG = 0;                  // RESET GOTO flag   
                    //GOTO_TARGET = 0;                // RESET GOTO flag   

                    VELOCITY_X_CMD = 0;               // Reset manual speed  to 0
                    VELOCITY_Y_CMD = 0;               // Reset manual speed  to 0
                    VELOCITY_Z_CMD = 0;               // Reset manual speed  to 0 
                    
                    // while(xstage.busyCheck());     // board not busy check
                    xstage.softStop();                // STOP command
                    // while(ystage.busyCheck());     // board not busy check
                    ystage.softStop();                // STOP command
                    // while(zstage.busyCheck());     // board not busy check
                    zstage.softStop();                // STOP command                    
                   break; 
                   
                  
                  case 'z':                           // zero-ing stage and setting stage position reference to 0 
                    Serial.println();                 // spacer
                    Serial.println("z OK ");          // reply ACK to GUI
                    
                    if(SetManualLimits)
                    {
                      END_POS_X = X_MAN_ENDPOS;       // Holds stage end position (mark) in steps from 0 point, this value is set in ZeroStage()
                      END_POS_Y = Y_MAN_ENDPOS;       // Holds stage end position (mark) in steps from 0 point, this value is set in ZeroStage()
                      END_POS_Z = Z_MAN_ENDPOS;       // Holds stage end position (mark) in steps from 0 point, this value is set in ZeroStage()  

                     if(XSTAGE_ENABLE)                // XSTAGE    
                     {
                        X_INIT_DONE = 0;               // testing only, commnent out for application 
                        INIT_X_STAGE = 0;  
                     }

                     if(YSTAGE_ENABLE)                 // XSTAGE    
                     {
                        Y_INIT_DONE = 0;                // testing only, commnent out for application 
                        INIT_Y_STAGE = 0; 
                     }

                     if(YSTAGE_ENABLE)                 // XSTAGE    
                     {
                        Z_INIT_DONE = 0;              // testing only, commnent out for application
                        INIT_Z_STAGE = 0;    
                     }                    

                     ZeroStage();                     // Execute zero stage routine
                     
                    }
                    else                              // Get limit via automiatic Zeroing
                    {
                       ZeroStage();                   // Execute zero stage routine
                       
                    }
                  break;   
                  

                  case 's': // SET commands   **************************************************************************

                    switch(rx_arr[1])
                    {
                         case 's': // SET stepper motor top speed

                             switch(rx_arr[2])
                                {
                                  case 'x': // xstage
                                    Serial.println();                               // spacer
                                    rx_str = rx_str.substring(3);                   // strip off first 2 chars
                                    SER_RXD_VAL = rx_str.toInt();                   // assign newly rxd data to SER_RXD_VAL
                                    TOP_SPD_X = float(SER_RXD_VAL);                 // assign TOP_SPD with new value                                    
        
                                    //Serial.print("TOP_SPD_X pre SPEED_MODE: ");   // reply ACK to GUI
                                    //Serial.println(TOP_SPD_X);                    // echo entry data, optional
                                    //Serial.print("SER_RXD_VAL SPEED_MODE: ");     // reply ACK to GUI
                                    //Serial.println(SER_RXD_VAL);                  // echo entry data, optional
  
                                    if(TOP_SPD_X < SLOW_SPD_THR)                    // ( slow speed mode: <1750 steps/sec )
                                    {
                                        SPEED_MODE_X = 0;
                                        JOG_STEP_SIZE_X = TOP_SPD_X / 116;          // ==> / 100 since  
                                        X_APR_STATE = 1;                            // set APPROACH to COMMAND ISSUES (1)
                                        
                                        if (JOG_STEP_SIZE_X < 1)
                                        {
                                          JOG_STEP_SIZE_X = 1;
                                        }
        
                                        if(JOG_STEP_SIZE_X > MAX_JOG_STEP_SIZE) 
                                        {
                                          JOG_STEP_SIZE_X = MAX_JOG_STEP_SIZE;      // clip to max value, currently max of 10 steps @ 40 is the max before move command gets ignored by driver board since previous move is still ongoing
                                        }
                                        
                                    }
                                    else
                                    {
                                        SPEED_MODE_X = 1; // normal speed mode ( >1750 steps/sec )
                                        SET_SPD_X = TOP_SPD_X / 113;
                                    }
                                  
                                    if((TOP_SPD_X > 0.00) && (TOP_SPD_X < MAX_SS_SPD))  // do value OK/ in range check for steps/sec speed entry
                                    {
                                        Serial.println("ssx OK ");                      // reply ACK to GUI
                                        Serial.println(TOP_SPD_X);                      // echo entry data, optional
                                        //Serial.println("SPEED_MODE_X");               // reply ACK to GUI
                                        //Serial.println(TOP_SPD_X);                    // reply ACK to GUI
                                        //Serial.println("JOG_STEP_SIZE_X");            // reply ACK to GUI
                                        //Serial.println(JOG_STEP_SIZE_X);              // reply ACK to GUI
                                        //Serial.println("TOP_SPD_X");                  // reply ACK to GUI
                                        //Serial.println(TOP_SPD_X);                    // reply ACK to GUI
                                        
                                        
                                        //while(xstage.busyCheck());                    // wait untill driver is not busy anymore
                                        if(SPEED_MODE_X == 1)
                                        {
                                           xstage.setMaxSpeed(SET_SPD_X);               // top speed in units of full steps/s 
                                           xstage.setMinSpeed(1);           
                                        }                                       
                                       
                                        EEPROM.put(NVM_SPD_X_ADR, float(SER_RXD_VAL));  // write data to NVM (eeprom)
                                        delay(10);                                      // delay 10 mSec
                                    }
                                    else
                                    {
                                        Serial.println("*");  // bad entry response
                                        Serial.println(TOP_SPD_X);                      // echo entry data, optional
                                    }
                                    break; // End X-stage



                                    case 'y': // Y-stage
                                    Serial.println();                               // spacer
                                    rx_str = rx_str.substring(3);                   // strip off first 2 chars
                                    SER_RXD_VAL = rx_str.toInt();                   // assign newly rxd data to SER_RXD_VAL
                                    TOP_SPD_Y = SER_RXD_VAL;                        // assign TOP_SPD with new value
        
                                    //Serial.print("TOP_SPD_Y pre SPEED_MODE: ");   // reply ACK to GUI
                                    //Serial.println(TOP_SPD_Y);                    // echo entry data, optional
  
                                    if(TOP_SPD_Y < SLOW_SPD_THR)                    // ( slow speed mode: <1750 steps/sec )
                                    {
                                        SPEED_MODE_Y = 0;
                                        JOG_STEP_SIZE_Y = TOP_SPD_Y / 116;          // ==> / 100 since 
                                        Y_APR_STATE = 1;                            // set APPROACH to COMMAND ISSUES (1) 
                                        
                                        if (JOG_STEP_SIZE_Y < 1)
                                        {
                                          JOG_STEP_SIZE_Y = 1;
                                        }
        
                                        if(JOG_STEP_SIZE_Y > MAX_JOG_STEP_SIZE) 
                                        {
                                          JOG_STEP_SIZE_Y = MAX_JOG_STEP_SIZE;      // clip to max value, currently max of 10 steps @ 40 is the max before move command gets ignored by driver board since previous move is still ongoing
                                        }
                                        
                                    }
                                    else
                                    {
                                        SPEED_MODE_Y = 1; // normal speed mode ( >1750 steps/sec )
                                        SET_SPD_Y = TOP_SPD_Y / 113;
                                    }
                                  
                                    if((TOP_SPD_Y > 0.00) && (TOP_SPD_Y < MAX_SS_SPD))  // do value OK/ in range check for steps/sec speed entry
                                    {
                                        Serial.println("ssy OK ");                      // reply ACK to GUI
                                        Serial.println(TOP_SPD_Y);                      // echo entry data, optional
                                        //Serial.println("SPEED_MODE_Y");               // reply ACK to GUI
                                        //Serial.println(TOP_SPD_Y);                    // reply ACK to GUI
                                        //Serial.println("JOG_STEP_SIZE_Y");            // reply ACK to GUI
                                        //Serial.println(JOG_STEP_SIZE_Y);              // reply ACK to GUI
                                        //Serial.println("TOP_SPD_Y");                  // reply ACK to GUI
                                        //Serial.println(TOP_SPD_Y);                    // reply ACK to GUI
          
                                        
                                        //while(xstage.busyCheck());                   // wait untill driver is not busy anymore
                                        if(SPEED_MODE_Y == 1)
                                        {
                                           ystage.setMaxSpeed(SET_SPD_Y);              // top speed in units of full steps/s 
                                           ystage.setMinSpeed(1);           
                                        }                                       
                                       
                                        EEPROM.put(NVM_SPD_Y_ADR, float(SER_RXD_VAL)); // write data to NVM (eeprom)
                                        delay(10);                                     // delay 10 mSec
                                    }
                                    else
                                    {
                                        Serial.println("*");  // bad entry response
                                        Serial.println(TOP_SPD_Y);                      // echo entry data, optional
                                    }
                                    break; // End X-stage


                                    case 'z': // Z-stage
                                    Serial.println();                               // spacer
                                    rx_str = rx_str.substring(3);                   // strip off first 2 chars
                                    SER_RXD_VAL = rx_str.toInt();                   // assign newly rxd data to SER_RXD_VAL
                                    TOP_SPD_Z = SER_RXD_VAL;                        // assign TOP_SPD with new value
        
                                    //Serial.print("TOP_SPD_Z pre SPEED_MODE: ");   // reply ACK to GUI
                                    //Serial.println(TOP_SPD_Z);                    // echo entry data, optional
  
                                    if(TOP_SPD_Z < SLOW_SPD_THR)                    // ( slow speed mode: <1750 steps/sec )
                                    {
                                        SPEED_MODE_Z = 0;
                                        JOG_STEP_SIZE_Z = TOP_SPD_Z / 116;          // ==> / 100 since  
                                        Y_APR_STATE = 1;                            // set APPROACH to COMMAND ISSUES (1) 
                                        
                                        if (JOG_STEP_SIZE_Z < 1)
                                        {
                                          JOG_STEP_SIZE_Z = 1;
                                        }
        
                                        if(JOG_STEP_SIZE_Z > MAX_JOG_STEP_SIZE) 
                                        {
                                          JOG_STEP_SIZE_Z = MAX_JOG_STEP_SIZE; // clip to max value, currently max of 10 steps @ 40 is the max before move command gets ignored by driver board since previous move is still ongoing
                                        }
                                        
                                    }
                                    else
                                    {
                                        SPEED_MODE_Z = 1; // normal speed mode ( >1750 steps/sec )
                                        SET_SPD_Z = TOP_SPD_Z / 113;
                                        
                                    }
                                  
                                    if((TOP_SPD_Z > 0.00) && (TOP_SPD_Z < MAX_SS_SPD))  // do value OK/ in range check for steps/sec (SS) speed entry
                                    {
                                        Serial.println("ssz OK ");                      // reply ACK to GUI
                                        Serial.println(TOP_SPD_Z);                      // echo entry data, optional
                                        //Serial.println("SPEED_MODE_Z");               // reply ACK to GUI
                                        //Serial.println(TOP_SPD_Z);                    // reply ACK to GUI
                                        //Serial.println("JOG_STEP_SIZE_Z");            // reply ACK to GUI
                                        //Serial.println(JOG_STEP_SIZE_Z);              // reply ACK to GUI
                                        //Serial.println("TOP_SPD_Z");                  // reply ACK to GUI
                                        //Serial.println(TOP_SPD_Z);                    // reply ACK to GUI
          
                                        
                                        //while(xstage.busyCheck());                   // wait untill driver is not busy anymore
                                        if(SPEED_MODE_Z == 1)
                                        {
                                           zstage.setMaxSpeed(SET_SPD_Z);              // top speed in units of full steps/s 
                                           zstage.setMinSpeed(1);           
                                        }                                       
                                       
                                        EEPROM.put(NVM_SPD_Z_ADR, float(SER_RXD_VAL));        // write data to NVM (eeprom)
                                        delay(10);                                     // delay 10 mSec
                                    }
                                    else
                                    {
                                        Serial.println("*");  // bad entry response
                                        Serial.println(TOP_SPD_Z);                      // echo entry data, optional
                                    }
                                    break; // End Z-stage

                                    
                              } // switch(rx_arr[2])
                              
                              break;  // end case 's' (speed)

                      
                         

                         case 'a': // SET stepper motor acceleration
                            Serial.println();                               // spacer
                            rx_str = rx_str.substring(2);                   // strip off first 2 chars
                            SER_RXD_VAL = rx_str.toInt();                   // assign newly rxd data to SER_RXD_VAL

                            if(stage_pos_units)
                            {
                               STEP_ACCEL = SER_RXD_VAL/2.56;               // entry in um/sec
                            }
                            else
                            {
                               STEP_ACCEL = SER_RXD_VAL;                    // entry in steps/sec
                            }
                                                                  
                            
                            if((STEP_ACCEL >= 0) && (STEP_ACCEL <= MAX_STEP_ACCEL)) // do value OK/ in range check
                            {
                              Serial.println("sa OK ");                     // reply ACK to GUI
                              Serial.println(STEP_ACCEL);                   // Echo back rxd data, optional 
                              //while(xstage.busyCheck());                  // wait untill driver is not busy anymore
                              xstage.setAcc(STEP_ACCEL);                    // full steps/s^2 acceleration
                              //while(ystage.busyCheck());                  // wait untill driver is not busy anymore
                              ystage.setAcc(STEP_ACCEL);                    // full steps/s^2 acceleration
                              //while(zstage.busyCheck());                  // wait untill driver is not busy anymore
                              zstage.setAcc(STEP_ACCEL);                    // full steps/s^2 acceleration
                              EEPROM.put(NVM_ACC_ADR, STEP_ACCEL);          // write data to NVM (eeprom)
                              delay(10);                                    // delay 10 mSec
                            }
                            else
                            {
                              Serial.println("*");  // bad entry response
                            }
                         break;

                         case 'd': // SET stepper motor deceleration
                            Serial.println();                               // spacer
                            rx_str = rx_str.substring(2);                   // strip off first 2 chars
                            SER_RXD_VAL = rx_str.toInt();                   // assign newly rxd data to SER_RXD_VAL

                            //STEP_DECEL = SER_RXD_VAL;

                            if(stage_pos_units)
                            {
                               STEP_DECEL = SER_RXD_VAL/2.56; // entry in um/sec
                            }
                            else
                            {
                               STEP_DECEL = SER_RXD_VAL;    // entry in steps/sec
                            }

                            
                            if((STEP_DECEL >= 0) && (STEP_DECEL <= MAX_STEP_DECEL)) // do value OK/ in range check
                            {
                              Serial.println("sd OK ");                     // reply ACK to GUI
                              Serial.println(STEP_DECEL);                   // Echo back rxd data, optional 
                              //while(xstage.busyCheck());                  // wait untill driver is not busy anymore
                              xstage.setDec(STEP_DECEL);                    // full steps/s^2 acceleration
                              //while(ystage.busyCheck());                  // wait untill driver is not busy anymore
                              ystage.setDec(STEP_DECEL);                    // full steps/s^2 acceleration
                              //while(zstage.busyCheck());                  // wait untill driver is not busy anymore
                              zstage.setDec(STEP_DECEL);                    // full steps/s^2 acceleration
                              EEPROM.put(NVM_DEC_ADR, STEP_DECEL);          // write data to NVM (eeprom)
                              delay(10);                                    // delay 10 mSec
                            }
                            else
                            {
                              Serial.println("*");  // bad entry response
                            }
                         break;

                         case 'p': // GOTO/set position
                         //RESET_TO_ZERO = 1; // debug only
                         //X_INIT_DONE     = 1; // debug only 
                         //X_INIT_DONE     = 1; // debug only
                         //X_INIT_DONE     = 1; // debug only
                         

                         if((X_INIT_DONE) && (Y_INIT_DONE) && (Z_INIT_DONE))                                 // check if stage has been zeroed ==>  yes, goto pos , NO, error ack
                         {
                            Serial.println();                               // Spacer
                            rx_str = rx_str.substring(3);                   // strip off first 2 chars
                            SER_RXD_VAL = rx_str.toInt();                   // assign newly rxd data to SER_RXD_VAL
  
                            if(stage_pos_units == 0) // Units in steps, max aprox 50K
                            {
                               if((SER_RXD_VAL > stage_endpos_steps) || (SER_RXD_VAL < 0))
                               {
                                 Serial.println("*");  // bad entry response
                                 break;
                               }
                            }
  
                            if(stage_pos_units == 1) // Units in steps, max aprox 200K
                            {
                               if((SER_RXD_VAL > stage_endpos_micron) || (SER_RXD_VAL < 0))
                               {
                                 Serial.println("*");  // bad entry response
                                 break;
                               }
                            }
                            
                            if(stage_pos_units == 0)                        // determine uits (uM or steps)
                            {
                              Target_Position = SER_RXD_VAL;                // Target expressed in motor steps
                            }
                            else
                            {
                              Target_Position = (SER_RXD_VAL * 256) / 100;  // target position expressed in uM
                            }
                              
                            switch(rx_arr[2])
                              {
                                case 'x': // xstage
                                    //stage = "x";

                                    if(XSTAGE_ENABLE)
                                    {
                                        Serial.println("spx OK ");                      // reply ACK to GUI  
                                    }
                                    else
                                    {
                                        Serial.println("X-stage not enabled!");
                                    }                                    
                                   
                                    Target_Position_X = Target_Position;

                                    if(CUR_POS_MOT_X != Target_Position_X)
                                    {
                                        GOTO_X_FLAG = 1 ;                            // set flag high to command driver 
                                        MOVE_TMR_X = 0;                              // set motion timer to 0
                                        VELOCITY_X_CMD = 0;                          // force velocity command off
                                        
                                        if(SPEED_MODE_X == 0)
                                        {
                                            X_APR_STATE = 1;     
                                        }                                                                     
                                    }                                   
                                break;
                                
                                case 'y': // ystage
                                  //stage = "y";
                                   if(YSTAGE_ENABLE)
                                   {
                                      Serial.println("spy OK ");                      // reply ACK to GUI
                                   }
                                   else
                                   {
                                      Serial.println("Y-stage not enabled!");
                                   }
                                    
                                    Target_Position_Y = Target_Position;

                                    if(CUR_POS_MOT_Y != Target_Position_Y)
                                    {
                                        GOTO_Y_FLAG = 1 ;                           // set flag high to command driver   
                                        MOVE_TMR_Y = 0;                             // set motion timer to 0
                                        VELOCITY_Y_CMD = 0;                         // force velocity command off
                                        
                                        if(SPEED_MODE_Y == 0)
                                        {
                                            Y_APR_STATE = 1;     
                                        }                                                                     
                                    }
                                break;
                                
                                case 'z': // zstage
                                   //stage = "z";
                                   if(ZSTAGE_ENABLE)
                                   {
                                    Serial.println("spz OK ");                      // reply ACK to GUI
                                   }
                                   else
                                   {
                                    Serial.println("Z-stage not enabled!");
                                   }
                                    
                                    Target_Position_Z = Target_Position;
                                    
                                    if(CUR_POS_MOT_Z != Target_Position_Z)
                                    {
                                        GOTO_Z_FLAG = 1 ;                               // set flag high to command driver  
                                        MOVE_TMR_Z = 0;                                 // set motor timer to 0
                                        VELOCITY_Z_CMD = 0;                             // force velocity command off
                                        
                                        if(SPEED_MODE_Z == 0)
                                        {
                                            Z_APR_STATE = 1;     
                                        }                                                                                 
                                    }                                             
                                break;
                              }
                          }
                          else
                          {
                             Serial.println("Stage has not been zeroed, zero stage first [z] before attempting motion commands... ");      // bad requestlong  ACK
                             //Serial.println("*");      // bad request short ACK
                          }
                         break;

                         case 'r':                                          // SET response (debug reponse)
                            Serial.println();                               // Spacer
                            rx_str = rx_str.substring(2);                   // strip off first 2 chars
                            SER_RXD_VAL = rx_str.toInt();                   // assign newly rxd data to SER_RXD_VAL
                            
                            if((SER_RXD_VAL >= 0) && (SER_RXD_VAL < 3))     // do value OK/ in range check
                            {
                              Serial.println("sr OK ");                     // reply ACK to GUI
                              Serial.println(SER_RXD_VAL);                  // Echo param data, optional 
                              DBG_MODE = SER_RXD_VAL;
                            }
                            else
                            {
                              Serial.println("*");                          // bad entry response
                            }
                         break;                         

                         case 't':                                          // SET PID setpoint temperature
                            Serial.println();                               // Spacer
                            rx_str = rx_str.substring(2);                   // strip off first 2 chars
                            SER_RXD_VAL = rx_str.toInt();                   // assign newly rxd data to SER_RXD_VAL
                            
                            if((SER_RXD_VAL >= 0) && (SER_RXD_VAL <= MAX_PID_TEMP)) // do value OK/ in range check
                            {
                              Serial.println("st OK ");                     // reply ACK to GUI
                              //Serial.println(SER_RXD_VAL);                  // Echo param data, optional 
                              //SP_TEMP = double(SER_RXD_VAL/100.00);         // divide input value to obtain decimal value
                              RXD_TEMP_VAL = double(SER_RXD_VAL/100.00);         // divide input value to obtain decimal value

                              if(RXD_TEMP_VAL > 220.00)
                              {
                                RXD_TEMP_VAL = 220.00;
                              }
                              
                              SP_TEMP = RXD_TEMP_VAL;
                              //Serial.print("SP_TEMP RXD: ");              // Testing reply ACK to GUI
                              //Serial.println(SP_TEMP);                    // Testing ony
                              EEPROM.put(NVM_TSP_ADR, SP_TEMP);             // write data to NVM (eeprom)
                              SP_HEAT = double(SP_TEMP - DB_TEMP);          // re-calculate deadband adjusted Temperature setpoint for PID task
                              SP_COOL = double(SP_TEMP + DB_TEMP);          // re-calculate deadband adjusted Temperature setpoint for PID task

                              if(DBG_MODE == 2)                               // Init plotter with keys/labels for dataplot
                              {
                                delay(10); 
                                Serial.println("SV_TMP:,PV_TMP:,CV_HEAT:,CV_COOL:,X_SPD:,Y_SPD:,Z_SPD:,");                // Legend/Keys for plotter/chart
                                delay(10);                                      // wait 500 mS before commencing otherwise labels will contain sensor data
                              }
                              
                              delay(10);                                    // delay 10 mSec                             
                            }
                            else
                            {
                              Serial.println("*");  // bad entry response
                            }
                         break;

                         case 'b':                                          // SET PID (dead)band temperature
                            Serial.println();                               // Spacer
                            rx_str = rx_str.substring(2);                   // strip off first 2 chars
                            SER_RXD_VAL = rx_str.toInt();                   // assign newly rxd data to SER_RXD_VAL
                            
                            
                            if((SER_RXD_VAL >= 0) && (SER_RXD_VAL <= MAX_PID_TEMP)) // do value OK/ in range check
                            {
                              Serial.println("sb OK ");                     // reply ACK to GUI
                              Serial.println(SER_RXD_VAL);                  // echo param data, optional 
                              //DB_TEMP = double(SER_RXD_VAL / 100.00);     // modify data to decimal value (incoming data is value x10)
                              RXD_TEMP_VAL = double(SER_RXD_VAL / 100.00);  // modify data to decimal value (incoming data is value x10)
                              DB_TEMP = RXD_TEMP_VAL;                       // 
                              SP_HEAT = double(SP_TEMP - DB_TEMP);          // re-calculate deadband adjusted Temperature setpoint for PID task
                              SP_COOL = double(SP_TEMP + DB_TEMP);          // re-calculate deadband adjusted Temperature setpoint for PID task

                              if(DBG_MODE == 2)                               // Init plotter with keys/labels for dataplot
                              {
                                delay(10); 
                                Serial.println("SV_TMP:,PV_TMP:,CV_HEAT:,CV_COOL:,X_SPD:,Y_SPD:,Z_SPD:,");                // Legend/Keys for plotter/chart
                                delay(10);                                      // wait 500 mS before commencing otherwise labels will contain sensor data
                              }

                              delay(10); 
                              //Serial.print("DB_TEMP RXD: ");              // Testing reply ACK to GUI
                              //Serial.println(DB_TEMP);                    // Testing ony
                              EEPROM.put(NVM_TDB_ADR, DB_TEMP);             // write data to NVM (eeprom)
                              delay(10);                                    // delay 10 mSec                             
                            }
                            else
                            {
                              Serial.println("*");  // bad entry response
                            }
                         break;

                         case 'f':                                          // SET thermocouple temperature OFFSET
                            Serial.println();                               // Spacer
                            Serial.println("sf OK ");                       // reply ACK to GUI                              
                            SET_TEMP_OFFSET() ;                             // call set thermocoouple offset
                         break;

                         case 'u':                                          // Set section ON/OFF ==> 0=OFF, 1=ON
                            Serial.println();                               // Spacer
                            rx_str = rx_str.substring(2);                   // strip off first 2 chars
                            SER_RXD_VAL = rx_str.toInt();                   // assign newly rxd data to SER_RXD_VAL
                            

                            if(SER_RXD_VAL == 1)                            // SUCTION ON 
                            {
                              Serial.println("su OK ");                     // reply ACK to GUI
                              Serial.println(SER_RXD_VAL);                  // Echo param data, optional 
                              SUCTIONMODE = 1;                              // PIDMODE = 1 ==> RUN PID control
                            }

                            if(SER_RXD_VAL == 0)                            // SUCTION OFF
                            {
                              Serial.println("su OK ");                     // reply ACK to GUI
                              Serial.println(SER_RXD_VAL);                  // Echo param data, optional 
                              SUCTIONMODE = 0;                              // PIDMODE = 0 ==> STOP PID control
                            }
                            
                            if((SER_RXD_VAL < 0) || (SER_RXD_VAL > 1))      // bad entry condition check
                            {
                              Serial.println("*");                          // bad entry response
                            }
                          break;   // end case 'u'
                          

                          case 'v':  // (Manual) Velocity control
                            Serial.println();                               // Spacer
                            rx_str = rx_str.substring(3);                   // strip off first 2 chars
                            SER_RXD_VAL = rx_str.toInt();                   // assign newly rxd data to SER_RXD_VAL
                           

                            if((X_INIT_DONE) && (Y_INIT_DONE) && (Z_INIT_DONE))                                 // check if stage has been zeroed ==>  yes, goto pos , NO, error ack
                            {
                                  switch(rx_arr[2])
                                  {
                                    case 'x': // X-stage
      
                                        if((SER_RXD_VAL > -(MAX_SS_SPD)) && (SER_RXD_VAL < MAX_SS_SPD) && (RUNMODE == 1)) // do value OK/ in range check
                                        {
                                          Serial.println("svx OK ");                    // reply ACK to GUI
                                          Serial.println(SER_RXD_VAL);                  // Echo param data, optional 
                                          VELOCITY_X_CMD = float(SER_RXD_VAL)/116;      // divide input value to obtain decimal value
                                          Serial.print("VELOCITY_X_CMD: ");             // Testing reply ACK to GUI
                                          Serial.println(VELOCITY_X_CMD);               // Testing ony  
                                          SET_VELO_X = 1;  
      
                                          if((VELOCITY_X_CMD > 0) && (VELOCITY_X_CMD < 1))
                                          {
                                            VELOCITY_X_CMD = 1;
                                          }
      
                                          if((VELOCITY_X_CMD > -1) && (VELOCITY_X_CMD < 0))
                                          {
                                            VELOCITY_X_CMD = -1;
                                          }
      
                                          if(VELOCITY_X_CMD > 0)
                                          {
                                            xstage.run(FWD, VELOCITY_X_CMD);              // run/dir/speed     
                                          }
                                          if(VELOCITY_X_CMD < 0)
                                          {
                                            xstage.run(REV, abs(VELOCITY_X_CMD));         // run/dir/speed  
                                          }
                                          
                                          if(VELOCITY_X_CMD == 0)
                                          {
                                            xstage.softStop();                            // STOP command
                                          }                                                                  
                                        }
                                        else                                              // bad entry
                                        {
                                          Serial.println("*");                            // bad entry response
                                        }
                                     break; 
      
                                     case 'y': // Y-stage
      
                                        if((SER_RXD_VAL > -(MAX_SS_SPD)) && (SER_RXD_VAL < MAX_SS_SPD) && (RUNMODE == 1)) // do value OK/ in range check
                                        {
                                          Serial.println("svy OK ");                      // reply ACK to GUI
                                          Serial.println(SER_RXD_VAL);                    // Echo param data, optional 
                                          VELOCITY_Y_CMD = float(SER_RXD_VAL)/116;        // divide input value to obtain decimal value
                                          //Serial.print("VELOCITY_Y_CMD: ");             // Testing reply ACK to GUI
                                          //Serial.println(VELOCITY_Y_CMD);               // Testing ony 
                                          SET_VELO_Y = 1; 
      
                                          if((VELOCITY_Y_CMD > 0) && (VELOCITY_Y_CMD < 1))
                                          {
                                            VELOCITY_Y_CMD = 1;
                                          }
      
                                          if((VELOCITY_Y_CMD > -1) && (VELOCITY_Y_CMD < 0))
                                          {
                                            VELOCITY_Y_CMD = -1;
                                          }
                                          
                                          if(VELOCITY_Y_CMD > 0)
                                          {
                                            ystage.run(FWD, VELOCITY_Y_CMD);            // run/dir/speed     
                                          }
                                          
                                          if(VELOCITY_Y_CMD < 0)
                                          {
                                            ystage.run(REV, abs(VELOCITY_Y_CMD));       // run/dir/speed  
                                          }
                                          
                                          if(VELOCITY_Y_CMD == 0)
                                          {
                                            ystage.softStop();                          // STOP command
                                          }                                                                                                      
                                        }
                                        else // bad entry
                                        {                                    
                                          Serial.println("*");  // bad entry response
                                         //Serial.print("VELOCITY_Y_CMD: ");             // Testing ...reply ACK to GUI
                                         //Serial.println(VELOCITY_Y_CMD);               // Testing ony                     
                                        }
                                      break; 
      
                                      case 'z': // Z-stage
      
                                        if((SER_RXD_VAL > -(MAX_SS_SPD)) && (SER_RXD_VAL < MAX_SS_SPD) && (RUNMODE == 1)) // do value OK/ in range check
                                        {
                                          Serial.println("svz OK ");                      // reply ACK to GUI
                                          Serial.println(SER_RXD_VAL);                    // Echo param data, optional 
                                          VELOCITY_Z_CMD = float(SER_RXD_VAL)/116;        // divide input value to obtain decimal value
                                         // Serial.print("VELOCITY_Z_CMD: ");             // Testing reply ACK to GUI
                                         // Serial.println(VELOCITY_Z_CMD);               // Testing ony 
                                          SET_VELO_Z = 1;
      
                                          if((VELOCITY_Z_CMD > 0) && (VELOCITY_Z_CMD < 1))
                                          {
                                            VELOCITY_Z_CMD = 1;
                                          }
      
                                          if((VELOCITY_Z_CMD > -1) && (VELOCITY_Z_CMD < 0))
                                          {
                                            VELOCITY_Z_CMD = -1;
                                          }
                                          
                                          if(VELOCITY_Z_CMD > 0)
                                          {
                                            zstage.run(FWD, VELOCITY_Z_CMD);              // run/dir/speed     
                                          }
                                          
                                          if(VELOCITY_Z_CMD < 0)
                                          {
                                            zstage.run(REV, abs(VELOCITY_Z_CMD));         // run/dir/speed  
                                          }
                                          
                                          if(VELOCITY_Z_CMD == 0)
                                          {
                                            xstage.softStop();                            // STOP command
                                          }                                                                                                       
                                        }
                                        else // bad entry
                                        {
                                          Serial.println("*");                            // bad entry response
                                        }
                                      break;  // end case z 
                               
                               }                              
                               break;         // end  switch(rx_arr[2])
                          }                    
                          else
                          {
                             Serial.println("Stage has not been zeroed, zero stage first [z] before attempting motion commands... ");      // bad requestlong  ACK
                             //Serial.println("*");      // bad request short ACK
                          }
                          break;   // case 'v':  // (Manual) Velocity control
                        
                  }                 //  end  switch(rx_arr[1])
                  break;   


                  

                  case 'g': // GET commands *********************************************************************************
                  
                      switch(rx_arr[1])
                      {
                           case 'a':    // GET ACTOR state      
                             
                              Serial.println();                     // Spacer
                              Serial.println("ga OK ");             // reply ACK to GUI
                              EEPROM.get(NVM_ACC_ADR,STEP_ACCEL);          // GET stepper motor acceleration setting from NVM
                              delay(10);
                              Serial.println(STEP_ACCEL);             // Send data out                                                                                
                           break;

                           case 'd':    // GET ACTOR state      
                             
                              Serial.println();                     // Spacer
                              Serial.println("ga OK ");             // reply ACK to GUI
                              EEPROM.get(NVM_DEC_ADR,STEP_DECEL);          // GET stepper motor acceleration setting from NVM
                              delay(10);
                              Serial.println(STEP_DECEL);             // Send data out                                                                                
                           break;
                        
                           case 'i':    // GET DEVICE  ID  "I"                       
                               switch(rx_arr[2])
                               {
                                  case 'd':    // GET DEVICE ID "D"
                                  {
                                    Serial.println();                     // Spacer
                                    Serial.println("gid OK ");            // reply ACK to GUI
                                    Serial.print(DeviceType);             // Send data out
                                    Serial.println(FW_Version);           // Send data out
                                  }
                               }                             
                            break;
                        

                           case 'c':                                      // Get the stepper driver (hardware) configuration
                              Serial.println();                           // Spacer
                              Serial.println("gc OK ");                   // reply ACK to GUI
                              rx_str = rx_str.substring(3);               // strip off first 2 chars
                              SER_RXD_VAL = rx_str.toInt();               // assign newly rxd data to SER_RXD_VAL
                              //while(driver.busyCheck());                // board not busy check
                              //DRIVER_CFG = driver.getParam(SER_RXD_VAL);// assign config variable
                              Serial.println(DRIVER_CFG);                 // Send data out
                           break;
                           
                           
                           case 'p':                                     
                            switch(rx_arr[2])
                            {
                             //xstage
                              case 'x':                                   // Get position
                                Serial.println();                         // Spacer
                                Serial.println("gpx OK ");                // reply ACK to GUI

                                CUR_POS_MOT_X = xstage.getPos();          // get position of stepper (via internal step accumulator)
                              
                                if(stage_pos_units == 0)                  // units in steps
                                {
                                  Serial.println(CUR_POS_MOT_X);          // send requested data 
                                }
                                else                                      // units in micron
                                {
                                  Serial.println((CUR_POS_MOT_X * 100) /256);   // send requested data 
                                }
                              break;
                             
                             //ystage
                              case 'y':                                   // Get the stepper driver (hardware) configuration
                                Serial.println();                         // Spacer
                                Serial.println("gpy OK ");                // reply ACK to GUI

                                 CUR_POS_MOT_Y = ystage.getPos();         // get position of stepper (via internal step accumulator)
                              
                                if(stage_pos_units == 0)                  // units in steps
                                {
                                  Serial.println(CUR_POS_MOT_Y);          // send requested data 
                                }
                                else                                      // units in micron
                                {
                                  Serial.println((CUR_POS_MOT_Y * 100) /256);   // send requested data 
                                }
                              break;                                      //

                             
                             //zstage
                              case 'z':                                   // Get the stepper driver (hardware) configuration
                                Serial.println();                         // Spacer
                                Serial.println("gpz OK ");                // reply ACK to GUI

                                CUR_POS_MOT_Z = zstage.getPos();          // get position of stepper (via internal step accumulator)
                              
                                if(stage_pos_units == 0)                  // units in steps
                                {
                                  Serial.println(CUR_POS_MOT_Z);          // send requested data 
                                }
                                else                                      // units in micron
                                {
                                  Serial.println((CUR_POS_MOT_Z * 100) /256);   // send requested data 
                                }
                              break;
                            }
                            Serial.println();                             // Spacer
                           break;
                           

                           case 's':                                      // GET stepper motor speed
                            Serial.println();                             // Spacer
                            
                            switch(rx_arr[2])
                            {                              
                              //xstage
                              case 'x':                                   // stepper speed X-stage
                               Serial.println("gsx OK ");                 // reply ACK to GUI
                               Serial.println(CUR_MOT_SPD_X);             // return value                              
                              break;   
                              
                              //xstage
                              case 'y':                                   // stepper speed Y-stage
                               Serial.println("gsy OK ");                 // reply ACK to GUI
                               Serial.println(CUR_MOT_SPD_Y);             // return value    
                              break;   
                                     
                              //xstage
                              case 'z':                                   // stepper speed Z-stage
                               Serial.println("gsz OK ");                 // reply ACK to GUI
                               Serial.println(CUR_MOT_SPD_Z);             // return value    
                              break;  
                            }    
                           break;                           

                           case 't':                                    // GET temperature
                              Serial.println();                         // Spacer
                              Serial.println("gt OK ");                 // reply ACK to GUI
                              Serial.println(PV_TEMP);                  // send requested data  ==> temp in degrees C
                           break;

                           case 'o':                                    // GET output/actor state heater(s)/coolet (TEC)
                              Serial.println();                         // Spacer
                              Serial.println("go OK ");                 // reply ACK to GUI
                              HTR_STATE = digitalRead(ACT_HTR);         // check state of limit switch
                              CLR_STATE = digitalRead(ACT_CLR);         // check state of limit switch
                              Serial.println(HTR_STATE);                // Command Value (0-255)
                              Serial.println(CV_HEAT);                  // Command Value (0-255)
                              Serial.println(CLR_STATE);                // Command Value (0-240)
                              Serial.println(CV_COOL);                  // Command Value (0-24ga0)
                           break;

                           case 'l':                                   // GET limit switch states
                              Serial.println();                         // Spacer
                              Serial.println("gl OK ");                 // reply ACK to GUI
                              
                              //XSTAGE_LSU = digitalRead(LSU_X_PIN);      // read state for debug  
                              //YSTAGE_LSU = digitalRead(LSU_Y_PIN);      // read state for debug  
                              //ZSTAGE_LSU = digitalRead(LSU_Z_PIN);      // read state for debug
                              //XSTAGE_LSD = digitalRead(LSD_X_PIN);      // read state for debug  
                              //YSTAGE_LSD = digitalRead(LSD_Y_PIN);      // read state for debug  
                              //ZSTAGE_LSD = digitalRead(LSD_Z_PIN);      // read state for debug  

                              if(XSTAGE_ENABLE)
                              {
                                 XSTAGE_LSU = digitalRead(LSU_X_PIN);             // read state for debug  
                                 XSTAGE_LSD = digitalRead(LSD_X_PIN);             // read state for debug 
                              }
                              else
                              {
                                 XSTAGE_LSU = 0;                                  // reset to 0  
                                 XSTAGE_LSD = 0;                                  // reset to 0  
                              }
                  
                              if(YSTAGE_ENABLE)
                              {
                                YSTAGE_LSU = digitalRead(LSU_Y_PIN);             // read state for debug
                                YSTAGE_LSD = digitalRead(LSD_Y_PIN);             // read state for debug
                              }
                              else
                              {
                                 YSTAGE_LSU = 0;                                  // reset to 0  
                                 YSTAGE_LSD = 0;                                  // reset to 0  
                              }
                  
                  
                              if(ZSTAGE_ENABLE)
                              {
                                 ZSTAGE_LSD = digitalRead(LSD_Z_PIN);             // read state for debug
                                 ZSTAGE_LSU = digitalRead(LSU_Z_PIN);             // read state for debug 
                                
                              }
                              else
                              {
                                 ZSTAGE_LSD = 0;                                  // reset to 0  
                                 ZSTAGE_LSU = 0;                                  // reset to 0  
                              }  
                              
                              Serial.println(XSTAGE_LSU);               // XSTAGE_LSU, limit switch Xstage MARK
                              Serial.println(XSTAGE_LSD);               // XSTAGE_LSD, limit switch Xstage HOME
                              Serial.println(END_POS_X);                // XSTAGE, numeric end position limit
                              
                              Serial.println(YSTAGE_LSU);               // YSTAGE_LSU, limit switch Ystage MARK
                              Serial.println(YSTAGE_LSD);               // YSTAGE_LSD, limit switch Ystage HOME
                              Serial.println(END_POS_Y);                // YSTAGE, numeric end position limit
                              
                              Serial.println(ZSTAGE_LSU);               // ZSTAGE_LSU, limit switch Zstage MARK
                              Serial.println(ZSTAGE_LSD);               // ZSTAGE_LSD, limit switch Zstage HOME
                              Serial.println(END_POS_Z);                // ZSTAGE, numeric end position limit
                           break;

                           case 'e':                                    // GET controller error state (temp/actors/stepper)
                           // ERROR STATUS BITS: 
                              Serial.println();                             // Spacer
                              Serial.println("ge OK ");                     // reply ACK to GUI                  
                              //Serial.println(GLOBAl_ERR);                 // HOLDS global error state
                              Serial.println(PWR_ERR);                      // HOLDS PWR ERROR, BIT 0 in GLOBAL ERROR
                              Serial.println(ESTOP_SET);                    // HOLDS ESTOP ERROR, BIT 1 in GLOBAL ERROR
                              Serial.println(MOT_ERR);                      // HOLDS STEPPER MOTOR ERROR, BIT 2 in GLOBAL ERROR
                              Serial.println(TC_ERR);                       // HOLDS Thermocouple ERROR, BIT 3 in GLOBAL ERROR
                              Serial.println(HTR_ERR);                      // HOLDS Heater ERROR, BIT 4 in GLOBAL ERROR
                              Serial.println(TEC_ERR);                      // HOLDS TEC ERROR, BIT 5 in GLOBAL ERROR
                              Serial.println(ZERO_ERR);                     // HOLDS ZERO ERROR, BIT 6 in GLOBAL ERROR
                              Serial.println(RTD_ERR);                      // HOLDS RTD ERROR, BIT 7 in GLOBAL ERROR
                              Serial.println(RES08_ERR);                    // HOLDS RES06 ERROR, BIT 8 in GLOBAL ERROR
                              Serial.println(RES09_ERR);                    // HOLDS RES07 ERROR, BIT 9 in GLOBAL ERROR
                              Serial.println(RES10_ERR);                    // HOLDS RES08 ERROR, BIT 10 in GLOBAL ERROR
                              Serial.println(RES11_ERR);                    // HOLDS RES09 ERROR, BIT 11 in GLOBAL ERROR
                              Serial.println(RES12_ERR);                    // HOLDS RES10 ERROR, BIT 12 in GLOBAL ERROR
                              Serial.println(RES13_ERR);                    // HOLDS RES11 ERROR, BIT 13 in GLOBAL ERROR
                              Serial.println(RES14_ERR);                    // HOLDS RES12 ERROR, BIT 14 in GLOBAL ERROR
                              Serial.println(RES15_ERR);                    // HOLDS RES13 ERROR, BIT 15 in GLOBAL ERROR                             
                           break;

                           case 'b':                                    // GET stepper driver board internal status
                              Serial.println();                         // Spacer
                              Serial.println("gb OK ");                 // reply ACK to GUI

                              // XSTAGE STATUS
                              DRIVER_STATUS = xstage.getStatus();       // query of status clears error flag
                              //Serial.println(ERR_STATE);              // send requested data   
                              MOT_STALL_A = bitRead(DRIVER_STATUS,15);  // active low ==> becomes 0 when event is detected     
                              MOT_STALL_B = bitRead(DRIVER_STATUS,14);  // active low ==> becomes 0 when event is detected    
                              MOT_OCD = bitRead(DRIVER_STATUS,13);      // active low ==> becomes 0 when event is detected    
                              MOT_TH_A = bitRead(DRIVER_STATUS,12);
                              MOT_TH_B = bitRead(DRIVER_STATUS,11);        
                              MOT_UVLO_ADC = bitRead(DRIVER_STATUS,10);      
                              MOT_UVLO = bitRead(DRIVER_STATUS,9);      // active low ==> becomes 0 when event is detected    
                              MOT_STCK = bitRead(DRIVER_STATUS,8);   
                              MOT_CMD_ERR = bitRead(DRIVER_STATUS,7); 
                              MOT_STA_A = bitRead(DRIVER_STATUS,6);     // ==> Powerstep manual table 59
                              MOT_STA_B = bitRead(DRIVER_STATUS,5);     // ==> Powerstep manual table 59
                              MOT_DIR = bitRead(DRIVER_STATUS,4);       // 1 = Forward, 0 = Reverse
                              MOT_SW_EVN = bitRead(DRIVER_STATUS,3);
                              MOT_SW_F = bitRead(DRIVER_STATUS,2);
                              MOT_BUSY = bitRead(DRIVER_STATUS,1);
                              MOT_HIZ = bitRead(DRIVER_STATUS,0); 

                              Serial.println(MOT_STALL_A);              // send requested data   
                              Serial.println(MOT_STALL_B);              // send requested data   
                              Serial.println(MOT_OCD);                  // send requested data   
                              Serial.println(MOT_TH_A);                 // send requested data   
                              Serial.println(MOT_TH_B);                 // send requested data   
                              Serial.println(MOT_UVLO_ADC);             // send requested data   
                              Serial.println(MOT_UVLO);                 // send requested data   
                              Serial.println(MOT_STCK);                 // send requested data   
                              Serial.println(MOT_CMD_ERR);              // send requested data   
                              Serial.println(MOT_STA_A);                // send requested data   
                              Serial.println(MOT_STA_B);                // send requested data   
                              Serial.println(MOT_DIR);                  // send requested data   
                              Serial.println(MOT_SW_EVN);               // send requested data   
                              Serial.println(MOT_SW_F);                 // send requested data   
                              Serial.println(MOT_BUSY);                 // send requested data     
                              Serial.println(MOT_HIZ);                  // send requested data 

                              
                              // YSTAGE STATUS
                              DRIVER_STATUS = ystage.getStatus();       // query of status clears error flag
                              //Serial.println(ERR_STATE);              // send requested data   
                              MOT_STALL_A = bitRead(DRIVER_STATUS,15);  // active low ==> becomes 0 when event is detected     
                              MOT_STALL_B = bitRead(DRIVER_STATUS,14);  // active low ==> becomes 0 when event is detected    
                              MOT_OCD = bitRead(DRIVER_STATUS,13);      // active low ==> becomes 0 when event is detected    
                              MOT_TH_A = bitRead(DRIVER_STATUS,12);
                              MOT_TH_B = bitRead(DRIVER_STATUS,11);        
                              MOT_UVLO_ADC = bitRead(DRIVER_STATUS,10);      
                              MOT_UVLO = bitRead(DRIVER_STATUS,9);      // active low ==> becomes 0 when event is detected    
                              MOT_STCK = bitRead(DRIVER_STATUS,8);   
                              MOT_CMD_ERR = bitRead(DRIVER_STATUS,7);   // ==> Becomes 1 when a command is send when motor is busy
                              MOT_STA_A = bitRead(DRIVER_STATUS,6);     // ==> Powerstep manual table 59
                              MOT_STA_B = bitRead(DRIVER_STATUS,5);     // ==> Powerstep manual table 59
                              MOT_DIR = bitRead(DRIVER_STATUS,4);       // 1 = Forward, 0 = Reverse
                              MOT_SW_EVN = bitRead(DRIVER_STATUS,3);
                              MOT_SW_F = bitRead(DRIVER_STATUS,2);
                              MOT_BUSY = bitRead(DRIVER_STATUS,1);      // State is 1 when driver is actively driving the stepper
                              MOT_HIZ = bitRead(DRIVER_STATUS,0); 

                              Serial.println(MOT_STALL_A);              // send requested data   
                              Serial.println(MOT_STALL_B);              // send requested data   
                              Serial.println(MOT_OCD);                  // send requested data   
                              Serial.println(MOT_TH_A);                 // send requested data   
                              Serial.println(MOT_TH_B);                 // send requested data   
                              Serial.println(MOT_UVLO_ADC);             // send requested data   
                              Serial.println(MOT_UVLO);                 // send requested data   
                              Serial.println(MOT_STCK);                 // send requested data   
                              Serial.println(MOT_CMD_ERR);              // send requested data   
                              Serial.println(MOT_STA_A);                // send requested data   
                              Serial.println(MOT_STA_B);                // send requested data   
                              Serial.println(MOT_DIR);                  // send requested data   
                              Serial.println(MOT_SW_EVN);               // send requested data   
                              Serial.println(MOT_SW_F);                 // send requested data   
                              Serial.println(MOT_BUSY);                 // send requested data     
                              Serial.println(MOT_HIZ);                  // send requested data

                              
                              // ZSTAGE STATUS
                              DRIVER_STATUS = zstage.getStatus();       // query of status clears error flag
                              //Serial.println(ERR_STATE);              // send requested data   
                              MOT_STALL_A = bitRead(DRIVER_STATUS,15);  // active low ==> becomes 0 when event is detected     
                              MOT_STALL_B = bitRead(DRIVER_STATUS,14);  // active low ==> becomes 0 when event is detected    
                              MOT_OCD = bitRead(DRIVER_STATUS,13);      // active low ==> becomes 0 when event is detected    
                              MOT_TH_A = bitRead(DRIVER_STATUS,12);
                              MOT_TH_B = bitRead(DRIVER_STATUS,11);        
                              MOT_UVLO_ADC = bitRead(DRIVER_STATUS,10);      
                              MOT_UVLO = bitRead(DRIVER_STATUS,9);      // active low ==> becomes 0 when event is detected    
                              MOT_STCK = bitRead(DRIVER_STATUS,8);   
                              MOT_CMD_ERR = bitRead(DRIVER_STATUS,7); 
                              MOT_STA_A = bitRead(DRIVER_STATUS,6);     // ==> Powerstep manual table 59
                              MOT_STA_B = bitRead(DRIVER_STATUS,5);     // ==> Powerstep manual table 59
                              MOT_DIR = bitRead(DRIVER_STATUS,4);       // 1 = Forward, 0 = Reverse
                              MOT_SW_EVN = bitRead(DRIVER_STATUS,3);
                              MOT_SW_F = bitRead(DRIVER_STATUS,2);
                              MOT_BUSY = bitRead(DRIVER_STATUS,1);
                              MOT_HIZ = bitRead(DRIVER_STATUS,0); 

                              Serial.println(MOT_STALL_A);              // send requested data   
                              Serial.println(MOT_STALL_B);              // send requested data   
                              Serial.println(MOT_OCD);                  // send requested data   
                              Serial.println(MOT_TH_A);                 // send requested data   
                              Serial.println(MOT_TH_B);                 // send requested data   
                              Serial.println(MOT_UVLO_ADC);             // send requested data   
                              Serial.println(MOT_UVLO);                 // send requested data   
                              Serial.println(MOT_STCK);                 // send requested data   
                              Serial.println(MOT_CMD_ERR);              // send requested data   
                              Serial.println(MOT_STA_A);                // send requested data   
                              Serial.println(MOT_STA_B);                // send requested data   
                              Serial.println(MOT_DIR);                  // send requested data   
                              Serial.println(MOT_SW_EVN);               // send requested data   
                              Serial.println(MOT_SW_F);                 // send requested data   
                              Serial.println(MOT_BUSY);                 // send requested data     
                              Serial.println(MOT_HIZ);                  // send requested data 
                           break;

                           default:                                     // Not a valid command char / string
                              Serial.println();
                              //Serial.println("Command Invalid"); 
                              Serial.println("Command not valid, please enter correct command and/or parameter");  // debug response string
                       }
                  break; 

                  case 'f': // FORCE ON/OFF commands *********************************************************************************
                  
                      switch(rx_arr[1])
                      {   
                          case 'c':  // Force Cooler ON/OFF  (0-255)  
                             Serial.println();                                // Spacer
                            rx_str = rx_str.substring(2);                     // strip off first 2 chars
                            SER_RXD_VAL = rx_str.toInt();                     // assign newly rxd data to SER_RXD_VAL
                            
                            if((SER_RXD_VAL >= 0) && (SER_RXD_VAL < 255) && (RUNMODE == 0)) // do value OK/ in range check
                            {
                              Serial.println("fc OK ");                       // reply ACK to GUI
                              Serial.println(SER_RXD_VAL);                    // Echo param data, optional 
                              FORCE_CLR = SER_RXD_VAL;                        // divide input value to obtain decimal value
                             // Serial.print("FORCE_CLR: ");                  // Testing reply ACK to GUI
                             // Serial.println(FORCE_CLR);                    // Testing ony
                              delay(10);                                      // delay 10 mSec
                              
                              if(DBG_MODE == 2)                               // Init plotter with keys/labels for dataplot
                              {
                                delay(10); 
                                Serial.println("SV_TMP:,PV_TMP:,CV_HEAT:,CV_COOL:,X_SPD:,Y_SPD:,Z_SPD:,");                // Legend/Keys for plotter/chart
                                delay(10);                                    // wait 500 mS before commencing otherwise labels will contain sensor data
                              }
                            }
                            else // bad entry
                            {
                              Serial.println("*");  // bad entry response
                            }
                          break;             

                          case 'h':  // Force cooler ON/OFF (0-255)
                            Serial.println();                               // Spacer
                            rx_str = rx_str.substring(2);                   // strip off first 2 chars
                            SER_RXD_VAL = rx_str.toInt();                   // assign newly rxd data to SER_RXD_VAL
                            
                            if((SER_RXD_VAL >= 0) && (SER_RXD_VAL < 255) && (RUNMODE == 0)) // do value OK/ in range check
                            {
                              Serial.println("fh OK ");                     // reply ACK to GUI
                              Serial.println(SER_RXD_VAL);                  // Echo param data, optional

                              delay(10); 
                               
                              if(DBG_MODE == 2)                             // Init plotter with keys/labels for dataplot
                              {
                                delay(10);                         
                                Serial.println("SV_TMP:,PV_TMP:,CV_HEAT:,CV_COOL:,X_SPD:,Y_SPD:,Z_SPD:,");                // Legend/Keys for plotter/chart
                                delay(10);                                  // wait 500 mS before commencing otherwise labels will contain sensor data
                              }
                  
                              FORCE_HTR = SER_RXD_VAL;                      // divide input value to obtain decimal value
                              //Serial.print("FORCE_HTR: ");                // Testing reply ACK to GUI
                              //Serial.println(FORCE_HTR);                  // Testing ony
                              //delay(10);                                  // delay 10 mSec
                            }
                            else // bad entry
                            {
                              Serial.println("*");  // bad entry response
                            }
                          break;
                          
                          case 'p':                                         // Force PIDMODE ON/OFF (0 / 1)
                            Serial.println();                               // Spacer
                            rx_str = rx_str.substring(2);                   // strip off first 2 chars
                            SER_RXD_VAL = rx_str.toInt();                   // assign newly rxd data to SER_RXD_VAL
                            
                            if(SER_RXD_VAL == 1)                            // PIDMODE ON ==> PID CONTROL ON
                            {
                              Serial.println("fp OK ");                     // reply ACK to GUI
                              Serial.println(SER_RXD_VAL);                  // Echo param data, optional 
                              PIDMODE = 1;                                  // PIDMODE = 1 ==> RUN PID control
                              if(DBG_MODE == 2)                             // Init plotter with keys/labels for dataplot
                              {
                                delay(10); 
                                Serial.println("SV_TMP:,PV_TMP:,CV_HEAT:,CV_COOL:,X_SPD:,Y_SPD:,Z_SPD:,");                // Legend/Keys for plotter/chart
                                delay(10);                                  // wait 500 mS before commencing otherwise labels will contain sensor data
                              }
                            }

                            if(SER_RXD_VAL == 0)                            // PIDMODE OFF ==> PID CONTROL OFF
                            {
                              Serial.println("fp OK ");                     // reply ACK to GUI
                              Serial.println(SER_RXD_VAL);                  // Echo param data, optional 
                              PIDMODE = 0;                                  // PIDMODE = 0 ==> STOP PID control
                              if(DBG_MODE == 2)                             // Init plotter with keys/labels for dataplot
                              {
                                delay(10); 
                                Serial.println("SV_TMP:,PV_TMP:,CV_HEAT:,CV_COOL:,X_SPD:,Y_SPD:,Z_SPD:,");                // Legend/Keys for plotter/chart
                                delay(10);                                  // wait 500 mS before commencing otherwise labels will contain sensor data
                              }
                            }
                            
                            if((SER_RXD_VAL > 1) || (SER_RXD_VAL < 0))      // bad entry
                            {
                              Serial.println("*");  // bad entry response
                            }
                          break; // end case p
                      }
                      break; // end case f
                    

                  default: // Not a valid command char / string
                     Serial.println();
                     //Serial.println("Command Invalid"); 
                     Serial.println("Command not valid, please enter correct command and/or parameter");  // debug response string
              }
              
              rx_str = "";                                // clear the string for re-use
              rx_index = 0;                               // reset array index to 0
              
            }// newline detected
    }// while (serial available())
}// CheckSerial

// *****************************    UpdatePID  (temperature control)    *************************************************************************************************
//  HEAT and COOL both have their own/seperated PID control loops
//  HEAT and COLD share the same setpoint with optional variable deadband
//  OUTPUTS of PID loops (CV_COOL and CV_HEAT) are utilized in later functions for output control
// **********************************************************************************************************************************************************************
void UpdatePID()                                       // default 5Hz update rate, change update rate through UPD_PID_INTVAL value 
{  
  if((UPD_PID_CNT >= UPD_PID_INTVAL) && (uptime > SEN_INIT_TIME))                    // 5Hz update rate, 
  {
     HEAT_PID.Compute();                               // Do a PID control iteration for heating process
     COOL_PID.Compute();                               // Do a PID control iteration for cooling process  

     CV_HEAT  = double(CV_HEAT * GAIN_HTR / 100);      // multiply with scaling factor and offset

     if(CV_HEAT > 0)
     {
        CV_HEAT = CV_HEAT + OFS_HTR;                   // add offset only when PID > 0
     }
     else
     {
        CV_HEAT = 0;                                   // reset to zero
     }

     if (CV_HEAT > MAX_PWM_HTR)
     {
      CV_HEAT = MAX_PWM_HTR;                          // clip max
     }

     if (CV_HEAT < 0)
     {
        CV_HEAT = 0;                                  // clip min
     }     

     CV_COOL  = double(CV_COOL * GAIN_TEC / 100);     // multiply with scaling factor and offset

     if(CV_COOL > 0)                                  // check for value to insert offset
     {
        CV_COOL = CV_COOL + OFS_TEC;                  // add offset only when PID > 0
     }
     else
     {
      CV_COOL = OFS_TEC;                              // reset to zero
     }     

     if(CV_COOL > MAX_PWM_TEC)                        // check for max value
     {
        CV_COOL = MAX_PWM_TEC;                        // clip to max
     }

     if(CV_COOL < 0)                                  // clip to 0
     {
        CV_COOL = OFS_TEC;                            // clip to min
     }

     if(!PIDMODE)                                     // override values by PIDMODE, 0 = NO PID control out values, 1 = PID control output values
     {
        CV_COOL = 0;                                  // set to 0
        CV_HEAT = 0;                                  // set to 0
     }

     CV_TEC = uint8_t(CV_COOL);

     //TPD_PINSTATE = !TPD_PINSTATE;                  // Toggle, LED STATE 
     //digitalWrite(TPD_PIN, TPD_PINSTATE);           // Override pin state, for debugging purposes
       
     UPD_PID_CNT = 0;                                 // reset scheduling timer
  }
}
// -- END OF UPDATE PID


//************************************************************  UpdateActors  *********************************************************************************************
// - Update state of actors/outputs
// - Actors/outputs are: heater (24Vdc), TEC/Peltier (2.1 Vdc), Front Panel LEDS (<4.0 Vdc)
// - Actors are heater and cooler are governed by PWM, resolution is 8 bits (0-255).
// - Front panel leds indicate the ON/OFF state of an actor
// **********************************************************************************************************************************************************************
void UpdateActors()
{
    if(UPD_TEC_CNT > UPD_TEC_INTVAL)
    {
         if((CV_TEC > 0) && (RUNMODE == 1))
         {
           digitalWrite(ACT_CLR, HIGH);                  // Switch ON
           digitalWrite(CLR_LED, HIGH);                  // TURN LED ON
           //digitalWrite(TPD_PIN, HIGH);                // Override pin state, for debugging purposes
           UPD_TEC_TMR = 0;
           TEC_ACT = 1;  
         }
         else
         {
            if(FORCE_CLR == 0) // FORCE OFF CHECK
            {
               digitalWrite(ACT_CLR, LOW);               // Switch OFF
               digitalWrite(CLR_LED, LOW);               // TURN LED OFF
               //digitalWrite(TPD_PIN, LOW);             // Override pin state, for debugging purposes
               TEC_ACT = 0;
            }          
         }

         UPD_TEC_CNT = 0;                                // reset scheduling timer
    }   // if(UPD_TEC_CNT > UPD_TEC_INTVAL)

    if(UPD_TEC_TMR > CV_TEC || (CV_TEC == 0) || RUNMODE == 0) // Check for deactivation command
    {
       if(FORCE_CLR == 0) // FORCE OFF CHECK
       {
         digitalWrite(ACT_CLR, LOW);                     // De-energize cooler
         digitalWrite(CLR_LED, LOW);                     // TURN LED OFF
         //digitalWrite(TPD_PIN, LOW);                   // Override pin state, for debugging purposes
         TEC_ACT = 0;
       }
    }
  
   if(UPD_ACT_CNT > UPD_ACT_INTVAL)                     // ACTOR UPDATE RATE
   {
     PSU_MOT_VAL  = (analogRead(PSU_MOT));              // check voltage stepper motor PSU ==> ADC conv. mV/step
     PSU_TCO_VAL  = (analogRead(PSU_TCO));              // check voltage temp. control PSU ==> ADC conv. mV/step

     if((SUCTIONMODE) && (RUNMODE == 1))                // check for suction pump mode/state
     {
        digitalWrite(ACT_SUC, HIGH);                    // Energize Suction pump
     }
     else
     {
        digitalWrite(ACT_SUC, LOW);                     // De-energize Suction pump
     }
     

    // CV_HEAT
     if((CV_HEAT > 0) && (RUNMODE == 1))                // Check for heater active
     {
        digitalWrite(ACT_HTR, HIGH);                    // Energize heater
        analogWrite(ACT_HTR, CV_HEAT);                  // SET PWM %
        digitalWrite(HTR_LED, HIGH);                    // TURN LED ON
     }
     else
     {
        CV_HEAT = 0;                                    // De-energize heater
        digitalWrite(ACT_HTR, LOW);                     // De-energize heater
        analogWrite(ACT_HTR, CV_HEAT);                  // SET PWM %
        digitalWrite(HTR_LED, LOW);                     // TURN LED OFF
     }

     
    
     // ESTOP CHECK
     if((PSU_MOT_VAL < 200) && (PSU_TCO_VAL < 200))      // check voltage of power supply motor and power supply temp control
     {
        while(xstage.busyCheck());                       // wait until driver is not busy anymore
        xstage.softStop();                               // soft stop prevents errors in the next operation
        while(ystage.busyCheck());                       // wait until driver is not busy anymore
        ystage.softStop();                               // soft stop prevents errors in the next operation
        while(zstage.busyCheck());                       // wait until driver is not busy anymore
        zstage.softStop();                               // soft stop prevents errors in the next operatio
        bitWrite(GLOBAL_ERR,0,1);
        RUNMODE   = 0;                                   // put controller into stopmode
        FORCE_CLR = 0;                                   // FORCE cooler/TEC OFF when in stopmode
        FORCE_HTR = 0;                                   // FORCE heater OFF when in stopmode
        ESTOP_SET = 1;                                   // RESET ESTOP SET FLAG 
     }
     else
     {
        if(ESTOP_SET == 1)
        {
            if((PSU_MOT_VAL > 200) && (PSU_TCO_VAL > 200))  //Typical values around 800/1024-ish for 24Vdc PSU
            bitWrite(GLOBAL_ERR,0,0);                       // RESET ESTOP ERROR FLAG
            ESTOP_CNT++;                                    // Increment ESTOP counter
            xstage.getStatus();                             // get status from driver board, this get clears error flags
            ystage.getStatus();                             // get status from driver board, this get clears error flags
            zstage.getStatus();                             // get status from driver board, this get clears error flags
            ESTOP_SET = 0;                                  // RESET ESTOP SET FLAG 
         }
     }


      // Power/PSU status check and signaling
     PSU_CHK_VOLTAGE  = (analogRead(PWR_PIN)) * 25.22;      // 24.24 Vdc = aprox 961 ADC steps

     if(PSU_CHK_VOLTAGE < 9000) // PSU is aprox 24Vdc so 9000mV/9Vdc is safe threshold
     {
       PWR_ERR = 1;
       digitalWrite(PWR_LED, LOW);               // ENERGIZE TEC module
     }
     else
     {
       PWR_ERR = 0;
       digitalWrite(PWR_LED, HIGH);               // ENERGIZE TEC module
     }
     

     // Driver status check and signaling
      XSTAGE_STATUS = xstage.getStatus();       // clears error flags when status is read
      YSTAGE_STATUS = ystage.getStatus();       // clears error flags when status is read
      ZSTAGE_STATUS = zstage.getStatus();       // clears error flags when status is read

    
      if((!XSTAGE_STATUS) && (!XSTAGE_STATUS) && (!XSTAGE_STATUS) && (!PWR_ERR))
      {
        MOT_ERR = 1;
       
      }
      else
      {
        MOT_ERR = 0;       
      }
     

     // RUNMODE handling
     if(RUNMODE == 1) // RUNNING 
     {
       if(PIDMODE == 1)
       {
          digitalWrite(RUNMODE_LED, HIGH);            //  RUNMODE LED on when in runmode 
       }       
     }
     else // STOPPED
     {  
        // if(PIDMODE == 0)
        // {
        //    digitalWrite(RUNMODE_LED, LOW);         //  RUNMODE LED on when in runmode 
        // }

         digitalWrite(RUNMODE_LED, LOW);              //  RUNMODE LED on when in runmode 
                 
         while(xstage.busyCheck());                   // wait until driver is not busy anymore
         xstage.softStop();                           // soft stop prevents errors in the next operation
         while(ystage.busyCheck());                   // wait until driver is not busy anymore
         ystage.softStop();                           // soft stop prevents errors in the next operation
         while(zstage.busyCheck());                   // wait until driver is not busy anymore
         zstage.softStop();                           // soft stop prevents errors in the next operation

         if(FORCE_HTR > 0)
         {
           digitalWrite(ACT_HTR, HIGH);               // ENERGIZE HEATER
           analogWrite(ACT_HTR, FORCE_HTR);           // SET PWM %
           digitalWrite(HTR_LED, HIGH);               // TURN LED ON
         }
         else
         {
           digitalWrite(ACT_HTR, LOW);                // DE-ENERGIZE HEATER
           analogWrite(ACT_HTR, 0);                   // SET PWM %
           digitalWrite(HTR_LED, LOW);                // TURN LED OFF
         }

         if(FORCE_CLR > 0)
         {
           digitalWrite(ACT_CLR, HIGH);               // ENERGIZE TEC module
           digitalWrite(CLR_LED, HIGH);               // TURN LED ON
         }
         else
         {
           digitalWrite(ACT_CLR, LOW);                // DE-ENERGIZE TEC module
           digitalWrite(CLR_LED, LOW);                // TURN LED OFF
         }
     }

      UPD_ACT_CNT = 0;                                // reset scheduling timer
   } 

   // LED signaling/handling 
   if(UPD_SIG_CNT > UPD_SIG_INTVAL )                  // check update interval
   {   
        if((RUNMODE == 1) && (PIDMODE == 0))          // Motor Drive only RUNMODE ==> flashing blue
        {
          RUN_STATE =! RUN_STATE;                     //  toggle, LED STATE           
          digitalWrite(RUNMODE_LED, RUN_STATE);       //  Override pin state, for debugging purposes   
        }  

          /*
          bool PWR_ERR             = 0;                  // HOLDS PWR ERROR, BIT 0 in GLOBAL ERROR
          bool ESTOP_SET           = 0;                  // HOLDS ESTOP ERROR, BIT 1 in GLOBAL ERROR
          bool RTD_ERR             = 0;                  // HOLDS RTD ERROR, BIT 2 in GLOBAL ERROR
          bool TC_ERR              = 0;                  // HOLDS Thermocouple ERROR, BIT 3 in GLOBAL ERROR
          bool ZERO_ERR            = 0;                  // HOLDS PWR ERROR, BIT 4 in GLOBAL ERROR
          bool MOT_ERR             = 0;                  // HOLDS motor/steper ERROR, BIT 5 in GLOBAL ERROR
          bool HTR_ERR             = 0;                  // HOLDS RES06 ERROR, BIT 6 in GLOBAL ERROR
          bool TEC_ERR             = 0;                  // HOLDS RES07 ERROR, BIT 7 in GLOBAL ERROR
          bool RES08_ERR           = 0;                  // HOLDS RES08 ERROR, BIT 8 in GLOBAL ERROR
          bool RES09_ERR           = 0;                  // HOLDS RES09 ERROR, BIT 9 in GLOBAL ERROR
          bool RES10_ERR           = 0;                  // HOLDS RES10 ERROR, BIT 10 in GLOBAL ERROR
          bool RES11_ERR           = 0;                  // HOLDS RES11 ERROR, BIT 11 in GLOBAL ERROR
          bool RES12_ERR           = 0;                  // HOLDS RES12 ERROR, BIT 12 in GLOBAL ERROR
          bool RES13_ERR           = 0;                  // HOLDS RES13 ERROR, BIT 13 in GLOBAL ERROR
          bool RES14_ERR           = 0;                  // HOLDS RES14 ERROR, BIT 14 in GLOBAL ERROR
          bool RES15_ERR           = 0;                  // HOLDS RES15 ERROR, BIT 15 in GLOBAL ERROR
          */
    
        
        if(ESTOP_SET || RTD_ERR || TC_ERR || ZERO_ERR || MOT_ERR || HTR_ERR ||TEC_ERR )                           // check value
        {
           ERR_LEDSTATE = !ERR_LEDSTATE;              //  toggle, LED STATE 
           //digitalWrite(ERR_LED, ERR_LEDSTATE);       //  Override pin state, for debugging purposes   
        }
        else
        {
           digitalWrite(ERR_LED, LOW);                // reset led state
        }
        
        UPD_SIG_CNT = 0;                              // reset scheduling timer
        
   } // end UPD_TEC_INTVAL
  
} // end UpdateActors()




// *****************************   Debug Printout      ****************************************************************************************************
// Contains section for serial print  (terminal usage)
// Contains plotter section for use with a Arduino IDE plotter to plot/debug variables
// Note: serial prints will not print out when plotter is enabled 
// ********************************************************************************************************************************************************
void DebugPrint()             // contains moutiple debug modes
{
   if(MSEC_CNT > 999)         // Interval check 
   {
      uptime++;               // increment uptime timer (1 sec tick)
      MSEC_CNT = 0;           // reset millisec timer
   }
  
    if(DBG_MODE > 0)          // DBG_MODE ==> 0=OFF, 1=PRINT-OUT, 2=PLOTTER
    {
          if((UPD_DBG_CNT >= UPD_DBG_INTVAL) &&  (DBG_MODE == 1)) // Debug data when interval has passed (1 hz)
          {
            Serial.println("");                         // SPACER
            Serial.println("************************  DEBUG DATA  ************************************");            // Debug data header
            Serial.println(""); 
            Serial.print("uptime: "); 
            Serial.print(uptime);        
            Serial.println(" secs"); 

            Serial.print("MOT_ERR: "); 
            Serial.println(MOT_ERR);   
            Serial.print("TEC_ERR: "); 
            Serial.println(TEC_ERR); 
            Serial.print("ZERO_ERR: "); 
            Serial.println(ZERO_ERR); 
             Serial.print("TC_ERR: "); 
            Serial.println(TC_ERR); 

          
               



           
            Serial.print("PSU Voltage: "); 
            Serial.println(PSU_CHK_VOLTAGE); 
            
            // Temperature = (Vout - 1250) / 5 ,  e.g.: if voltage from module is 1500mV (1.5 Vdc), temperature is (1500 - 1250) / 5 = 50°C
            TC_TEMP_RAW = analogRead(TC_PIN); // read adc channel (10 bit res.)    
                    
            if(XSTAGE_ENABLE)
            {
               XSTAGE_LSU = digitalRead(LSU_X_PIN);             // read state for debug  
               XSTAGE_LSD = digitalRead(LSD_X_PIN);             // read state for debug 
            }
            else
            {
               XSTAGE_LSU = 0;                                  // reset to 0  
               XSTAGE_LSD = 0;                                  // reset to 0  
            }

            if(YSTAGE_ENABLE)
            {
              YSTAGE_LSU = digitalRead(LSU_Y_PIN);             // read state for debug
              YSTAGE_LSD = digitalRead(LSD_Y_PIN);             // read state for debug
            }
            else
            {
               YSTAGE_LSU = 0;                                  // reset to 0  
               YSTAGE_LSD = 0;                                  // reset to 0  
            }


            if(ZSTAGE_ENABLE)
            {
               ZSTAGE_LSD = digitalRead(LSD_Z_PIN);             // read state for debug
               ZSTAGE_LSU = digitalRead(LSU_Z_PIN);             // read state for debug 
              
            }
            else
            {
               ZSTAGE_LSD = 0;                                  // reset to 0  
               ZSTAGE_LSU = 0;                                  // reset to 0  
            }  
            
            Serial.println("");  
            Serial.print("XSTAGE_LSU: ");                    // oversampled and filtered voltage on ADC pin
            Serial.println(XSTAGE_LSU);                      // oversampled and filtered voltage on ADC pin
            Serial.print("XSTAGE_LSD: ");                    // oversampled and filtered voltage on ADC pin
            Serial.println(XSTAGE_LSD);                      // oversampled and filtered voltage on ADC pin

            Serial.println("");  
            Serial.print("YSTAGE_LSU: ");                    // oversampled and filtered voltage on ADC pin
            Serial.println(YSTAGE_LSU);                      // oversampled and filtered voltage on ADC pin
            Serial.print("YSTAGE_LSD: ");                    // oversampled and filtered voltage on ADC pin
            Serial.println(YSTAGE_LSD);                      // oversampled and filtered voltage on ADC pin            

            Serial.println("");  
            Serial.print("ZSTAGE_LSU: ");                    // oversampled and filtered voltage on ADC pin
            Serial.println(ZSTAGE_LSU);                      // oversampled and filtered voltage on ADC pin
            Serial.print("ZSTAGE_LSD: ");                    // oversampled and filtered voltage on ADC pin
            Serial.println(ZSTAGE_LSD);                      // oversampled and filtered voltage on ADC pin
        
            //Serial.print("Thermocouple RAW ADC value (10 bit): ");      // display raw adc value in 10 bit resolution
            //Serial.println(TC_TEMP_RAW); 
            
            // TC_TEMP_CAL = float(ADC_INP_mV - TC_BaseVoltage) / 5;      // calculate Thermo-couple temp. from Millivolt value
            Serial.print("Thermocouple Temp. (Deg C): "); 
            Serial.println(TC_TEMP_CAL); 
        
            //Serial.print("ADC_INP_mV): ");              // oversampled and filtered voltage on ADC pin
            //Serial.println(ADC_INP_mV);                 // oversampled and filtered voltage on ADC pin

            Serial.print("RUNMODE: ");                    // 
            Serial.println(RUNMODE);                      // 

            Serial.print("PIDMODE: ");                    // 
            Serial.println(PIDMODE);                      // 

            Serial.print("SPEED_MODE_X: ");               // SPEED_MODE
            Serial.println(SPEED_MODE_X);                 // SPEED_MODE
            Serial.print("SPEED_MODE_Y: ");               // SPEED_MODE
            Serial.println(SPEED_MODE_Y);                 // SPEED_MODE
            Serial.print("SPEED_MODE_Z: ");               // SPEED_MODE
            Serial.println(SPEED_MODE_Z);                 // SPEED_MODE

            Serial.print("SP_TEMP: ");                    // oversampled and filtered voltage on ADC pin
            Serial.println(SP_TEMP);                      // oversampled and filtered voltage on ADC pin

            Serial.print("OS_TEMP: ");                    // THERMOCOUPLE OLD VALUE
            Serial.println(OS_TEMP);                      // THERMOCOUPLE OLD VALUE

            Serial.print("SP_HEAT: ");                    // oversampled and filtered voltage on ADC pin
            Serial.println(SP_HEAT);                      // oversampled and filtered voltage on ADC pin

            Serial.print("SP_COOL: ");                    // oversampled and filtered voltage on ADC pin
            Serial.println(SP_COOL);                      // oversampled and filtered voltage on ADC pin

            Serial.print("PV_TEMP: ");                    // oversampled and filtered voltage on ADC pin
            Serial.println(PV_TEMP);                      // oversampled and filtered voltage on ADC pin

            Serial.print("CV_HEAT: ");                    // OUTPUT VALUE
            Serial.println(CV_HEAT);                      // OUTPUT VALUE

            Serial.print("CV_COOL: ");                    // OUTPUT VALUE
            Serial.println(CV_COOL);                      // OUTPUT VALUE

            Serial.print("VREF_RAW: ");                   // VREF
            Serial.println(VREF_RAW);                     // VREF

            Serial.print("VREF_OSV: ");                   // VREF OVERSAMPLE
            Serial.println(VREF_OSV);                     // VREF OVERSAMPLE

            Serial.print("TC_INP_OLD: ");                 // THERMOCOUPLE OLD VALUE
            Serial.println(TC_INP_OLD);                   // THERMOCOUPLE OLD VALUE  
        
            UPD_DBG_CNT = 0;                              // reset update counter
            
          }

          if((UPD_PLT_CNT >= UPD_PLT_INTVAL) && (DBG_MODE == 2)) // print data for plotter when interval has passed
          {
              //  Plotter key/legend labels are:
              //  Serial.println("SV_TMP;,PV_TMP:,CV_HEAT:,CV_COOL:,X_SPD:,Y_SPD:,Z_SPD:,");                // Legend/Keys for plotter/chart
              
              Serial.print(SP_TEMP);           // Setpoint temperature
              Serial.print(" ");               // separator
              Serial.print(PV_TEMP);           // Actual Temperature value
              Serial.print(" ");               // separator
              Serial.print(CV_HEAT);           // Command value heater
              Serial.print(" ");               // separator
              Serial.print(CV_COOL);           // Command value heater
              Serial.print(" ");               // separator
              Serial.print(LIN_X_SPD);         // Linear speed of spindle
              Serial.print(" ");               // separator
              Serial.print(LIN_Y_SPD);         // Linear speed of spindle
              Serial.print(" ");               // separator
              Serial.print(LIN_Z_SPD);         // Linear speed of spindle
              Serial.println();                // Terminator
              
              UPD_PLT_CNT = 0;                 // reset update counter
          }
          
    }
}
// -- END of DEBUGPRINT

//************************************************************************************************************************************************
//                                                            MAIN LOOP 
// calls functions below sequentially 
// Timing of function is done within the function via timers incremented in the timer ISR
// Only use DBG_MODE = 0 or 2 for application, use DBG_MODE = 1 only for debugging, since the printouts cause a loss in performance due to (printout) delays
// 
//************************************************************************************************************************************************
void loop()               // main loop
{
  CheckSerialRXD();       // Check for serial command data from GUI (PC/USB) 

  ReadTemperature();      // Readout temperature (via thermocouple and optionaly via PT100)  

  UpdatePID();            // PID control (Temperature control through heater and TEC)  

  UpdateActors();         // Update actors (Cooler, Heater & Suction pump)

  UpdateStepper();        // Update stepper motor position/velocity (manual or via PC)
  
  DebugPrint();           // Debug data/Plotter print-outs via serial port (PC/USB)
}
// -- END of MAIN LOOP


// ****************************************   Timer1 ISR (set to 1 mSec)  **************************************************************************
ISR(TIMER1_OVF_vect)        // ISR label for Timer1
{
  TCNT1 = 65474;            // reload timer1 ==> overflows every 1 mSec (65535 - 65473 = 62 ==> 62 * 16 (uSec) = 992 uSec)      

  UPD_TCR_CNT++;            // update read thermocouple internal timer/counter
  UPD_PID_CNT++;            // update PID internal timer/counter
  UPD_ACT_CNT++;            // update actor internal timer/counter
  UPD_MOT_CNT++;            // update motor drive internal timer/counter
  UPD_DBG_CNT++;            // update debug internal timer/counter
  UPD_PLT_CNT++;            // update plotter internal timer/counter
  UPD_RTD_CNT++;            // update RTD read counter
  UPD_TEC_TMR++;            // update actor internal timer/counter
  UPD_TEC_CNT++;            // update TEC/PELTIER timer/counter
  UPD_SIG_CNT++;            // update err handler timer/counter
  MSEC_CNT++;               // update millisec timer
  MOVE_TMR_X++;             // Move/motion timer stepper X
  MOVE_TMR_Y++;             // Move/motion timer stepper Y
  MOVE_TMR_Z++;             // Move/motion timer stepper Z

  //ERR_LEDSTATE = !ERR_LEDSTATE;                  // Toggle, LED STATE 
  //digitalWrite(TPD_PIN, ERR_LEDSTATE);           //  Override pin state, for debugging purposes

  // TPD_PINSTATE = !TPD_PINSTATE;                 // Toggle, LED STATE 
  // digitalWrite(TPD_PIN, TPD_PINSTATE);          // Override pin state, for debugging purposes
     
} 
// -- END of TIMER ISR
