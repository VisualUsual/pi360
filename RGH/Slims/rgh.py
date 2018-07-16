The bootloader we glitch is CB_A, so we can run the CB_B we want.

On slims, we weren't able to find a motherboard track for CPU_PLL_BYPASS. Our first idea was to remove the 27Mhz master 360 crystal and generate our own clock instead but it was a difficult modification and it didn't yield good results. We then looked for other ways to slow the CPU clock down and found that the HANA chip had configurable PLL registers for the 100Mhz clock that feeds CPU and GPU differential pairs. Apparently those registers are written by the SMC through an I2C bus. I2C bus can be freely accessed, it's even available on a header (J2C3). So the HANA chip will now become our weapon of choice to slow the CPU down (sorry tmbinc, you can't always be right, it isn't boring and it does sit on an interesting bus ;)

So it goes like that:
 - We send an i2c command to the HANA to slow down the CPU at POST code D8 .
 - We wait for POST DA start (POST DA is the memcmp between stored hash and image hash), and start a counter.
 - When that counter has reached a precise value, we send a 20ns pulse on CPU_RESET.
 - We wait some time and then we send an i2c command to the HANA to restore regular CPU clock.
 - The cpu speed goes back to normal, and with a bit of luck, instead of getting POST error F2, the boot process continues and CB_A runs our custom CB_B.

When CB_B starts, DRAM isn't initialised so we chose to only apply a few patches to it so that it can run any CD, the patches are:
 - Always activate zero-paired mode, so that we can use a modified SMC image.
 - Don't decrypt CD, instead expect a plaintext CD in NAND.
 - Don't stop the boot process if CD hash isn't good.

CB_B is RC4 crypted, the key comes from the CPU key, so how do we patch CB_B without knowing the CPU key? RC4 is basically: crypted = plaintext xor pseudo-random-keystream So if we know plaintext and crypted, we can get the keystream, and with the keystream, we can encrypt our own code. It goes like that: guessed-pseudo-random-keystream = crypted xor plaintext new-crypted = guessed-pseudo-random-keystream xor plaintext-patch You could think there's a chicken and egg problem, how did we get plaintext in the first place? Easy: we had plaintext CBs from fat consoles, and we thought the first few bytes of code would be the same as the new CB_B, so we could encrypt a tiny piece of code to dump the CPU key and decrypt CB_B!

The NAND contains CB_A, a patched CB_B, our payload in a custom plaintext CD, and a modified SMC image. The SMC image is modified to have infinite reboot, and to prevent it from periodically sending I2C commands while we send ours.

Now, maybe you haven't realised yet, but CB_A contains no checks on revocation fuses, so it's an unpatchable hack !
