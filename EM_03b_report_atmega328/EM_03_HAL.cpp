/*
 * Hardware Abstract layer (HAL) library for Energy Meter EM-03b(Ver EM-HAL-1.0b)
 * File name: EM_03_HAL.cpp
 * Copyright 2016 by MinhDuc Thieu (thieuminhduc2011@gmail.com)
 * Created 28-11-2016
 * 21-12-2016
 *****************************************************************************
 * Main function
 * Control the peripheral devices of EM-03a, which includes:
 * LCD5110
 * Timer/Counter 1
 * ADC
 * Real-time Clock
 * EEPROM
 *****************************************************************************
 */

#include "EM_03_HAL.h"

static binary_energy_t energy_bin;
/*
 ***********************************************
 * @fn      init_io
 * @brief   initialize I/O pins
 * @return  none
 */ 
 void init_io()
 {
   pinMode(VPin, INPUT);
   pinMode(IPin_LOW, INPUT);
   pinMode(IPin_HIGH, INPUT); 
 }


/*
 ************************************************
 * @fn      init_ref_voltage
 * @brief   initialize external reference voltage
 * @return  none
 */
 void init_ref_voltage()
 {
  analogReference(EXTERNAL);        
 }


/*
 ****************************************
 * @fn      init_rtc
 * @brief   initialize real time clock ic
 * @return  none
 */ 

/*
 ****************************************************
 * @fn      init_lcd
 * @brief   initialize lcd 5110
 * @return  none
 */

/*
 *********************************** 
 * @fn      print_dateTime_to_lcd
 * @brief   read date time from rtc
 * @return  none
 */

/*
 ******************************************************************************************************
 * @fn      eeprom_write_float
 * @brief   handle and save data to EEPROM.
 *          To save to EEPROM, energy value form: abcde.f must be separated into 4 parts:
            Part 1 (e[1]): a, part 2 (e[2]): bc, part 3 (e[3]): de, part 4 (e[4]): f
            NOTE: With this library, when saving data to EEPROM, it will clear the hold page (16 bytes)
 * @return  none
 */
void eeprom_write_float(int addr, float energy)
{
  energy_bin.e = energy;
  eeprom.writeBytes(addr, 4, energy_bin.binary);  
}


/*
 ****************************************************
 * @fn      eeprom_read_float
 * @brief   read data and handle it from EEPROM
 * @return  float
 */
float eeprom_read_float(int addr)
{
  eeprom.readBytes(addr, 4, energy_bin.binary);
  return energy_bin.e;
}


/*
 ******************************************************************************************************
 * @fn      eeprom_update_energy_value
 * @brief   cumulatively update energy value to eeprom every 0.5kWh
 * @return  none
 */
 void eeprom_update_energy_value(float energy, int addr)
 {
   float e_save = eeprom_read_float(addr);
   if(((energy - e_save) >= 0.5) && ((energy - e_save) < 0.55))        //Save to EEPROM every 0.5 kWh
   {
      eeprom_write_float(addr, energy);
   }
 }


/*
 *****************************************************
 * @fn      print_1st_scr
 * @brief   display 1st screen on lcd
 * @return  none
 */


/*
 *****************************************************
 * @fn      print_2nd_scr
 * @brief   display 2nd screen on lcd
 * @return  none
 */
 
