
import pydicom
from pydicom import dcmread
from pydicom.fileset import FileSet
import os 
import glob 
import numpy as np
from tqdm import tqdm

# RTDOSE only: Scans patient folders for RTDOSE files, computes max dose (using DoseGridScaling), selects the highest-dose file (PLAN/BEAM), and converts that dose grid to NIfTI.

def get_all_subdirectories(folder_path):
    subdirectories = []
    
    for root, dirs, files in os.walk(folder_path):
        for dir in dirs:
            subdirectories.append(os.path.join(root, dir))
    
    return subdirectories

def get_all_files(directory):
    all_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            all_files.append(os.path.join(root, file))
            
    return all_files

def get_dose_max(dicom_dose):
    # Extract the dose grid scaling factor
    dose_grid_scaling = dicom_dose.DoseGridScaling
    # Extract the pixel data (dose grid)
    dose_grid = dicom_dose.pixel_array
    # Convert the pixel data to actual dose values
    actual_dose_grid = dose_grid * dose_grid_scaling
    # Find the maximum dose value
    max_dose_value = np.max(actual_dose_grid)
    # Print the maximum dose value
    return max_dose_value


path_raw = '/path/to/DataDicom/'
path_output = '/path/to/Processed/'



#list_patient = os.listdir(path_raw)
#patients with beam dosi
list_beam = ['HSL-5657471', 'HSL-0745724', 'HSL-5477445', 'HSL-5718521', 'HSL-5672785', 'HSL-5633631', 'HSL-5625917', 'HSL-5555798', 'HSL-5653123', 'HSL-5618976', 'HSL-5642174', 'HSL-5589382', 'HSL-5578236', 'HSL-0190945', 'HSL-0753213', 'HSL-0173954', 'HSL-5718228', 'HSL-0998790', 'HSL-5751119', 'HSL-5533702', 'HSL-5431877', 'HSL-5710062']
list_patient = [p for p in list_beam if os.path.exists(os.path.join(path_raw, p))]

##No Oro

# for pnb in tqdm(sorted(list_patient)):
#     try:
#         pathp = path_raw + pnb
#         files = get_all_files(pathp)  # Get all files directly in the patient folder

#         # Store biggest dose
#         dose_max = 0
#         dose_max_path = ''

#         for file in files:
#             if file.split('/')[-1][:5] == 'RTDOS':  # Ensure it correctly identifies RTDOSE files
                
#                 dicom = pydicom.dcmread(file)
#                 modality = dicom['Modality']
#                 # Check if file is a dose
#                 if modality.value == 'RTDOSE':
#                     type_dose = dicom[('3004', '000a')]
#                     # Check if file is a Dose PLAN 
#                     if type_dose.value == 'PLAN':
#                         max_plan = get_dose_max(dicom)
#                         # Get the max dose plan 
#                         if max_plan > dose_max:
#                             dose_max = max_plan
#                             dose_max_path = file


#         print(f"Final dose_max_path: {dose_max_path}")
#         print(f"Patient number: {pnb}")
#         output = path_output + "{:05d}".format(int(pnb)) + '/dose_PLAN.nii.gz'
#         print(f"Output path: {output}")
        
#         # Create output directory if it doesn't exist
#         output_dir = os.path.dirname(output)
#         print(f"Creating directory: {output_dir}")
#         os.makedirs(output_dir, exist_ok=True)

#         # Use plastimatch
#         command = f"PROOT_NO_SECCOMP=1 plastimatch convert --input {dose_max_path} --output-dose-img {output} --output-type float --prefix-format nii.gz --default-value 0 --prune-empty"
#         os.system(command)
#     except:
#         continue

for pnb in tqdm(sorted(list_patient)):
    try:
        pathp = path_raw + pnb
        files = get_all_files(pathp)
        print(f"\nProcessing patient {pnb}")
        print(f"Found {len(files)} files")
        
        rtdose_files = [f for f in files if os.path.basename(f)[:5] == 'RTDOS']
        print(f"Found {len(rtdose_files)} RTDOSE files:")
        
        dose_max = 0
        dose_max_path = ''
        
        for file in rtdose_files:
            print(f"\nChecking file: {file}")
            try:
                dicom = pydicom.dcmread(file)
                modality = dicom['Modality']
                print(f"Modality: {modality.value}")
                
                # for plan dosi only
                # if modality.value == 'RTDOSE':
                #     type_dose = dicom[('3004', '000a')]
                
                #     print(f"Dose Type: {type_dose.value}")
                    
                #     max_plan = get_dose_max(dicom)
                #     print(f"Max dose: {max_plan}")
                    
                #     if type_dose.value == 'PLAN':
                #         if max_plan > dose_max:
                #             dose_max = max_plan
                #             dose_max_path = file
                #             print(f"Selected as highest dose PLAN file: {dose_max_path}")
                #     else:
                #         print("Not a PLAN dose type")
                # else:
                #     print("Not an RTDOSE modality")

                #for both plan and beam dosi
                if modality.value == 'RTDOSE':
                    type_dose = dicom[('3004', '000a')]
                    max_plan = get_dose_max(dicom)
                    if max_plan > dose_max:
                        dose_max = max_plan
                        dose_max_path = file
                                    
            except Exception as e:
                print(f"Error reading DICOM file {file}: {str(e)}")
                continue
        
        if dose_max_path:
            try:
                # Keep original filename for the output
                original_filename = os.path.basename(dose_max_path)
                output_filename = os.path.splitext(original_filename)[0] + '.nii.gz'
                output = os.path.join(path_output, pnb, output_filename)
                print(f"Creating output: {output}")
                
                output_dir = os.path.dirname(output)
                os.makedirs(output_dir, exist_ok=True)
                
                command = f"PROOT_NO_SECCOMP=1 plastimatch convert --input {dose_max_path} --output-dose-img {output} --output-type float --prefix-format nii.gz --default-value 0 --prune-empty"
                print(f"Running command: {command}")
                result = os.system(command)
                
                if result == 0:
                    print(f"Successfully processed {pnb}")
                else:
                    print(f"Plastimatch command failed for {pnb} with exit code {result}")
            
            except Exception as e:
                print(f"Error processing output for {pnb}: {str(e)}")
        else:
            print(f"No valid RTDOSE PLAN file found for {pnb}")
            
    except Exception as e:
        print(f"Error processing patient {pnb}: {str(e)}")
        continue