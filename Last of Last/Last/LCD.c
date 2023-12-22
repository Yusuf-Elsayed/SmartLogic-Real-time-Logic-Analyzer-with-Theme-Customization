/*
 * LCD.c
 *
 * Created: 2/23/2018 4:38:26 PM
 *  Author: Mohamed Zaghlol
 */ 
#include "LCD.h"
#define  F_CPU 8000000UL 
#include <util/delay.h>

void LCD_vInit(void)
{
	_delay_ms(200);
	#if defined eight_bits_mode
	DIO_vsetPINDir('C',0,1);
	DIO_vsetPINDir('C',1,1);
	DIO_vsetPINDir('C',2,1);
	DIO_vsetPINDir('C',3,1);
	DIO_vsetPINDir('C',4,1);
	DIO_vsetPINDir('C',5,1);
	DIO_vsetPINDir('C',6,1);
	DIO_vsetPINDir('C',7,1);
	DIO_vsetPINDir('D',EN,1);
	DIO_vsetPINDir('D',RW,1);
	DIO_vsetPINDir('D',RS,1);
	DIO_write('D',RW,0);
	LCD_vSend_cmd(EIGHT_BITS); //8 bit mode
	_delay_ms(1);
	LCD_vSend_cmd(CURSOR_ON_DISPLAN_ON);//display on cursor on
	_delay_ms(1);
	LCD_vSend_cmd(CLR_SCREEN);//clear the screen
	_delay_ms(10);
	LCD_vSend_cmd(ENTRY_MODE); //entry mode
	_delay_ms(1); 
	
	#elif defined four_bits_mode
	DIO_vsetPINDir('A',4,1);
	DIO_vsetPINDir('A',5,1);
	DIO_vsetPINDir('A',6,1);
	DIO_vsetPINDir('A',7,1);
	DIO_vsetPINDir('B',EN,1);
	DIO_vsetPINDir('B',RW,1);
	DIO_vsetPINDir('B',RS,1);
   	DIO_write('B',RW,0);
	LCD_vSend_cmd(RETURN_HOME); //return home
	_delay_ms(10);
	LCD_vSend_cmd(FOUR_BITS); //4bit mode
	_delay_ms(1);
	LCD_vSend_cmd(CURSOR_ON_DISPLAN_ON);//display on cursor on
	_delay_ms(1);
	LCD_vSend_cmd(CLR_SCREEN);//clear the screen
	_delay_ms(10);
	LCD_vSend_cmd(ENTRY_MODE); //entry mode
	_delay_ms(1);
	#endif
}


static void send_falling_edge(void)
{
	DIO_write('D',EN,1);
	_delay_ms(2);
	DIO_write('D',EN,0);
	_delay_ms(2);
}
void LCD_vSend_cmd(char cmd)
{
	#if defined eight_bits_mode
	DIO_write_port('C',cmd);
	DIO_write('D',RS,0);
	send_falling_edge();
	
	#elif defined four_bits_mode
	write_high_nibble('C',cmd>>4);
	DIO_write('D',RS,0);
	send_falling_edge();
	write_high_nibble('C',cmd);
	DIO_write('D',RS,0);
	send_falling_edge();
	#endif
	_delay_ms(1);
}

void LCD_vSend_char(char data)
{
	#if defined eight_bits_mode
	DIO_write_port('C',data);
	DIO_write('D',RS,1);
	send_falling_edge();
	
	#elif defined four_bits_mode
	write_high_nibble('C',data>>4);
	DIO_write('D',RS,1);
	send_falling_edge();
	write_high_nibble('C',data);
	DIO_write('D',RS,1);
	send_falling_edge();
	#endif
	_delay_ms(1);
}


void LCD_vSend_string(char *data)
{
	while((*data)!='\0')
	{
		LCD_vSend_char(*data);
		data++;
	}
}
void LCD_clearscreen()
{
	LCD_vSend_cmd(CLR_SCREEN);
	_delay_ms(10);
}
void LCD_movecursor(char row,char coloumn)
{
	char data ;
	if(row>2||row<1||coloumn>16||coloumn<1)
	{
		data=0x80;
	}
	else if(row==1)
	{
		data=0x80+coloumn-1 ;
	}
	else if (row==2)
	{
		data=0xc0+coloumn-1;
	}
	LCD_vSend_cmd(data);
	_delay_ms(1);
}
//Send Number
void LCD_vidSendNum(uint32_t Copy_U32Number){
	uint32_t Local_u32Counter=1 , Local_u32Digit=0;

	if (Copy_U32Number == 0)
	{
		LCD_vSend_char('0');
	}
	else
	{
		while (Copy_U32Number/Local_u32Counter != 0)
		{
			Local_u32Counter *= 10;
		}
		Local_u32Counter /=10;

		while (Local_u32Counter != 0)
		{
			Local_u32Digit = Copy_U32Number/Local_u32Counter;

			LCD_vSend_char(Local_u32Digit + '0');

			Copy_U32Number = Copy_U32Number%Local_u32Counter;

			Local_u32Counter /= 10;
		}
	}
}