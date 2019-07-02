/*
 * Hardware Abstract layer (HAL) library for Energy Meter EM-03b(Ver EM-HAL-1.0b)
 * File name: EM_03_HAL.h
 * Copyright 2016 by MinhDuc Thieu (thieuminhduc2011@gmail.com)
 * Edited by KhacPhong Nguyen ( phonghust1995@gmail.com)
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
 *
 *
 */

#ifndef EM_03_HAL_H
#define EM_03_HAL_H

#include <LCD5110_Basic.h>
//#include <SPI.h>
//#include <mrf24j.h>
#include <Eeprom24C04_16.h>
#include <Wire.h>

#define VPin            A0           //Voltage channel
#define IPin_LOW        A1           //Current Channel (Gain = 1; 5-20A range)
#define IPin_HIGH       A2           //Current Channel (Gain = 3.97; 0-5A range)
#define EEPROM_I2C_ADDRESS       0x50
#define EEPROM_FIRST_BYTE_ADDR   0x00

extern Eeprom24C04_16 eeprom;
extern uint8_t SmallFont[];



//Binary array for storing energy value
typedef union 
{
  float e;
  byte binary[4];
} binary_energy_t;


/*
 **********************************************************************
 * APIs LIST:
 **********************************************************************
 */
 void   init_io();

 void   init_ref_voltage();
 
 float  eeprom_read_float(int addr);
  
 void   print_1st_scr(float Urms);
 
 

 #endif     /*EM_03_HAL_H*/
