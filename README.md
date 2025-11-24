# snappy-py

## Install

```sh
#python setup.py bdist_wheel
pip install -e .
```

## Use

```python3
import snappy_py

c = snappy_py.compress(b"111")
snappy_py.uncompress(c)
snappy_py.decompress(c)
```

## Testing

```sh
#pip install cramjam
#pip install python-snappy
python benchmark.py
```

```
 - snappy_py (import snappy_py)
 - python-snappy (import snappy)
 - cramjam (import cramjam)
Impl                           Data       Size     Orig(MB)  Comp(bytes)  CompRatio Comp MB/s   Decomp MB/s
--------------------------------------------------------------------------------------------------------------
snappy_py (import snappy_py)   random     64K      0.06      65542        1.000     7526.52     20854.24   
snappy_py (import snappy_py)   random     1M       1.00      1048627      1.000     9634.07     18021.82   
snappy_py (import snappy_py)   random     8M       8.00      8388996      1.000     3807.41     7610.85    
snappy_py (import snappy_py)   repetitive 64K      0.06      3080         0.047     8179.56     2132.57    
snappy_py (import snappy_py)   repetitive 1M       1.00      49235        0.047     8272.15     2214.69    
snappy_py (import snappy_py)   repetitive 8M       8.00      393860       0.047     7292.14     2073.36    
snappy_py (import snappy_py)   textlike   64K      0.06      3194         0.049     7947.45     5237.07    
snappy_py (import snappy_py)   textlike   1M       1.00      51085        0.049     7341.82     5491.71    
snappy_py (import snappy_py)   textlike   8M       8.00      408690       0.049     6983.48     4992.22    
python-snappy (import snappy)  random     64K      0.06      65542        1.000     4375.85     5612.78    
python-snappy (import snappy)  random     1M       1.00      1048627      1.000     5112.24     6599.80    
python-snappy (import snappy)  random     8M       8.00      8388996      1.000     1620.08     2996.24    
python-snappy (import snappy)  repetitive 64K      0.06      3080         0.047     4435.91     2261.54    
python-snappy (import snappy)  repetitive 1M       1.00      49235        0.047     5981.81     2450.51    
python-snappy (import snappy)  repetitive 8M       8.00      393860       0.047     5003.61     1976.17    
python-snappy (import snappy)  textlike   64K      0.06      3194         0.049     4430.12     4343.35    
python-snappy (import snappy)  textlike   1M       1.00      51085        0.049     6005.18     5179.45    
python-snappy (import snappy)  textlike   8M       8.00      408690       0.049     4806.67     2894.25    
cramjam (import cramjam)       random     64K      0.06      65554        1.000     1794.07     2621.00    
cramjam (import cramjam)       random     1M       1.00      1048714      1.000     2219.84     3351.00    
cramjam (import cramjam)       random     8M       8.00      8389642      1.000     1490.91     2315.09    
cramjam (import cramjam)       repetitive 64K      0.06      3098         0.047     2144.04     1610.51    
cramjam (import cramjam)       repetitive 1M       1.00      49418        0.047     3120.36     1837.56    
cramjam (import cramjam)       repetitive 8M       8.00      395274       0.047     2792.03     1660.05    
cramjam (import cramjam)       textlike   64K      0.06      3212         0.049     2153.98     2230.35    
cramjam (import cramjam)       textlike   1M       1.00      51268        0.049     3034.38     2961.80    
cramjam (import cramjam)       textlike   8M       8.00      410104       0.049     2753.58     2465.15    

CompRatio = compressed_bytes / original_bytes
```