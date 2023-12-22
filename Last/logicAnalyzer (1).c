#include <avr/io.h>
#include <stdlib.h>
 
#include <util/delay.h>
 
#include "logicAnalyzer.h"
#include <avr/interrupt.h>
#include "uart.h"
#include "std_macros.h"
#include "LCD.h"

 
#define _CMD_START_CNT 1
#define _CMD_END_CNT   1
#define _CMD_SPACING   1
#define _CMD_PINS_ST   1
#define _CMD_TIME_SNAP 4
 
#define FULL_SAMPLE_CNT (_CMD_START_CNT + _CMD_PINS_ST +  _CMD_TIME_SNAP + _CMD_END_CNT)
 
#define _SAMPLE_PIN  (_CMD_START_CNT)
#define _SAMPLE_TIME (_CMD_START_CNT + _CMD_PINS_ST)
 
#define MARKER_END   (FULL_SAMPLE_CNT - 1)
#define MARKER_START (0)
 
// Send the following frame for each sample:
// @PIN TIME3 TIME2 TIME1 TIME0;
 
#define _SAMPLES_NUM 10
#define LOGIC_DDR  DDRA
#define LOGIC_PORT PINA
 
typedef enum {MONITOR, SAMPLING, SENDING, IDLE} states_t;
 
 
static logic_port_state = 0;
static logic_port_pre_state;
static states_t currentState = SAMPLING;
static uint8_t  pin_states[_SAMPLES_NUM];
static uint32_t time_snap[_SAMPLES_NUM];
static uint32_t ovcounter = 0;
 
 
static uint32_t getTime(void){
	uint8_t xl = TCNT1L;
	uint32_t x = TCNT1H;
	x = x << 8;	//65535
	x |= xl;
	x += ovcounter*65535;
	return x;
}
ISR(TIMER1_OVF_vect)
{
	ovcounter++;
}
 
void LOGIC_Init(void)
{
	// Initialize Timer1 in normal mode with overflow interrupt
	TCCR1A = 0;
	TCCR1B = (1 << CS10); // Set prescaler to 1
	TIMSK |= (1 << TOIE1); // Enable Timer1 overflow interrupt

	// Enable global interrupts
	sei();
	
	// fs = 8M / 1 = 8M >= 2*fm ==> fm <= 4M
	// Time =Tick time(125ns) * ticks => f of signal = 1/t

	TCNT1H = 0;
	TCNT1L = 0;
	
    /* Init UART driver. */
    UART_cfg my_uart_cfg;
    
    /* Set USART mode. */
    my_uart_cfg.UBRRL_cfg = (BAUD_RATE_VALUE)&0x00FF;
    my_uart_cfg.UBRRH_cfg = (((BAUD_RATE_VALUE)&0xFF00)>>8);
    
    my_uart_cfg.UCSRA_cfg = 0;
    my_uart_cfg.UCSRB_cfg = (1<<RXEN)  | (1<<TXEN) | (1<<TXCIE) | (1<<RXCIE);
    my_uart_cfg.UCSRC_cfg = (1<<URSEL) | (3<<UCSZ0);
    
    UART_Init(&my_uart_cfg);
 
    /* Start with getting which wave to generate. */ 
    currentState = SAMPLING;   
	
	DDRB = 0xFF;
}
static char dutyCycle[] = "0";
static char Frequency[] = "0000000";

void LOGIC_MainFunction(void)
{    
    static volatile uint8_t samples_cnt = 0;
    static char _go_signal_buf = 'N';
	
	// Convert selected channel to an integer
	int channel = atoi(dutyCycle);

	// Set PORTC based on the selected channel
	if (channel > 0 && channel <= 8) {
		PORTB = 1 << (channel - 1);
		} else {
		PORTB = 0xFF; // Default value for an invalid channel
	}
/*
	if(atoi(dutyCycle) != 0 && atoi(Frequency) != 0)
{
	LCD_movecursor(1,1);

	LCD_vSend_string("D.C = ");
	LCD_vSend_string(dutyCycle);
	
	LCD_movecursor(2,1);

	LCD_vSend_string("Freq = ");
	LCD_vSend_string(Frequency);
}*/
    // Main function must have two states,
    // First state is command parsing and waveform selection.
    // second state is waveform executing.
    switch(currentState)
    {
        case MONITOR:
        {
            LOGIC_DDR = 0;
            logic_port_pre_state = logic_port_state;
            logic_port_state     = LOGIC_PORT; 
            currentState = (logic_port_pre_state != logic_port_state) ? SAMPLING : MONITOR;
            break;
        }
        case SAMPLING:
        {
			time_snap[samples_cnt]  = getTime();
            // DO here sampling.
            LOGIC_DDR = 0;
            pin_states[samples_cnt] = logic_port_state;
            
            // Increment sample count.
            samples_cnt++;
 
            // Start sending the collected _SAMPLES_NUM samples.
            currentState = (samples_cnt >= _SAMPLES_NUM) ? SENDING : MONITOR;
            break;
        }
        case SENDING:
        {
			samples_cnt = 0;
            // For _SAMPLES_NUM samples send the construct the buffer.
            static uint8_t _sample_buf[FULL_SAMPLE_CNT];
            for(uint8_t i = 0; i < _SAMPLES_NUM; ++i)
            {
                // Construct the buffer.
                
                // Add buffer marker
                _sample_buf[MARKER_START] = '@';
 
                // Add pin value.
                _sample_buf[_SAMPLE_PIN]  = pin_states[i];
 
                // Add time snap value.
                _sample_buf[_SAMPLE_TIME + 0] = ((time_snap[i] & 0xFF000000) >> 24);
                _sample_buf[_SAMPLE_TIME + 1] = ((time_snap[i] & 0x00FF0000) >> 16);
                _sample_buf[_SAMPLE_TIME + 2] = ((time_snap[i] & 0x0000FF00) >> 8);
                _sample_buf[_SAMPLE_TIME + 3] = ((time_snap[i] & 0x000000FF) >> 0);
 
                _sample_buf[MARKER_END]   = ';';
 
                // Send sample.
                UART_SendPayload(_sample_buf, FULL_SAMPLE_CNT);
                while (0 == UART_IsTxComplete());
				
            }
 
            // Trigger receiving for go signal.
            //UART_ReceivePayload(&_go_signal_buf, 1);   
        }
        case IDLE:
        {
			DDRD = 0x08;
			PORTD = 0x08;
			
			do{
				 UART_ReceivePayload(&_go_signal_buf, 1);
				while(0 == UART_IsRxComplete());
			} while(_go_signal_buf != 'G');
            currentState = MONITOR;
			DDRD = 0x08;
			PORTD = 0x08;
			UART_ReceivePayload(&dutyCycle, 1); 
			
			
            if(currentState == MONITOR)
            {
                // TODO: Place your code here to reset the timer value.
				TCNT1H = 0;
				TCNT1L = 0;
				ovcounter = 0;
				for (int i = 0; i < _SAMPLES_NUM; i++) {
					pin_states[i] = 0;
					time_snap[i] = 0;
				}
				
            }
 
            break;
        }
        default: {/* Do nothing.*/}
    }
}
