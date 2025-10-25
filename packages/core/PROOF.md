## BigCrush (TestU01 1.2.3) — PASS

```
3773:========= Summary results of BigCrush =========
3776: Generator:        stdin_stream_u01
3778: Total CPU time:   02:36:42.84
3780: All tests were passed
```

**Environment snapshot**
```
Linux DESKTOP-T3HF4I6 5.15.167.4-microsoft-standard-WSL2 #1 SMP Tue Nov 5 00:21:55 UTC 2024 x86_64 x86_64 x86_64 GNU/Linux
Architecture:                         x86_64
CPU op-mode(s):                       32-bit, 64-bit
Address sizes:                        39 bits physical, 48 bits virtual
Byte Order:                           Little Endian
CPU(s):                               12
On-line CPU(s) list:                  0-11
Vendor ID:                            GenuineIntel
Model name:                           Intel(R) Core(TM) i7-10750H CPU @ 2.60GHz
gcc (Ubuntu 11.4.0-1ubuntu1~22.04.2) 11.4.0
cmake version 3.22.1
```
## PractRand — PASS (до 4 GiB)
```
Using: /home/pavlo/PractRand-0.95/RNG_test
RNG_test using PractRand version 0.95
RNG = RNG_stdin64, seed = unknown
test set = core, folding = standard (64 bit)

rng=RNG_stdin64, seed=unknown
length= 256 megabytes (2^28 bytes), time= 1.9 seconds
  no anomalies in 213 test result(s)

rng=RNG_stdin64, seed=unknown
length= 512 megabytes (2^29 bytes), time= 4.9 seconds
  no anomalies in 229 test result(s)

rng=RNG_stdin64, seed=unknown
length= 1 gigabyte (2^30 bytes), time= 9.9 seconds
  no anomalies in 246 test result(s)

rng=RNG_stdin64, seed=unknown
length= 2 gigabytes (2^31 bytes), time= 18.2 seconds
  no anomalies in 263 test result(s)

rng=RNG_stdin64, seed=unknown
length= 4 gigabytes (2^32 bytes), time= 33.8 seconds
  no anomalies in 279 test result(s)

```

## Dieharder — PASS
```
#=============================================================================#
#            dieharder version 3.31.1 Copyright 2003 Robert G. Brown          #
#=============================================================================#
   rng_name    |rands/second|   Seed   |
stdin_input_raw|  3.08e+07  | 681402399|
#=============================================================================#
        test_name   |ntup| tsamples |psamples|  p-value |Assessment
#=============================================================================#
   diehard_birthdays|   0|       100|     100|0.69456795|  PASSED  
      diehard_operm5|   0|   1000000|     100|0.28682665|  PASSED  
  diehard_rank_32x32|   0|     40000|     100|0.20664785|  PASSED  
    diehard_rank_6x8|   0|    100000|     100|0.25818688|  PASSED  
   diehard_bitstream|   0|   2097152|     100|0.59056568|  PASSED  
        diehard_opso|   0|   2097152|     100|0.88772048|  PASSED  
        diehard_oqso|   0|   2097152|     100|0.47067462|  PASSED  
         diehard_dna|   0|   2097152|     100|0.44940975|  PASSED  
diehard_count_1s_str|   0|    256000|     100|0.77466395|  PASSED  
diehard_count_1s_byt|   0|    256000|     100|0.32053975|  PASSED  
 diehard_parking_lot|   0|     12000|     100|0.07667826|  PASSED  
    diehard_2dsphere|   2|      8000|     100|0.95074315|  PASSED  
    diehard_3dsphere|   3|      4000|     100|0.62123971|  PASSED  
     diehard_squeeze|   0|    100000|     100|0.95796455|  PASSED  
        diehard_sums|   0|       100|     100|0.38718141|  PASSED  
        diehard_runs|   0|    100000|     100|0.96989820|  PASSED  
        diehard_runs|   0|    100000|     100|0.39411320|  PASSED  
       diehard_craps|   0|    200000|     100|0.53043716|  PASSED  
       diehard_craps|   0|    200000|     100|0.05502350|  PASSED  
 marsaglia_tsang_gcd|   0|  10000000|     100|0.19965348|  PASSED  
 marsaglia_tsang_gcd|   0|  10000000|     100|0.03975411|  PASSED  
         sts_monobit|   1|    100000|     100|0.67687163|  PASSED  
            sts_runs|   2|    100000|     100|0.39612668|  PASSED  
          sts_serial|   1|    100000|     100|0.79500888|  PASSED  
          sts_serial|   2|    100000|     100|0.04004860|  PASSED  
          sts_serial|   3|    100000|     100|0.14875158|  PASSED  
          sts_serial|   3|    100000|     100|0.15837146|  PASSED  
          sts_serial|   4|    100000|     100|0.16914060|  PASSED  
          sts_serial|   4|    100000|     100|0.69080906|  PASSED  
          sts_serial|   5|    100000|     100|0.06299728|  PASSED  
          sts_serial|   5|    100000|     100|0.03746317|  PASSED  
          sts_serial|   6|    100000|     100|0.32143157|  PASSED  
          sts_serial|   6|    100000|     100|0.92935087|  PASSED  
          sts_serial|   7|    100000|     100|0.02417964|  PASSED  
          sts_serial|   7|    100000|     100|0.20642337|  PASSED  
          sts_serial|   8|    100000|     100|0.06916835|  PASSED  
          sts_serial|   8|    100000|     100|0.78499816|  PASSED  
          sts_serial|   9|    100000|     100|0.19816258|  PASSED  
          sts_serial|   9|    100000|     100|0.59867275|  PASSED  
          sts_serial|  10|    100000|     100|0.14140240|  PASSED  
          sts_serial|  10|    100000|     100|0.56005419|  PASSED  
          sts_serial|  11|    100000|     100|0.13536748|  PASSED  
          sts_serial|  11|    100000|     100|0.26259830|  PASSED  
          sts_serial|  12|    100000|     100|0.06759964|  PASSED  
          sts_serial|  12|    100000|     100|0.64587329|  PASSED  
          sts_serial|  13|    100000|     100|0.02941634|  PASSED  
          sts_serial|  13|    100000|     100|0.19396246|  PASSED  
          sts_serial|  14|    100000|     100|0.11454958|  PASSED  
          sts_serial|  14|    100000|     100|0.61418723|  PASSED  
          sts_serial|  15|    100000|     100|0.47620805|  PASSED  
          sts_serial|  15|    100000|     100|0.03965625|  PASSED  
          sts_serial|  16|    100000|     100|0.25737736|  PASSED  
```
