A simple compression algorithm that works the best on a sequence of data where the difference between consecutive samples can
be represented as a normal distribution with a small variance. If a sensor data is acquired with a frequency high enough that
the value between consecutive samples is close to zero, this algorithm finds its purpouse!

Compression algorithm is written so that it can easily be implemented on any microcontroller. Receiver side is written for a PC
in a shape of a python script that gets its data from a serial port. Script decompresses received data and saves it to a database.
