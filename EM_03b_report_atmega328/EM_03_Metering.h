/*
 * Metering Library for Energy Meter EM-03b(Ver EM-MET-1.0b)
 * File name: EM_03_Metering.h
 * Copyright 2016 by MinhDuc Thieu (thieuminhduc2011@gmail.com)
 * Created 29-11-2016
 * Updated 12-12-2016
 * Updated 21-12-2016
 *****************************************************************************
 * Main function
 * Sample voltage and current signal
 * Calculate energy parameters
 *****************************************************************************
 */

 
#ifndef EM_03_METERING_H
#define EM_03_METERING_H

#include <Arduino.h>

/*
 * Paramenters Configuration
 ***************************
 */

/*
 * The parameters below is for EM - 03a
#define R1             880                               //kOhm
#define R2             3.3                               //kOhm
#define Vref           3.0                               //External Vref from REF5030
#define calibV         1.0481                            //Urms Calibration Factor 19/12/16 (170-250V)
#define offsetV        0.7258                            //Uref = calibV * Uread + offsetV

#define calibI_SCT     1.0515                            //Calib gain (20/12)
#define offsetI_SCT    -0.0343                           
#define ratioSCT       1800.0
#define burdenSCT      62.0                              
#define burden         (120.0*68.0/(120.0+68.0))         

#define numSamples      2048.0                            
#define GAIN_HIGH       3.97
#define GAIN_LOW        1.0
#define timeSample      1.0  */
/*
 * The parameters below is for EM - 03b
 */
#define R1             960                               //kOhm (100k + 470k + 390k)
#define R2             3.3                               //kOhm
#define Vref           2.5                               //External Vref from REF5025
#define calibV         1.0847                            //Urms Calibration Factor 19/12/16 (170-250V)
#define offsetV        2.3418                            //Uref = calibV * Uread + offsetV

#define calibI_SCT     1.0399                            //Calib gain (19/12/16)
#define offsetI_SCT    -0.0127                           //Calib gain (19/12/16)
#define ratioSCT       1800.0
#define burdenSCT      62.0                              
#define burden         (120.0*68.0/(120.0+68.0)) 
#define resGainINA128  18.0        

#define numSamples     2048.0                            
#define GAIN_HIGH      (1+ 50.0/resGainINA128)             //Gain INA128: 1+50/Rburden
#define GAIN_LOW       1.0
#define timeSample     1.0 
                                      

#define constU         (((R1+R2) * calibV * Vref)/(R2 * 1023))
#define constI_SCT     ((Vref * ratioSCT * calibI_SCT)/(1023 * burdenSCT))     //for SCT current transformer
#define constP_SCT     (constU * constI_SCT / numSamples)
#define constE         (timeSample/3600000.0)                                  //calculate every 1s, kWh = (W*h)/1000


/*
 **********************************************************************
 * APIs LIST:
 **********************************************************************
 */
 float sample_voltage(const int VPin);

 float sample_current_low(const int IPin);

 float sample_current_high(const int IPin);

 float calc_rms_voltage(float sumValV);

 float calc_rms_current(float sumValI);

 float calc_rms_power(float sumValP);
 
 
#endif /*EM_03_METERING_H*/
