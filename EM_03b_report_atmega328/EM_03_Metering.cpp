/*
 * Metering Library for Energy Meter EM-03b(Ver EM-MET-1.0b)
 * File name: EM_03_Metering.cpp
 * Copyright 2016 by MinhDuc Thieu (thieuminhduc2011@gmail.com)
 * Created 29-11-2016
 * Updated 12-12-2016
 *****************************************************************************
 * Main function
 * Sample voltage and current signal
 * Calculate energy parameters
 *****************************************************************************
 */


 #include "EM_03_Metering.h"
 
/*
 ****************************************************
 * @fn      sample_sq_voltage
 * @brief   sample and digital high pass filter
 *          instantaneous voltage from analog channel
 * @return  float
 */  
 float sample_voltage(const int VPin)
 {
    static int valV, lastValV;              
    static float filterValV;
    lastValV = valV;
    valV = analogRead(VPin) ;
    filterValV = 0.996 * (filterValV + (valV - lastValV));
    return filterValV;
 }


/*
 ****************************************************
 * @fn      sample_current_low
 * @brief   sample and digital high pass filter
 *          instantaneous current in 0-5A range
 * @return  float
 */
 float sample_current_low(const int IPin)
 {
    static int valI, lastValI;                       
    static float filterValI;
    lastValI = valI;
    valI = analogRead(IPin);
    filterValI = 0.996 * (filterValI + (valI - lastValI));   
    return filterValI; 
 }


/*
 ****************************************************
 * @fn      sample_current_high
 * @brief   sample and digital high pass filter
 *          instantaneous current in 5-20A range
 * @return  float
 */
 float sample_current_high(const int IPin)
 {
    static int valI, lastValI;                       
    static float filterValI;
    lastValI = valI;
    valI = analogRead(IPin);
    filterValI = 0.996 * (filterValI + (valI - lastValI)) / (GAIN_HIGH);   
    return filterValI; 
 }

 
/*
 ****************************************************
 * @fn      calc_rms_voltage
 * @brief   calculate root-mean-square voltage
 * @return  float
 */
 float calc_rms_voltage(float sumValV)
 {
    float rmsValV, Urms;              
    rmsValV = sqrt(sumValV / numSamples);
    Urms = rmsValV * constU + offsetV;
    
    //calibrate offset value
    if(Urms <= offsetV)          
      Urms = 0;
    return Urms;
 }



/*
 ****************************************************
 * @fn      calc_rms_current
 * @brief   calculate root-mean-square current
 * @return  float
 */

/*
 ****************************************************
 * @fn      calc_rms_power
 * @brief   calculate root-mean-square power
 * @return  float
 */

/*
 ****************************************************
 * @fn      calc_power_factor
 * @brief   calculate power factor
 * @return  float
 */

/*
 *********************************************************
 * @fn      calc__energy_consumption
 * @brief   calculate energy consumption, 
 *          add a previous value from eeprom to the result
 * @return  float
 */
