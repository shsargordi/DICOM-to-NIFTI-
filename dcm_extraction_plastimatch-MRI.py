
import glob
import os 
import pydicom
from tqdm import tqdm


#(MRI only): Recursively finds MR-series folders (names starting with "MR") and converts MRI DICOM series to NIfTI using plastimatch with --modality MR (runs plastimatch locally, not via udocker).

dicom_folder = '/path/to/DataDicom/'
output_folder = '/path/to/Processed/'


def dcm_to_nii(list_p=sorted(os.listdir(dicom_folder)),
              output_folder=output_folder,CorTab=None):
    

    #For each patient
    for p_nb in tqdm(list_p):
        
        
        subdirectories = get_all_subdirectories(dicom_folder+p_nb+'/')

        #Rename files to fix gaps in strings 
        for folders in subdirectories:
                    
                    new_name = "/".join(folders.split('/')[:-1]) + '/' + ("_".join((folders.split('/')[-1]).split(' ')))
                    os.rename(src=f'{folders}',dst=f'{new_name}')


        subdirectories = get_all_subdirectories(dicom_folder+p_nb+'/')
        

        #Make output dir
        #Make directory for ouput

        output_dir= output_folder+p_nb+'/'
        if not os.path.exists(output_dir+'/'):
            os.makedirs(output_dir)
       
        
        for folder in subdirectories:
            #print(folder)
            #if ((folder.split('/')[-1][:2]=='T1') or ( folder.split('/')[-1][:2]=='T2')):
            if ((folder.split('/')[-1][:2]=='MR')):
                    print(folder)
                    
            #if (folder.startswith('MR')):
                    #print('yes')
                    
                    
                    name = folder.split('/')[-1]
                    
                    
                    try:
                    
                        input = folder
                        #set output file
                        output = output_folder+p_nb+'/' + name +'.nii.gz'
                       

                        command="PROOT_NO_SECCOMP=1\
                                plastimatch convert\
                                --input"+" " +f'{input}' +"\
                                --output-img"+" " + output +"\
                                --output-type float \
                                --modality MR \
                                --prefix-format nii.gz \
                                --default-value 0 \
                                --prune-empty"
                        
                        os.system(command)

                    except:
                        continue

def get_all_subdirectories(folder_path):
    subdirectories = []
    
    for root, dirs, files in os.walk(folder_path):
        for dir in dirs:
            subdirectories.append(os.path.join(root, dir))
    
    return subdirectories


def main():

    list_to_process=sorted(os.listdir(dicom_folder))
    
    #send query on rest of patients to process
    dcm_to_nii(list_to_process)
        
if __name__ == "__main__":
    main()
