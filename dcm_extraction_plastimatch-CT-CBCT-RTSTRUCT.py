import glob
import os 
import pydicom

# (CT + CBCT + RTSTRUCT): Converts DICOM CT folders, CBCT folders, and RTSTRUCT DICOM files to NIfTI using plastimatch in a udocker container (RTSTRUCT masks are exported using a referenced CT).


dicom_folder = '/path/to/DataDicom/'
output_folder = '/path/to/Processed/'

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
            if os.path.isdir(dcm_path) and os.path.basename(dcm_path)[:2] == 'CT':
                print('This is a CT folder')
                ct_name = os.path.basename(dcm_path)     
                print('Processing CT:', ct_name)    

                command = (
                    "PROOT_NO_SECCOMP=1 udocker run "
                    "--volume={}:/mnt/input "
                    "--volume={}:/mnt/output "
                    "mayoqin/plastimatch:latest "
                    "plastimatch convert "
                    "--input /mnt/input "
                    "--output-img /mnt/output/{}.nii.gz "
                    "--output-type float "
                    "--prefix-format nii.gz "
                    "--default-value -1024 "
                    "--prune-empty"
                ).format(dcm_path, output_dir, ct_name)
                print("Executing command:", command)
                os.system(command)
                
            # IF RTSTRUCT (file)
            elif os.path.isfile(dcm_path) and os.path.basename(dcm_path).startswith('RTSTRUCT'):
                print('This is an RTSTRUCT file')
                
                # Read the RTSTRUCT file
                rtstruct_file = dcm_path
                ds = pydicom.dcmread(rtstruct_file)
                study_date = ds.StudyDate
                print('Study Date:', study_date)

                # Get the reference CT folder
                ct_folders = glob.glob(os.path.join(dicom_folder, p_nb, "CT*"))
                if len(ct_folders) > 1:
                    ref_ct_dir = os.path.join(dicom_folder, p_nb, "CT." + study_date)
                else:
                    ref_ct_dir = ct_folders[0]
                print('Reference CT directory:', ref_ct_dir)

                # Mount the parent directory of the RTSTRUCT file
                rtstruct_parent_dir = os.path.dirname(rtstruct_file)

                print('Output name:', "RTStruct." + study_date + ".nii.gz")
                command = (
                    "PROOT_NO_SECCOMP=1 udocker run "
                    "--volume={}:/mnt/input "
                    "--volume={}:/mnt/output "
                    "--volume={}:/mnt/referenced_ct "
                    "mayoqin/plastimatch:latest "
                    "plastimatch convert "
                    "--input /mnt/input/{} "
                    "--output-prefix /mnt/output/RTStruct.{} "
                    "--referenced-ct /mnt/referenced_ct "
                    "--output-type float "
                    "--prefix-format nii.gz "
                    "--default-value -1024 "
                    "--prune-empty"
                ).format(rtstruct_parent_dir, output_dir, ref_ct_dir, os.path.basename(rtstruct_file), study_date)
                print("Executing command:", command)
                os.system(command)

            # IF CBCT (directory)
            elif os.path.isdir(dcm_path) and os.path.basename(dcm_path).startswith('CBCT'):
                print('This is a CBCT folder')
                date = os.path.basename(dcm_path)
                input_dir = dcm_path
                output_file = os.path.join(output_dir, date + ".nii.gz")

                command = (
                    "PROOT_NO_SECCOMP=1 udocker run "
                    "--volume={}:/mnt/input "
                    "--volume={}:/mnt/output "
                    "mayoqin/plastimatch:latest "
                    "plastimatch convert "
                    "--input /mnt/input "
                    "--output-img /mnt/output/{}.nii.gz "
                    "--output-type float "
                    "--prefix-format nii.gz "
                    "--default-value -1024 "
                    "--prune-empty"
                ).format(input_dir, output_dir, date)
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