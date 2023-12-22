/*
 * Wafe_Generator.c
 *
 * Created: 11/8/2023 11:28:57 AM
 * Author : youssef
 */ 

#include <avr/io.h>
#include <avr/interrupt.h>
#include <util/delay.h>
#include "uart.h"
#include "logicAnalyzer.h"



int main(void) {

	LOGIC_Init();

	sei();
	
	while (1)
	{
		LOGIC_MainFunction();
	}
	return 0; // never reached
}