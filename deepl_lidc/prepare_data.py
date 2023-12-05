import pylidc as pl
import numpy as np
import matplotlib.pyplot as plt
import csv
from deepl_lidc import utils
import os 
import pydicom
import numpy as np
from torch.utils.data import Dataset


patients_ids = []
path = "C:\Pliki\sem5\Advanced_data_mining\DEEPL-LIDC\input\LIDC-01-10\manifest-1701190789220"
with open(path+"\metadata.csv", newline='', encoding='utf-8') as csvfile:
    csv_reader = csv.DictReader(csvfile)
    for row in csv_reader:
        subject_id = row['Subject ID']
        if subject_id not in patients_ids:
            patients_ids.append(subject_id)

annotations_ids= [[] for _ in patients_ids]
malignancy_avg = [0 for _ in patients_ids]


def link_patients_with_annotations():
    annot = pl.query(pl.Annotation)
    for x in annot:
        if x.scan.patient_id in patients_ids:
            index = patients_ids.index(x.scan.patient_id)
            annotations_ids[index].append(x.id)

def visualize_by_pid(pid):
    plt.figure(figsize=(3, 3))
    plt.set_cmap('gray')
    scan = pl.query(pl.Scan).filter(pl.Scan.patient_id == pid).first()
    vol = scan.to_volume()
    nodules = scan.cluster_annotations()
    scan.visualize(nodules)

def calculate_malignancy_avg():
    for i in range (len(patients_ids)):
        sum=0
        if annotations_ids[i]:
            for j in annotations_ids[i]:
                annot = pl.query(pl.Annotation).filter(pl.Annotation.id == j).first()
                sum+= annot.malignancy
            malignancy_avg[i]=sum/len(annotations_ids[i])


def print_patients_and_annotations():
    for i in range (len(patients_ids)):
        print(f'patient_ID: {patients_ids[i]}, patient_malignancy_acg: {malignancy_avg[i]}, annotations_ids: {annotations_ids[i]}')

def print_annotations_by_patient_index(k):
    print(f"Annotations linked to patient {patients_ids[k]}")
    for i in annotations_ids[k]:
        annot = pl.query(pl.Annotation).filter(pl.Annotation.id == i).first()
        print(f"     Annotation.id = {i}: malignancy = {annot.malignancy}")
 #        annot.print_formatted_feature_table()


 ############################Choose the middle slice ##################################
def get_path_to_middle_slice(pid):
    path_pid = f'{path}\LIDC-IDRI\{pid}'
    print(path_pid)
    files = os.listdir(path_pid)
    path_pid=f'{path_pid}\{files[0]}'
    files = os.listdir(path_pid)
    path_pid=f'{path_pid}\{files[0]}'
    files = os.listdir(path_pid)

    number_of_slices = len(files) - 1
    middle_slice_index = int(number_of_slices/2)

    index =""
    if(middle_slice_index<10):
        index="00"+str(middle_slice_index)
    elif (middle_slice_index<100):
        index="0"+str(middle_slice_index)
    else:
        index=str(middle_slice_index)
    index='1-'+index
    path_to_middle_slice = f'{path_pid}\{index}.dcm'
    print(path_to_middle_slice)
    return path_to_middle_slice
    '''
    dicom_data = pydicom.dcmread(path_to_middle_slice)
    image_array = dicom_data.pixel_array
    plt.imshow(image_array, cmap='gray')
    plt.title('DICOM Image')
    plt.show()
    '''

 ##########################PYTORCH DATASET#################################
class CustomDataset(Dataset):
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.file_list = os.listdir(data_dir)

    def __len__(self):
        return len(self.file_list)

    def __getitem__(self, idx):
        file_path = get_path_to_middle_slice(patients_ids[idx])

        dicom_data = pydicom.dcmread(file_path)
        image_array = dicom_data.pixel_array.astype(np.float32)

        # Przetwarzanie danych obrazu (normalizacja, zmiana rozmiaru, itp.)
        # Tutaj możesz dodać swoje operacje przetwarzania obrazu

        # Przyporządkuj etykietę (możesz uzyskać ją z bazy danych lub pliku etykiet)
        label = labels[idx]  # Przykładowa etykieta - dostosuj do swoich potrzeb

        return {"image": image_array, "label": label}
 
################# DATA PREPROCESSING
link_patients_with_annotations()
calculate_malignancy_avg()

##
malignant_lower_bound = 3
labels = [int(x>malignant_lower_bound) for x in malignancy_avg]
print(labels)
####################################

print_patients_and_annotations()
print_annotations_by_patient_index(4)


pid = "LIDC-IDRI-0004"
#utils.visualize_by_pid(pid)
get_path_to_middle_slice(pid)

############ create dataset
data_directory = path+"\LIDC-IDRI"
custom_dataset = CustomDataset(data_directory)

# Pobierz pierwszy element z zestawu danych

for i in range (len(patients_ids)):
    sample = custom_dataset[i]
    image = sample["image"]
    label = sample["label"]
    print("Image Shape:", image.shape)
    print("Label:", label)
    print("Image:",image)
    plt.imshow(image, cmap='gray')  # 'cmap' określa kolor mapy; 'gray' oznacza obraz w odcieniach szarości
    plt.title(f'DICOM from patient {patients_ids[i]}')
    plt.show()


