import numpy as np

# original trained signed weights
W = np.array([
    [ 0.49017206, -0.14793849, -0.21196492, -0.03845493, -0.34618822,
     -0.20618300, -0.39352155,  0.47310162, -0.34876707],
    [ 0.12888297,  0.04021618,  0.10801066, -0.05738540,  0.04913563,
      0.30687930,  0.04887176, -0.12209833,  0.40992123]
], dtype=float)

# choose a common positive shift
shift = -W.min()

# shift all weights positive
W_shift = W + shift

# normalize globally so the largest shifted weight becomes 1.0
W_norm = W_shift / W_shift.max()

# reference / offset column
W_ref = np.full(W.shape[1], shift / W_shift.max())

# strongest programmed state
R_min = 60e3   # 60 kOhm

# optional cap for very weak weights
R_cap = 2e6    # 2 MOhm, change if needed

# map normalized weights to resistance
# max weight -> 60k, smaller weight -> larger resistance
R_col1 = np.clip(R_min / W_norm[0], R_min, R_cap)
R_col2 = np.clip(R_min / W_norm[1], R_min, R_cap)
R_ref  = np.clip(R_min / W_ref,     R_min, R_cap)

# round to 1 decimal place
R_col1 = np.round(R_col1, 1)
R_col2 = np.round(R_col2, 1)
R_ref  = np.round(R_ref, 1)

print("shift =", shift)

print("\nW_shift:")
print(W_shift)

print("\nW_norm:")
print(W_norm)

print("\nW_ref:")
print(W_ref)

print("\nR_col1 (ohms):")
print(R_col1)

print("\nR_col2 (ohms):")
print(R_col2)

print("\nR_ref (ohms):")
print(R_ref)

print("\nR_col1 (kOhms):")
print(np.round(R_col1 / 1e3, 1))

print("\nR_col2 (kOhms):")
print(np.round(R_col2 / 1e3, 1))

print("\nR_ref (kOhms):")
print(np.round(R_ref / 1e3, 1))
