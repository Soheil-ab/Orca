//============================================================================
// Author      : Soheil Abbasloo
// Version     : 1.0
//============================================================================

/*
  MIT License
  Copyright (c) Soheil Abbasloo 2020 (ab.soheil@gmail.com)

  Permission is hereby granted, free of charge, to any person obtaining a copy
  of this software and associated documentation files (the "Software"), to deal
  in the Software without restriction, including without limitation the rights
  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
  copies of the Software, and to permit persons to whom the Software is
  furnished to do so, subject to the following conditions:
  The above copyright notice and this permission notice shall be included in all
  copies or substantial portions of the Software.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
  SOFTWARE.
*/
//#####################################################################################################
#ifndef COMMON_H_
#define COMMON_H_
//#####################################################################################################

//=========================================================================
#include <stdio.h>
#include <string.h>
//#include "Debug.h"
//#include "MemTrack.h"
//=========================================================================

//=========================================================================
//General Result Codes
enum ERes
{
	ERES_SUCCESS 					=  0,
	ERES_WARNING					= -1,
	ERES_ERROR 						= -2,
	ERES_ERR_INVALID_PARAMETER		= -3,
	ERES_ERR_OPERATION_FAILED		= -4,
	ERES_ERR_INVALID_POINTER		= -5,
	ERES_ERR_NO_MEM					= -6,
	ERES_ERR_INVALID_OPERATION		= -7,
	ERES_ERR_NOT_IMPLEMENTED		= -8,
};
//=========================================================================

//#define ERROR		-1


/*
//ANSI Terminal Colors
#define COL_DGRY "[0;30m"
#define COL_DBLU "[0;34m"
#define COL_DGRN "[0;32m"
#define COL_DCYN "[0;36m"
#define COL_DRED "[0;31m"
#define COL_DMAG "[0;35m"
#define COL_DYEL "[0;33m"
#define COL_DWHT "[0;37m"
#define COL_LGRY "[1;30m"
#define COL_LBLU "[1;34m"
#define COL_LGRN "[1;32m"
#define COL_LCYN "[1;36m"
#define COL_LRED "[1;31m"
#define COL_LMAG "[1;35m"
#define COL_LYEL "[1;33m"
#define COL_LWHT "[1;37m"
//#define COL_LBLK "[1;30m"
#define HIDCRSR "[?25l"
#define SHWCRSR "[?25h"
#define CLSSTR  "[2J"
#define ESCS	""
#define ESCC	''
#define ESCNUM	0x1B
#define CC_BS	'\x08'
*/
//ANSI Terminal Colors
#define COL_DGRY ""
#define COL_DBLU ""
#define COL_DGRN ""
#define COL_DCYN ""
#define COL_DRED ""
#define COL_DMAG ""
#define COL_DYEL ""
#define COL_DWHT ""
#define COL_LGRY ""
#define COL_LBLU ""
#define COL_LGRN ""
#define COL_LCYN ""
#define COL_LRED ""
#define COL_LMAG ""
#define COL_LYEL ""
#define COL_LWHT ""
//#define COL_LBLK "[1;30m"
#define HIDCRSR ""
#define SHWCRSR ""
#define CLSSTR  ""
#define ESCS	""
#define ESCC	''
#define ESCNUM	0x1B
#define CC_BS	'\x08'

#define MOVCRSR(_x,_y)   "["#_y";"#_x"H"


//=========================================================================
// GCC Attributes
//=========================================================================
//for Functions
#define __GFA_INLINE			__attribute__((always_inline)) 		//Force in-line
#define __GFA_NOINLINE			__attribute__((noinline))			//Force no in-line
#define __GFA_FLATTEN			__attribute__((flatten))			//in-line all calls from this function(if possible)
#define __GFA_ERROR(_msg_)		__attribute__((error(_msg_)))		//Generate Error
#define __GFA_WARN(_msg_)		__attribute__((warning(_msg_)))		//Generate Warning
#define __GFA_UNUSED			__attribute__((unused)) 			//do not generate warning if not used
#define __GFA_USED				__attribute__((used)) 				//mark as used
//for Types
#define __GTA_ALIGNE_BYTE		__attribute__((aligned(8))) 		//Byte alignment
#define __GTA_ALIGNE			__attribute__((aligned)) 			//Use Optimum alignment
#define __GTA_PACKED			__attribute__((packed)) 			//Use minimum memory(for enums,union,...)
#define __GTA_UNUSED			__attribute__((unused)) 			//do not generate warning if not used
//for Variables
#define __GVA_ALIGNE_BYTE		__attribute__((aligned(8))) 		//Byte alignment
#define __GVA_ALIGNE			__attribute__((aligned)) 			//Use Optimum alignment
#define __GVA_PACKED			__attribute__((packed)) 			//Use minimum memory(for enums,union,...)
#define __GVA_UNUSED			__attribute__((unused)) 			//do not generate warning if not used
#define __GVA_USED				__attribute__((used)) 				//mark as used
//=========================================================================


//=========================================================================
#define VERSION(_major_, _minor_) ( ((_major_ & 0xFF)<<8) | (_minor_ & 0xFF) )
#define MAJOR_VERSION(_version_)	((_version_ >> 8) & 0xFF)
#define MINOR_VERSION(_version_)	(_version_ & 0xFF)

#define CHECK_VAR_RANGE_B(_var, _low, _high) (((_var) >= (_low))&&((_var) <= (_high)))
#define CHECK_VAR_RANGE_NB(_var, _low, _high) (((_var) > (_low))&&((_var) < (_high)))
#define CHECK_VAR_RANGE_NOT_B(_var, _low, _high) (((_var) <= (_low))||((_var) >= (_high)))
#define CHECK_VAR_RANGE_NOT_NB(_var, _low, _high) (((_var) < (_low))||((_var) > (_high)))

#define CHECK_POINTER(_pointer)	((_pointer)?1:0)

#define SUCCESS(_res) ( (_res==ERES_SUCCESS)?true:false)
#define ERROR(_res) ( (_res!=ERES_SUCCESS)?true:false)


#ifdef PALCON_H_
#define PUTCH(ch) CConsole::PutChar(ch)
#define PRINT(fmt, arg...)  CConsole::Print(fmt, ## arg )
#define PRINTXY(_x,_y, fmt, arg...)  do{CConsole::Print("[%d;%dH",_y,_x); CConsole::Print(fmt, ## arg );}while(0)
#define PRINTCOL(col, fmt, arg...) CConsole::Print( col fmt COL_DWHT, ## arg )
#define DBGPRINTPRTY(curlvl, showlvl, fmt, arg...)	do{if(curlvl>=showlvl)CConsole::Print(COL_LWHT "\r[%s] " COL_DWHT fmt COL_DWHT, __PRETTY_FUNCTION__ , ## arg );}while(0)
#define DBGPRINT(curlvl, showlvl, fmt, arg...)  do{if(curlvl>=showlvl)CConsole::Print(COL_LWHT "\r[%s] " COL_DWHT fmt COL_DWHT, __FUNCTION__ , ## arg );}while(0)
#define DBGMARK(curlvl, showlvl, fmt, arg...)	do{if(curlvl>=showlvl)CConsole::Print(COL_LBLU "\r[%s-%s-%d] " COL_DBLU fmt COL_DWHT, __FILE_NAME__, __FUNCTION__, __LINE__ , ## arg );}while(0)
#define DBGERROR(fmt, arg...)		CConsole::Print(COL_LRED "\r[%s] " COL_DRED fmt COL_DWHT, __FUNCTION__ , ## arg )
#define DBGWARN(fmt, arg...)		CConsole::Print(COL_LYEL "\r[%s] " COL_DYEL fmt COL_DWHT, __FUNCTION__ , ## arg )
#define DBGINFO(fmt, arg...)		CConsole::Print(COL_LBLU "\r[%s] " COL_DGRN fmt COL_DWHT, __FUNCTION__ , ## arg )
#else
#define PUTCH(ch) do{fputc(ch, stdout);}while(0)
#define PRINT(fmt, arg...)  do{fprintf(stdout, fmt, ## arg );fflush(stdout);}while(0)
#define PRINTXY(_x,_y,fmt,arg...) do{fprintf(stdout, "[%d;%dH",_y,_x); fprintf(stdout, fmt, ## arg );fflush(stdout);}while(0)
#define PRINTCOL(col, fmt, arg...) do{fprintf(stdout, col fmt COL_DWHT, ## arg );fflush(stdout);}while(0)
#define DBGPRINTPRTY(curlvl, showlvl,fmt, arg...)	do{if(curlvl>=showlvl){fprintf(stdout, COL_LWHT "\r[%s] " COL_DWHT fmt COL_DWHT, __PRETTY_FUNCTION__ , ## arg );fflush(stdout);}}while(0)
#define DBGPRINT(curlvl, showlvl, fmt, arg...)	do{if(curlvl>=showlvl){fprintf(stdout, COL_LWHT "\r[%s] " COL_DWHT fmt COL_DWHT, __FUNCTION__ , ## arg );fflush(stdout);}}while(0)
#define DBGMARK(curlvl, showlvl, fmt, arg...)	do{if(curlvl>=showlvl){fprintf(stdout, COL_LBLU "\r[%s-%s-%d] " COL_DBLU fmt COL_DWHT, __FILE_NAME__, __FUNCTION__, __LINE__ , ## arg );fflush(stdout);}}while(0)
#define DBGERROR(fmt, arg...)	do{fprintf(stdout, COL_LRED "\r[%s] " COL_DRED fmt COL_DWHT, __FUNCTION__ , ## arg );fflush(stdout);}while(0)
#define DBGWARN(fmt, arg...)	do{fprintf(stdout, COL_LYEL "\r[%s] " COL_DYEL fmt COL_DWHT, __FUNCTION__ , ## arg );fflush(stdout);}while(0)
#define DBGINFO(fmt, arg...)	do{fprintf(stdout, COL_LGRN "\r[%s] " COL_DGRN fmt COL_DWHT, __FUNCTION__ , ## arg );fflush(stdout);}while(0)
#endif
//=========================================================================
#define __FILE_NAME__ (strrchr(__FILE__,'/')?strrchr(__FILE__,'/')+1:__FILE__)
//=========================================================================

//#####################################################################################################

#endif /* COMMON_H_ */
