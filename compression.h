#ifndef __COMPRESSION_H__
#define __COMPRESSION_H__

#ifdef __cplusplus
 extern "C" {
#endif

#include "stdio.h"

/**
 * @brief Encode int16_t type data.
 * 
 * @param dataForCompression Uint16_t data for encoding.
 * @param d Pointer to uint32_t for storing encoded data.
 *                          
 * @return  Returns length of encoded data.
 */
uint8_t encode(int16_t dataForCompression, uint32_t* d);

/**
 * @brief Put data to data packet.
 * 
 * @param code Uint32_t type data that you want to put in a packet.
 * @param codeLen Length of the data.
 * @param finalDataBuffer Pointer to the buffer for storing data (packet).
 * @param bufferSize Buffer size.
 * @param counter Pointer to an outside counter that tracks current position in a packet.
 *                         
 * @return  Returns TRUE if the data is successfully put in a packet, returns FALSE otherwise.
 */
bool sendToPacket(uint32_t code, uint8_t codeLen, uint8_t* finalDataBuffer, size_t bufferSize, uint32_t* counter);

/**
 * @brief Puts n lower bits to one, others are zero.
 * 
 * @param n Number of bits that should be one.
 *                         
 * @return  Returns uint32_t type data.
 */
uint32_t nLowestBitsTo1(uint8_t n);

/**
 * @brief Prints data in binary.
 * 
 * @param size Size of data.
 * @param ptr Pointer to data that should be printed.
 *                         
 * @return  void
 */
void printBits(size_t const size, void const * const ptr);


#ifdef __cplusplus
}
#endif

#endif  //__COMPRESSION_H__