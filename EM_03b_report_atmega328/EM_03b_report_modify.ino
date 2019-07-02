#include <Eeprom24C04_16.h>
#include "EmonLib.h"                   // Include Emon Library
#include <Wire.h>
#include "TimerOne.h"
#include "EM_03_HAL.h"
#include "EM_03_Metering.h"
#include <SoftwareSerial.h>
//   Tx             Tx | 12                      Tx
//   Rx             Rx | 11                      Rx   
SoftwareSerial cc(11,12);                         //Must name as "cc" - RX, TX
Eeprom24C04_16 eeprom(EEPROM_I2C_ADDRESS);
        
int t;
byte td1 = 0, td2 = 0;
/*
 ***************************************************************************************
 * VARIABLES FOR VOLTAGE MEASURING
 */
volatile float valV;
volatile float sumValV = 0;              //Sum sqVal values
volatile float Urms;                     //ROOT MEAN SQUARE AC VOLTAGE
/*
 ***************************************************************************************
 * VARIABLES FOR CURRENT MEASURING
 */
volatile float valI;
volatile float sumValI = 0;
bool  SW_CH = 0;                //for switch Irms range automatically
                                //SW_CH = 0: select channel with gain = GAIN_LOW
                                //SW_CH = 1: select channel with gain = GAIN_HIGH
volatile int SW_CHx = 0;
/*
 ***************************************************************************************
 * VARIABLES FOR POWER MEASURING
 */
volatile float valP;                     //instantaneous power sample value
volatile float sumValP = 0;              //sum of instantaneous power ADC value

/*
 ****************************************************************************************
 * VARIABLES FOR ENERGY MEASURING
 */
volatile float energy = 0;               //Power used in every month
volatile float e_save = 0;               //Value stored in EEPROM
EnergyMonitor emon1;                   // Create an instance

void setup() 
{ 
  cc.begin(115200);
  Serial.begin(115200);
  emon1.current(1, 111.1);             // Current: input pin, calibration.
  delay(200);
  init_io();
  init_ref_voltage();
  init_eeprom();
  init_timerOne();

}

void loop() 
{
  double Irms = emon1.calcIrms(1480);  // Calculate Irms only
  delay(1000);
  Serial.print("Urms:<");
  Serial.print(Urms); 
  Serial.print(">Irms:<");
  Serial.print(Irms);
  Serial.println(">");
  //Check updating dateTime and EEPROM
}

void serialEvent() 
  {
          stop_timerOne();
          
          /*
          // For read attr mode
          get_read_attr_res_info()->urms = Urms;
          get_read_attr_res_info()->prms = Prms;
          get_read_attr_res_info()->energy = energy;
          get_read_attr_res_info()->irms = Irms;
          get_read_attr_res_info()->pf = factorP;*/
          
          //print_Response();
          //recv_Simple_Metering_AF_INCOMING_MSG_AREQ();
          
          restart_timerOne();
  }


void timer_ISR()
{
  /*
   ************************************************************************************* 
   * Sample and fiter signal
   */
  //Sample voltage
  valV = sample_voltage(VPin);
  sumValV += (valV * valV);

  //Sample current
  /*switch(SW_CH)         
  {
    //Sample current in 5-20A range (Gain=1)
    //case 0:
    {
                valI = sample_current_low(IPin_LOW);                           
                sumValI += (valI * valI);
                valP = abs(valV * valI);
                sumValP += valP;
                //break;
             }
    //Sample current in 0-5A range (Gain=3.97)          
    /*case 1:  {
                valI = sample_current_high(IPin_HIGH);                           
                sumValI += (valI * valI);                
                valP = abs(valV * valI);
                sumValP += valP;
                break;  
             }
    break;
  }*/
  /*
   
  if(Irms>5)
  
  {*/
  int state = digitalRead(11);
  if (state == LOW);
  valI = sample_current_low(IPin_LOW);                           
  sumValI += (valI * valI);
  valP = abs(valV * valI);
  sumValP += valP;
  SW_CHx = 1;
  /*
  else if( Irms<=5)
  {
                valI = sample_current_high(IPin_HIGH);                           
                sumValI += (valI * valI);                
                valP = abs(valV * valI);
                sumValP += valP;
                SW_CHx = 4;  
  
  /*
   **************************************************************************************
   * Calculation and displaying every 1s
   */
  t++; 
  if (t >= (numSamples - 1))    
  {
    t = 0;
    Urms = calc_rms_voltage(sumValV);
    if(Urms<0) Urms =0;

    //Reset sum variable
    sumValV = 0;                           
    sumValI = 0; 
    sumValP = 0;     
      
  } 
}


/*
 **************************************************************************************
 * @fn          init_eeprom
 * @brief       initialize external eeprom
 * @return      none
 */
void init_eeprom()
{
  eeprom.initialize();
  e_save = eeprom_read_float(EEPROM_FIRST_BYTE_ADDR);
  
}


/*
 **************************************************************************************
 * @fn          init_timerOne
 * @brief       initialize timer/counter1
 * @return      none
 */ 
void init_timerOne()
{
  noInterrupts();
  Timer1.initialize(500);                 // set a timer interval 500us (2047.8Hz)
  Timer1.attachInterrupt(timer_ISR);      // attach the service routine here
  interrupts();  
}


/*
 **************************************************************************************
 * @fn          restart_timerOne
 * @brief       restart timer/counter1
 * @return      none
 */
void restart_timerOne()
{
  Timer1.initialize(500);
  Timer1.attachInterrupt(timer_ISR);    
  interrupts();  
}


/*
 **************************************************************************************
 * @fn          stop_timerOne
 * @brief       Stop timer/counter 1 (clear clock source)
 * @return      none
 */
 void stop_timerOne()
 {
     Timer1.stop();
 }
