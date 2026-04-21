# Data Transfer Workflows

## Overview

This document describes how field data are transferred from site computers to the lab processing system across all CanN2Onet sites.

While transfer mechanisms vary (Google Drive API, Dropbox, DriveHQ), all sites follow a common logical workflow:

```
Site Computer → Transfer Mechanism → Lab Staging → Unpack/Organize → Archive → Processing
```

This document provides:

* a high-level architecture
* a common workflow (pseudocode)
* transfer mechanism patterns
* a comparison table across sites
* site-specific implementations

---

## 1. Data Transfer Architecture

Different sites use different transfer mechanisms depending on:

* field connectivity
* infrastructure constraints
* historical implementation

### Supported Transfer Mechanisms

* Google Drive API (scripted upload/download)
* Dropbox synchronization (passive sync)
* DriveHQ / FTP-style cloud services
* Hybrid approaches

### Key Design Principles

* Data ingestion is separated from processing
* Transfer is fault-tolerant and restartable
* Files are archived after transfer
* Temporary staging is used before processing

---

## 2. Common Workflow (Pseudocode)

```text
ALGORITHM DATA_TRANSFER_WORKFLOW

INPUT:
    site-generated data files (tower, TGA, manual)
    transfer mechanism (API / Dropbox / DriveHQ)

OUTPUT:
    organized data in lab repository
    archived transfer files

BEGIN

1. DETECT new data files
    - via API listing, folder scan, or sync client

2. TRANSFER to lab staging
    - download or sync into local staging directory

3. FOR each transferred file:

    IF file is compressed (ZIP):
        copy to temporary directory
        unzip into destination folder

    DETERMINE destination based on:
        - data type (TGA, EC, manual, etc.)
        - site configuration
        - date extracted from filename

    COPY data to:
        (a) main repository
        (b) site mirror directory (if applicable)

    IF file requires conversion (e.g., RawData):
        run conversion utility
        store converted output

    MOVE original transfer file to archive location

    VERIFY transfer success (e.g., file size match)

    IF verification successful:
        remove temporary/local copy
        remove remote copy (if API-based)

END FOR

END
```

---

## 3. Transfer Mechanism Patterns

### 3.1 Google Drive API

#### Overview

* Used by: ON1, ON3, AB1, AB2 (partial), SK1 (manual data)
* Fully scripted upload and download

#### Workflow

```
Site → Local "files" folder → Google Drive (API upload)
     → Lab download script → Local staging → Processing
```

#### Implementation Details

* Authentication via service account (`wagner-riddle-auth.json`)
* Upload:

  * files copied into local `files/` directory
  * uploaded using Drive API (`files().create`)
* Download:

  * list files using `files().list()`
  * download via `MediaIoBaseDownload`
* Cleanup:

  * delete from Drive after successful processing
* Acts as **temporary staging**, not long-term storage

---

### 3.2 Dropbox Sync

#### Overview

* Used by: SK1 (tower + TGA)
* Passive synchronization (no upload script)

#### Workflow

```
Site Dropbox folder → Cloud sync → Lab Dropbox folder → Processing
```

#### Implementation Details

* Site computer:

  * Dropbox client monitors directories
  * automatic upload (no scripting)
* Lab computer:

  * Dropbox syncs files locally
* Differences from API:

  * no explicit upload/download control
  * timing depends on sync completion
  * no automatic deletion after processing

---

### 3.3 DriveHQ / FTP-style Transfer

#### Overview

* Used by: AB2 (tower data)
* External cloud/FTP-style system

#### Workflow

```
Site → DriveHQ upload → Lab retrieval script → Processing
```

#### Implementation Details

* Upload handled externally (not in current scripts)
* Lab side:

  * scheduled retrieval/download
* Differences:

  * separate authentication system
  * less integrated with pipeline
  * typically used for tower datasets

---

## 4. Site Comparison Table

| Site | Tower Data                 | TGA Data   | Manual / Heights | Method Type |
| ---- | -------------------------- | ---------- | ---------------- | ----------- |
| ON1  | Google API                 | Google API | Google API       | Fully API   |
| ON3  | Google API                 | Google API | Google API       | Fully API   |
| SK1  | Dropbox                    | Dropbox    | Google API       | Hybrid      |
| AB1  | External / local + scripts | Google API | Google API       | Hybrid      |
| AB2  | DriveHQ                    | Google API | Google API       | Hybrid      |

---

## 5. Site-Specific Implementations

---

### 5.1 ON1 – Google Drive API Transfer

#### Overview

* Transfer method: Google Drive API
* Data: tower, TGA, manual, logbook
* Automation: Python + Task Scheduler

#### Workflow Summary

* Site: collect → rename → zip → upload
* Lab: download → unzip → organize → archive → cleanup

#### Destinations

**Main repository**

```
ses-lab-data\E26\hfdata\...
ses-lab-data\E26\database\...
```

**Mirror copy**

```
ses-lab-data\Guelph_agromet\sites\ON1\...
```

**Transfer archive**

```
ses-lab-data\Transfers\E26\...
```

#### Notes

* Files copied to both main repository and mirror
* ZIP files archived after processing
* Files removed from Drive only after verification

---

### 5.2 ON3 – Google Drive API Transfer

#### Overview

* Same architecture as ON1
* Different site configuration and paths

#### Differences from ON1

* station naming
* directory structure
* fewer/more instruments

---

### 5.3 SK1 – Dropbox + Google API (Hybrid)

#### Overview

* Tower + TGA: Dropbox
* Manual data: Google API

#### Workflow Summary

* Dropbox handles high-frequency data
* API handles manual/logbook files

#### Key Differences

* No upload script for tower data
* Sync timing depends on Dropbox
* No automatic deletion of remote files

---

### 5.4 AB1 – Hybrid Transfer

#### Overview

* Uses Google API for TGA + manual data
* Additional scripts for SmartFlux / summary data

#### Notes

* Multiple independent ingestion paths
* Requires coordination at processing stage

---

### 5.5 AB2 – DriveHQ + Google API (Hybrid)

#### Overview

* Tower data: DriveHQ
* TGA + manual: Google API

#### Workflow Summary

* DriveHQ used for tower (SmartFlux) datasets
* API used for TGA and other structured datasets

#### Key Differences

* External cloud replaces site upload script
* Lab retrieval handled separately
* Integrated downstream with same processing pipeline

---

## Summary

Despite different transfer mechanisms, all sites converge into a unified workflow:

```
Transfer → Staging → Organization → Archive → Processing
```

This design allows flexibility at the site level while maintaining consistency in downstream processing.
