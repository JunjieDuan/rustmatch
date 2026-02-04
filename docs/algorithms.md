# Algorithm Details

This document explains the algorithms and optimizations used in RustMatch.

## Normalized Cross-Correlation (NCC)

RustMatch uses NCC for template matching, which is robust to brightness and contrast variations.

### Mathematical Formula

```
NCC(x,y) = Σ[(S(x+i,y+j) - S_mean) × (T(i,j) - T_mean)] / (n × S_std × T_std)
```

Where:
- `S`: Source image
- `T`: Template image
- `S_mean`, `T_mean`: Local/template mean values
- `S_std`, `T_std`: Local/template standard deviations
- `n`: Number of pixels in template

### Properties

- **Range**: [-1, 1], where 1 indicates perfect match
- **Invariance**: Robust to linear brightness/contrast changes
- **Computational Cost**: O(W × H × w × h) for naive implementation

## Optimization Techniques

### 1. Integral Images (Summed Area Tables)

Integral images enable O(1) computation of rectangular region statistics.

**Definition:**
```
I(x,y) = Σ Σ img(i,j)  for all i ≤ x, j ≤ y
```

**Region Sum Calculation:**
```
sum(x1,y1,x2,y2) = I(x2,y2) - I(x1,y2) - I(x2,y1) + I(x1,y1)
```

This reduces local mean/variance computation from O(w×h) to O(1).

### 2. Image Pyramids

For large images, we use a coarse-to-fine search strategy:

1. **Downsample** both source and template by factor 4-8
2. **Coarse search** on small images (fast)
3. **Refine** in original image around candidate locations

**Speedup**: ~16x for 4x downsampling

### 3. Parallel Processing

Row-wise parallelization using Rayon:
- Each thread processes a subset of rows
- Results are combined using parallel reduction
- Near-linear speedup with CPU cores

### 4. Memory Optimizations

- **Contiguous arrays**: Cache-friendly memory layout
- **Unsafe access**: Skip bounds checking in hot loops
- **Precomputation**: Template statistics computed once

## Non-Maximum Suppression (NMS)

For multi-target matching, NMS removes overlapping detections:

1. Sort matches by confidence (descending)
2. For each match, check overlap with selected matches
3. Keep match if no significant overlap exists

**Overlap criterion**: Center distance < template_size / 2
