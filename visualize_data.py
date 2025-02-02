import pylidc as pl
import numpy as np
import matplotlib.pyplot as plt
import csv

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
 #         annot.print_formatted_feature_table()


################# DATA PREPROCESSING
link_patients_with_annotations()
calculate_malignancy_avg()

##
malignant_lower_bound = 2.5
labels = [int(x>malignant_lower_bound) for x in malignancy_avg]
print(labels)
####################################

print_patients_and_annotations()
print_annotations_by_patient_index(4)
pid = 'LIDC-IDRI-0004'
#visualize_by_pid()




