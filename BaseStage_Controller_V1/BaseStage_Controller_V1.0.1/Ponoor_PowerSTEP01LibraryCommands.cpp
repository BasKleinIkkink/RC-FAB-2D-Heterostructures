#include "Ponoor_PowerSTEP01Library.h"
//commands.ino - Contains high-level command implementations- movement
//   and configuration commands, for example.

// Realize the "set parameter" function, to write to the various registers in
//  the dSPIN chip.
void powerSTEP::setParam(byte param, unsigned long value) 
{
  param |= SET_PARAM;
  SPIXfer((byte)param);
  paramHandler(param, value);
}

// Realize the "get parameter" function, to read from the various registers in
//  the dSPIN chip.
long powerSTEP::getParam(byte param)
{
  SPIXfer(param | GET_PARAM);
  return paramHandler(param, 0);
}

// Returns the content of the ABS_POS register, which is a signed 22-bit number
//  indicating the number of steps the motor has traveled from the HOME
//  position. HOME is defined by zeroing this register, and it is zero on
//  startup.
long powerSTEP::getPos()
{
  long temp = getParam(ABS_POS);
  
  // Since ABS_POS is a 22-bit 2's comp value, we need to check bit 21 and, if
  //  it's set, set all the bits ABOVE 21 in order for the value to maintain
  //  its appropriate sign.
  if (temp & 0x00200000) temp |= 0xffc00000;
  return temp;
}

// Returns the content of the EL_POS register, which is a 9-bit indicates the current 
//  electrical position of the motor. 
unsigned int powerSTEP::getElPos()
{
  unsigned int temp = getParam(EL_POS);
  return temp;
}

// Just like getPos(), but for MARK.
long powerSTEP::getMark()
{
  long temp = getParam(MARK);
  
  // Since ABS_POS is a 22-bit 2's comp value, we need to check bit 21 and, if
  //  it's set, set all the bits ABOVE 21 in order for the value to maintain
  //  its appropriate sign.
  if (temp & 0x00200000) temp |= 0xffC00000;
  return temp;
}

// RUN sets the motor spinning in a direction (defined by the constants
//  FWD and REV). Maximum speed and minimum speed are defined
//  by the MAX_SPEED and MIN_SPEED registers; exceeding the FS_SPD value
//  will switch the device into full-step mode.
// The spdCalc() function is provided to convert steps/s values into
//  appropriate integer values for this function.
void powerSTEP::run(byte dir, float stepsPerSec)
{
  unsigned long integerSpeed = spdCalc(stepsPerSec);
  //Serial.print("RUN SPS: ");                     // status feedback, only for debug  
  //Serial.println(stepsPerSec);                     // status feedback, only for debug 
  runRaw(dir, integerSpeed);
}
void powerSTEP::runRaw(byte dir, unsigned long integerSpeed) {
  SPIXfer(RUN | dir);
  if (integerSpeed > 0xFFFFF) integerSpeed = 0xFFFFF;
  // Now we need to push this value out to the dSPIN. The 32-bit value is
  //  stored in memory in little-endian format, but the dSPIN expects a
  //  big-endian output, so we need to reverse the byte-order of the
  //  data as we're sending it out. Note that only 3 of the 4 bytes are
  //  valid here.
  
  // We begin by pointing bytePointer at the first byte in integerSpeed.
  byte* bytePointer = (byte*)&integerSpeed;
  // Next, we'll iterate through a for loop, indexing across the bytes in
  //  integerSpeed starting with byte 2 and ending with byte 0.
  for (int8_t i = 2; i >= 0; i--)
  {
    SPIXfer(bytePointer[i]);
  }
}

// STEP_CLOCK puts the device in external step clocking mode. When active,
//  pin 25, STCK, becomes the step clock for the device, and steps it in
//  the direction (set by the FWD and REV constants) imposed by the call
//  of this function. Motion commands (RUN, MOVE, etc) will cause the device
//  to exit step clocking mode.
void powerSTEP::stepClock(byte dir)
{
  SPIXfer(STEP_CLOCK | dir);
}

// MOVE will send the motor numStep full steps in the
//  direction imposed by dir (FWD or REV constants may be used). The motor
//  will accelerate according the acceleration and deceleration curves, and
//  will run at MAX_SPEED. Stepping mode will adhere to FS_SPD value, as well.
void powerSTEP::move(byte dir, unsigned long numSteps)
{
  SPIXfer(MOVE | dir);
  if (numSteps > 0x3FFFFF) numSteps = 0x3FFFFF;
  // See run() for an explanation of what's going on here.
  byte* bytePointer = (byte*)&numSteps;
  for (int8_t i = 2; i >= 0; i--)
  {
    SPIXfer(bytePointer[i]);
  }
}

// GOTO operates much like MOVE, except it produces absolute motion instead
//  of relative motion. The motor will be moved to the indicated position
//  in the shortest possible fashion.
void powerSTEP::goTo(long pos)
{
  SPIXfer(GOTO);
  if (pos > 0x3FFFFF) pos = 0x3FFFFF;
  // See run() for an explanation of what's going on here.
  byte* bytePointer = (byte*)&pos;
  for (int8_t i = 2; i >= 0; i--)
  {
    SPIXfer(bytePointer[i]);
  }
}

// Same as GOTO, but with user constrained rotational direction.
void powerSTEP::goToDir(byte dir, long pos)
{
  SPIXfer(GOTO_DIR | dir);
  if (pos > 0x3FFFFF) pos = 0x3FFFFF;
  // See run() for an explanation of what's going on here.
  byte* bytePointer = (byte*)&pos;
  for (int8_t i = 2; i >= 0; i--)
  {
    SPIXfer(bytePointer[i]);
  }
}

// GoUntil will set the motor running with direction dir (REV or
//  FWD) until a falling edge is detected on the SW pin. Depending
//  on bit SW_MODE in CONFIG, either a hard stop or a soft stop is
//  performed at the falling edge, and depending on the value of
//  act (either RESET or COPY) the value in the ABS_POS register is
//  either RESET to 0 or COPY-ed into the MARK register.
void powerSTEP::goUntil(byte action, byte dir, float stepsPerSec)
{
  unsigned long integerSpeed = spdCalc(stepsPerSec);
  goUntilRaw(action, dir, integerSpeed);
}
void powerSTEP::goUntilRaw(byte action, byte dir, unsigned long integerSpeed)
{
  action = (action > 0) << 3;
	SPIXfer(GO_UNTIL | action | dir);
	if (integerSpeed > 0x3FFFFF) integerSpeed = 0x3FFFFF;
  // See run() for an explanation of what's going on here.
  byte* bytePointer = (byte*)&integerSpeed;
  for (int8_t i = 2; i >= 0; i--)
  {
    SPIXfer(bytePointer[i]);
  }
}

// Similar in nature to GoUntil, ReleaseSW produces motion at the
//  higher of two speeds: the value in MIN_SPEED or 5 steps/s.
//  The motor continues to run at this speed until a rising edge
//  is detected on the switch input, then a hard stop is performed
//  and the ABS_POS register is either COPY-ed into MARK or RESET to
//  0, depending on whether RESET or COPY was passed to the function
//  for act.
void powerSTEP::releaseSw(byte action, byte dir)
{
  action = (action > 0) << 3;
  SPIXfer(RELEASE_SW | action | dir);
}

// GoHome is equivalent to GoTo(0), but requires less time to send.
//  Note that no direction is provided; motion occurs through shortest
//  path. If a direction is required, use GoTo_DIR().
void powerSTEP::goHome()
{
  SPIXfer(GO_HOME);
}

// GoMark is equivalent to GoTo(MARK), but requires less time to send.
//  Note that no direction is provided; motion occurs through shortest
//  path. If a direction is required, use GoTo_DIR().
void powerSTEP::goMark()
{
  SPIXfer(GO_MARK);
}

// setMark() and setHome() allow the user to define new MARK or
//  ABS_POS values.
void powerSTEP::setMark(long newMark)
{
  setParam(MARK, newMark);
}

void powerSTEP::setPos(long newPos)
{
  setParam(ABS_POS, newPos);
}

void powerSTEP::setElPos(unsigned int newElPos)
{
  setParam(EL_POS, newElPos);
}

// Sets the ABS_POS register to 0, effectively declaring the current
//  position to be "HOME".
void powerSTEP::resetPos()
{
  SPIXfer(RESET_POS);
}

// Reset device to power up conditions. Equivalent to toggling the STBY
//  pin or cycling power.
void powerSTEP::resetDev()
{
  SPIXfer(RESET_DEVICE);
}
  
// Bring the motor to a halt using the deceleration curve.
void powerSTEP::softStop()
{
  SPIXfer(SOFT_STOP);
}

// Stop the motor with infinite deceleration.
void powerSTEP::hardStop()
{
  SPIXfer(HARD_STOP);
}

// Decelerate the motor and put the bridges in Hi-Z state.
void powerSTEP::softHiZ()
{
  SPIXfer(SOFT_HIZ);
}

// Put the bridges in Hi-Z state immediately with no deceleration.
void powerSTEP::hardHiZ()
{
  SPIXfer(HARD_HIZ);
}

// Fetch and return the 16-bit value in the STATUS register. Resets
//  any warning flags and exits any error states. Using GetParam()
//  to read STATUS does not clear these values.
int powerSTEP::getStatus()
{
  int temp = 0;
#if defined(ARDUINO_ARCH_SAMD)
  __disable_irq();
#endif
  byte* bytePointer = (byte*)&temp;
  SPIXfer(CMD_GET_STATUS);
  bytePointer[1] = SPIXfer(0);
  bytePointer[0] = SPIXfer(0);
#if defined(ARDUINO_ARCH_SAMD)
  __enable_irq();
#endif
  return temp;
}
