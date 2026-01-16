## What this repository do

This repository provides utilities to preprocess radiotherapy head-and-neck DICOM data and convert it to NIfTI for downstream experiments. Supported modalities include:
- Planning **CT**
- Treatment-time **CBCT**
- Treatment-time **MRI**
- **RTSTRUCT** (structure/segmentation contours)
- **RTDOSE** (dose grid)

All conversions rely on **plastimatch** (either containerized via `udocker` or local execution depending on the script).


## Preprocessing steps (end-to-end)

1. **Set input/output paths**
   - In each script, set:
     - **Source:** `dicom_folder = '/path/to/DataDicom/'`  (root folder that contains one subfolder per patient)
     - **Destination:** `output_folder = '/path/to/Processed/'` (output root where one subfolder per patient will be created)

2. **Convert CT series (if present)**
   - Run either:
     - `dcm_extraction_plastimatch-CT-CBCT.py` (CT + CBCT), or
     - `dcm_extraction_plastimatch-CT-CBCT-RTSTRUCT.py` (CT + CBCT + RTSTRUCT)
   - The scripts convert any patient subfolder whose name starts with `CT` into `CT*.nii.gz`.

3. **Convert CBCT series (if present)**
   - Using the same CT/CBCT scripts above, the scripts convert any patient subfolder whose name starts with `CBCT` into `CBCT*.nii.gz` (or `cbct.<date>.nii.gz`, depending on the script naming).

4. **Convert RTSTRUCT**
   - Run either:
     - `dcm_extraction_plastimatch-CT-CBCT-RTSTRUCT.py` (RTSTRUCT conversion included), or
     - `dcm_extraction_plastimatch-RTSTRUCT.py` (RTSTRUCT only)
   - RTSTRUCT files are matched to a **reference CT** (preferably same `StudyDate` when available, otherwise the first CT found), then exported as NIfTI masks with prefix `RTStruct...`.

5. **Convert RTDOSE**
   - Run: `dcm_extraction_plastimatch-dosi.py`
   - This script searches for `RTDOSE` DICOM files (e.g., `RTDOS*`), selects the most relevant one (by highest max dose), and exports it as a dose NIfTI (`*.nii.gz`) under the patient output folder.

6. **Convert MRI**
   - Run: `dcm_extraction_plastimatch-MRI.py`
   - This script recursively finds folders whose name starts with `MR` and converts them to NIfTI using `--modality MR`.
