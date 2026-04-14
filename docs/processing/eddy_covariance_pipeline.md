# Eddy Covariance Processing Pipeline

The **Eddy Covariance (EC)** branch of the processing system.

## Scope & overview

- High-frequency (typically 10 Hz) EC data
- Half-hour segmentation
- Flux calculation using EddyPro
- Post-processing and filtering prior to archiving

```mermaid
flowchart TB
  A1[10 Hz EC data] --> B1[Half-hour segmentation]
  B1 --> C1[Format and naming conventions]
  C1 --> D1[EddyPro project configuration]
  D1 --> E1[EddyPro run]
  E1 --> F1[Flux and diagnostics outputs]
  F1 --> G1[Site-level checks and flags]
  G1 --> H1[Filtering and QA/QC]
  H1 --> I1[Publish to database and archive]
```


## Notes

- Instrument-specific details (e.g., IRGASON, CSAT3, LI-7500) are handled upstream
- The EC workflow is largely external to the MATLAB db_* system
- Outputs are synchronized with FG products for unified archiving

Continue to the detailed [Eddy-Covariance Analysis](../eddy-covariance/fundamentals.md) to learn about the  setup and context.
