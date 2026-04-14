# Flux-Gradient Processing Pipeline

The **Flux-Gradient (FG)** processing chain implemented primarily in MATLAB:

```mermaid
flowchart TB
  A1[Logger TOA5 files] --> B1[db_split_hhour]
  B1 --> C1[db_process_hhour]
  C1 --> D1[db_process_hhour_sonic]
  C1 --> E1[db_process_hhour_TGA]
  D1 --> F1[db_create_vectors]
  E1 --> F1
  F1 --> G1[ASCII vector files and MAT outputs]
  G1 --> H1[db_make_heights]
  H1 --> I1[db_get_ENVCAN_clim]
  I1 --> J1[db_calc_FG]
  J1 --> K1[Filtering and QA/QC]
  K1 --> L1[Database products]
```

## Notes

- The main entry point is `db_update_site.m`
- Site behavior is controlled by the site specific initialization script `<SITE>_init_all.m`
- MATLAB (`.mat`) structure files and ASCII output vector files are generated for diagnostics, sharing and subsequent archiving

Continue to the detailed [Flux-Gradient Analysis](../flux-gradient/processing-pipeline.md) to learn about the  setup and context.
