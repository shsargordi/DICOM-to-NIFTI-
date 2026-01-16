import glob
import os 
import pydicom


#(CT + CBCT only): Converts only DICOM CT and CBCT folders to NIfTI using plastimatch locally (same goal as Code 'dcm_extraction_plastimatch-CT-CBCT-RTSTRUCT.py' for CT/CBCT, but without RTSTRUCT and without running inside udocker).


dicom_folder = '/path/to/DataDicom/'
output_folder = '/path/to/Processed/'


def find_matching_ct(ct_folders, study_date):
    """Find the best matching CT folder for the given study date."""
    # First try exact match
    exact_match = [f for f in ct_folders if f.split('.')[-2] == study_date]
    if exact_match:
        return exact_match[0]
    
    # If no exact match, try finding CT from the same date (ignoring trailing numbers)
    date_matches = [f for f in ct_folders if study_date in f]
    if date_matches:
        return date_matches[0]
    
    # If still no match, return the first CT folder
    return ct_folders[0] if ct_folders else None

def dcm_to_nii(list_p=sorted(os.listdir(dicom_folder)), output_folder=output_folder):
    # For each patient
    for p_nb in list_p:
        print('Patient:', p_nb)
        output_dir = os.path.join(output_folder, p_nb)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # For each file/folder in patient directory
        for dcm_path in glob.glob(os.path.join(dicom_folder, p_nb, "*")):
            print("Processing:", dcm_path)
            
            # IF CT (directory)
            # if os.path.isdir(dcm_path) and os.path.basename(dcm_path)[:2] == 'CT':
            #     print('This is a CT folder')
            #     ct_name = os.path.basename(dcm_path)     
            #     print('Processing CT:', ct_name)    

                # command = (
                #     "PROOT_NO_SECCOMP=1 udocker run "
                #     "--volume={}:/mnt/input "
                #     "--volume={}:/mnt/output "
                #     "mayoqin/plastimatch:latest "
                #     "plastimatch convert "
                #     "--input /mnt/input "
                #     "--output-img /mnt/output/{}.nii.gz "
                #     "--output-type float "
                #     "--prefix-format nii.gz "
                #     "--default-value -1024 "
                #     "--prune-empty"
                # ).format(dcm_path, output_dir, ct_name)
                # print("Executing command:", command)
                # os.system(command)
            if os.path.isdir(dcm_path) and os.path.basename(dcm_path)[:2] == 'CT':
                print('This is a CT folder')
                ct_name = os.path.basename(dcm_path)     
                print('Processing CT:', ct_name)    

                command = (
                    "plastimatch convert "
                    "--input {} "
                    "--output-img {}/{}.nii.gz "
                    "--output-type float "
                    "--prefix-format nii.gz "
                    "--default-value -1024 "
                    "--prune-empty"
                ).format(dcm_path, output_dir, ct_name)

                print("Executing command:", command)
                os.system(command)  # Add this line


                
            # # IF RTSTRUCT (file)
            # elif os.path.isfile(dcm_path) and os.path.basename(dcm_path).startswith('RTSTRUCT'):
            #     print('This is an RTSTRUCT file')
                
            #     # Read the RTSTRUCT file
            #     rtstruct_file = dcm_path
            #     ds = pydicom.dcmread(rtstruct_file)
            #     study_date = ds.StudyDate
            #     print('Study Date:', study_date)

            #     # Get all CT folders for this patient
            #     ct_folders = glob.glob(os.path.join(dicom_folder, p_nb, "CT*"))
            #     if not ct_folders:
            #         print("No CT folders found for reference!")
            #         continue
                    
            #     # Find the matching CT folder
            #     ref_ct_dir = find_matching_ct(ct_folders, study_date)
            #     if not ref_ct_dir:
            #         print("Could not find matching CT folder!")
            #         continue
                    
            #     print('Reference CT directory:', ref_ct_dir)

            #     # Use the full path for the reference CT
            #     ref_ct_path = os.path.join(dicom_folder, p_nb, ref_ct_dir)
            #     if not os.path.exists(ref_ct_path):
            #         print(f"Reference CT path does not exist: {ref_ct_path}")
            #         continue

            #     command = (
            #         "PROOT_NO_SECCOMP=1 udocker run "
            #         "--volume={}:/mnt/input "
            #         "--volume={}:/mnt/output "
            #         "--volume={}:/mnt/referenced_ct "
            #         "mayoqin/plastimatch:latest "
            #         "plastimatch convert "
            #         "--input /mnt/input/{} "
            #         "--output-prefix /mnt/output/RTStruct.{} "
            #         "--referenced-ct /mnt/referenced_ct "
            #         "--output-type float "
            #         "--prefix-format nii.gz "
            #         "--default-value -1024 "
            #         "--prune-empty"
            #     ).format(
            #         os.path.dirname(rtstruct_file),
            #         output_dir,
            #         ref_ct_path,
            #         os.path.basename(rtstruct_file),
            #         study_date
            #     )
            #     print("Executing command:", command)
            #     os.system(command)

            # # IF CBCT (directory)
            # elif os.path.isdir(dcm_path) and os.path.basename(dcm_path).startswith('CBCT'):
            #     print('This is a CBCT folder')
            #     date = os.path.basename(dcm_path)

                # command = (
                #     "PROOT_NO_SECCOMP=1 udocker run "
                #     "--volume={}:/mnt/input "
                #     "--volume={}:/mnt/output "
                #     "mayoqin/plastimatch:latest "
                #     "plastimatch convert "
                #     "--input /mnt/input "
                #     "--output-img /mnt/output/{}.nii.gz "
                #     "--output-type float "
                #     "--prefix-format nii.gz "
                #     "--default-value -1024 "
                #     "--prune-empty"
                # ).format(dcm_path, output_dir, date)
                # print("Executing command:", command)
                # os.system(command)
            # IF CBCT (directory)
            elif os.path.isdir(dcm_path) and os.path.basename(dcm_path)[:4] == 'CBCT':
                print('This is a CBCT folder')
                cbct_name = os.path.basename(dcm_path)     
                print('Processing CBCT:', cbct_name)

                command = (
                    "plastimatch convert "
                    "--input {} "
                    "--output-img {}/{}.nii.gz "
                    "--output-type float "
                    "--prefix-format nii.gz "
                    "--default-value -1024 "
                    "--prune-empty"
                ).format(dcm_path, output_dir, cbct_name)

                print("Executing command:", command)
                os.system(command)


def main():
    list_to_process = sorted(os.listdir(dicom_folder))
    already_processed = os.listdir(output_folder)
    if already_processed:
        for p_nb in already_processed:
            try:
                list_to_process.remove(p_nb)
            except ValueError:
                print(p_nb, 'not found in list to process.')
                pass

    dcm_to_nii(list_to_process)
        
if __name__ == "__main__":
    main()