# FG Troubleshooting (Quick Guide)

This page lists common failure modes when onboarding or modifying a site.

---

## 1) No files found or nothing splits

Likely causes:
- wrong hfPth
- wrong fileExt or fileType
- headerLines mismatch causes the reader to reject data
- date window does not satisfy the epoch condition using Dates

What to check:
- confirm dbIni Instrument hfPth exists and contains expected raw files
- confirm fileExt matches real files
- confirm dateStr is after the epoch start

---

## 2) Split works but structures are missing or empty

Likely causes:
- parsing mismatch delimiter header tv columns
- dataOutputs names do not match actual output filenames
- SmartFlux time handling not supported in your local processing scripts

What to check:
- inspect one raw file and confirm delimiter and header assumptions
- confirm output naming conventions

---

## 3) Vectors exist but FG calculations are wrong or missing

Likely causes:
- incorrect plotCalcs mapping
- missing manual measurements or heights
- TGA alignment parameters wrong shiftDefault lagEst levelTime startLevel
- climate station missing or wrong

What to check:
- verify plot mapping against tower layout
- verify manifold timing and start level
- treat shiftDefault as tunable and update in epochs if it changed

---

## 4) Subtle bias or drift in gradients or fluxes

Likely causes:
- sonicOffset incorrect
- incorrect lag estimates
- unmodeled change in tubing or manifold behavior over time

What to do:
- confirm sonic orientation and apply correct offset
- estimate lags using diagnostics and update lagEst and shiftDefault
- introduce a new Dates epoch when configuration changes
