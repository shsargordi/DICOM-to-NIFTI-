import glob
import os 
import pydicom
import pandas as pd


# Targets only RTSTRUCT*.dcm files, processes them only if ROI count > 10, and uses a clearer reference-CT selection (match by StudyDate, otherwise first CT (It is taken before treatment and could be better aligned with the patient’s MRI.)) for a more controlled RTSTRUCT export.

dicom_folder = '/path/to/DataDicom/'
output_folder = '/path/to/Processed/'


def get_all_subdirectories(folder_path):
    subdirectories = []
    for root, dirs, files in os.walk(folder_path):
        for dir in dirs:
            subdirectories.append(os.path.join(root, dir))
    return subdirectories

def find_rtstruct_files(patient_dir):
    """Find all RTSTRUCT files in the patient directory (not in subdirectories)"""
    return glob.glob(os.path.join(patient_dir, "RTSTRUCT*.dcm"))

def find_reference_ct(patient_dir, rtstruct_file):
    """Find the appropriate reference CT for a given RTSTRUCT file"""
    try:
        ds = pydicom.dcmread(rtstruct_file)
        study_date = ds.StudyDate
        # First try to find CT with matching date
        ct_dirs = glob.glob(os.path.join(patient_dir, f"CT.{study_date}*"))
        if ct_dirs:
            return sorted(ct_dirs)[0]  # Return first matching CT
        # If no matching date, return first CT directory
        all_ct_dirs = glob.glob(os.path.join(patient_dir, "CT.*"))
        return sorted(all_ct_dirs)[0] if all_ct_dirs else None
    except:
        return None

def dcm_to_nii(list_p=sorted(os.listdir(dicom_folder)),
               output_folder=output_folder, CorTab=None):
    
    for p_nb in list_p:
        patient_dir = os.path.join(dicom_folder, p_nb)
        output_dir = os.path.join(output_folder, p_nb)
        
        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Find all RTSTRUCT files in patient directory
        rtstruct_files = find_rtstruct_files(patient_dir)
        
        for rtstruct_file in rtstruct_files:
            try:
                # Read RTSTRUCT file to check number of structures
                ds = pydicom.dcmread(rtstruct_file)
                struct_size = len(ds.StructureSetROISequence)
                
                # Only process if there are more than 10 structures
                if struct_size > 10:
                    # Find reference CT
                    reference_ct = find_reference_ct(patient_dir, rtstruct_file)
                    
                    if reference_ct:
                        output_prefix = os.path.join(output_dir, 'RTStruct')
                        
                        command = (
                            f"PROOT_NO_SECCOMP=1 "
                            f"plastimatch convert "
                            f"--input {rtstruct_file} "
                            f"--referenced-ct {reference_ct} "
                            f"--output-prefix {output_prefix} "
                            f"--output-type float "
                            f"--prefix-format nii.gz "
                            f"--default-value -1024 "
                            f"--prune-empty"
                        )
                        
                        print(f"Processing RTSTRUCT: {os.path.basename(rtstruct_file)}")
                        print(f"Reference CT: {os.path.basename(reference_ct)}")
                        print(f"Executing command: {command}")
                        
                        os.system(command)
                    else:
                        print(f"No reference CT found for RTSTRUCT: {rtstruct_file}")
                else:
                    print(f"Skipping {rtstruct_file} - too few structures ({struct_size})")
                    
            except Exception as e:
                print(f"Error processing {rtstruct_file}: {str(e)}")
                continue

def main():
    list_to_process = sorted(os.listdir(dicom_folder))
    dcm_to_nii(list_to_process)

if __name__ == "__main__":
    main()