On PHATS, the bootloader we glitch is CB, so we can run the CD we want.

cjak found that by asserting the CPU_PLL_BYPASS signal, the CPU clock is slowed down a lot, there's a test point on the motherboard that's a fraction of CPU speed, it's 200Mhz when the dash runs, 66.6Mhz when the console boots, and 520Khz when that signal is asserted.

So it goes like that:
 - We assert CPU_PLL_BYPASS around POST code 36 (hex).
 - We wait for POST 39 start (POST 39 is the memcmp between stored hash and image hash), and start a counter.
 - When that counter has reached a precise value (it's often around 62% of entire POST 39 length), we send a 100ns pulse on CPU_RESET.
 - We wait some time and then we deassert CPU_PLL_BYPASS.
 - The cpu speed goes back to normal, and with a bit of luck, instead of getting POST error AD, the boot process continues and CB runs our custom CD.

The NAND contains a zero-paired CB, our payload in a custom CD, and a modified SMC image. A glitch being unreliable by nature, we use a modified SMC image that reboots infinitely (ie stock images reboot 5 times and then go RROD) until the console has booted properly. In most cases, the glitch succeeds in less than 30 seconds from power on that way.
