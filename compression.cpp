#include "compression.h"
#include "stdio.h"
#include "math.h"
#include "debug.h"

uint8_t encode(int16_t dataForCompression, uint32_t* d)
{
    uint32_t code = 0;
    uint8_t length;
    uint8_t n = 0;
    uint16_t s = 0;

    if(dataForCompression == 0)
    {
        n = 0;
    }
    else
    {
        n = (uint8_t) log2(abs(dataForCompression)) + 1;
    }

    if(n == 0)
    {
        s = 0;
        length = n + 2;
    }
    else if(n > 0 && n <= 5)
    {
        s = n + 1;
        length = n + 3;
    }
    else
    {
        s = (uint8_t) pow(2, n - 2) - 2;
        length = 2 * n - 2;
    }

    code = s << n;
    if(dataForCompression >= 0)
        code |= dataForCompression & nLowestBitsTo1(n); 
    else
        code |= (dataForCompression - 1) & nLowestBitsTo1(n);
    *d = code;
    return length;
}

uint32_t nLowestBitsTo1(uint8_t n)
{
    uint32_t retVal = 0;
    for(int i = 0; i < n; i++)
    {
        retVal |= 1UL << i;
    }
    return retVal;
}

void printBits(size_t const size, void const * const ptr)
{
    unsigned char *b = (unsigned char*) ptr;
    unsigned char byte;
    int i, j;
    for (i = size-1; i >= 0; i--) {
        for (j = 7; j >= 0; j--) {
            byte = (b[i] >> j) & 1;
            debugPrintf("%u", byte);
        }
    }
    puts("");
}

bool sendToPacket(uint32_t code, uint8_t codeLen, uint8_t* finalDataBuffer, size_t bufferSize, uint32_t* counter)
{
    uint32_t numOfBitsInPacket = bufferSize * 8;
    bool retVal = false;
    if((*counter + codeLen) < numOfBitsInPacket)
    {
        while(codeLen > 0)
        {
            //debugPrintf("length: %d\n", codeLen);
            uint32_t currentDataInPacket = (uint32_t) *counter / 8;
            //debugPrintf("currDATA: %d\n", currentDataInPacket);
            uint8_t currentBitInPacket = 7 - (uint8_t) (*counter % 8);
            //debugPrintf("currBIT: %d\n", currentBitInPacket);
            int8_t overflow = codeLen - currentBitInPacket - 1;
            //debugPrintf("overflow: %d\n", overflow);

            if(overflow > 0)
            {
                *(finalDataBuffer + currentDataInPacket) |= code >> overflow;
                *counter += codeLen - overflow;  
                //debugPrintf("counter: %d\n", *counter);
                codeLen = overflow;
                //debugPrintf("codeLen: %d\n", codeLen);
            }
            else
            {
                *(finalDataBuffer + currentDataInPacket) |= code << -overflow;
                *counter += codeLen;
                //debugPrintf("counter: %d\n", *counter);
                codeLen = 0;
                retVal = true;
            }
        }
    }
    else
    {
        *counter = numOfBitsInPacket;
    }
    return retVal; 
}
