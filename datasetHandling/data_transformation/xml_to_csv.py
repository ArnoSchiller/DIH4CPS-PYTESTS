import os
import glob
import pandas as pd
import xml.etree.ElementTree as ET
import numpy as np

import argparse
parser = argparse.ArgumentParser(description='Convert xml files to csv file.')
parser.add_argument('--splitted', action='store_true', 
                    help='if selected a train_test_split will be done')
parser.add_argument('--xml_files_dir', type=str, default="TEMP_DOWNLOADS",
                    help='directory of the xml files, default: TEMP_DOWNLOADS.')

args = parser.parse_args()

def xml_to_csv(path):
    xml_list = []
    for xml_file in glob.glob(path + '/*.xml'):
        tree = ET.parse(xml_file)
        root = tree.getroot()
        for member in root.findall('object'):
            value = (root.find('filename').text,
                     int(root.find('size')[0].text),
                     int(root.find('size')[1].text),
                     member[0].text,
                     int(member[4][0].text),
                     int(member[4][1].text),
                     int(member[4][2].text),
                     int(member[4][3].text)
                     )
            xml_list.append(value)
    column_name = ['filename', 'width', 'height', 'class', 'xmin', 'ymin', 'xmax', 'ymax']
    xml_df = pd.DataFrame(xml_list, columns=column_name)
    return xml_df


def main(args):
    
    directory = os.path.join(os.path.dirname(__file__), args.xml_files_dir)
    xml_df = xml_to_csv(directory)
    xml_df.to_csv('images.csv', index=0)
    print('Successfully converted xml to csv.')

    if args.splitted:
        create_test_train_split()

def create_test_train_split():
    base_file = os.path.join(os.path.dirname(__file__), 'images.csv')
    labels = pd.read_csv(base_file)

    column_name = ['filename', 'width', 'height', 'class', 'xmin', 'ymin', 'xmax', 'ymax']

    test_percentage = 0.2
    num_labels = len(labels)
    num_test = int(test_percentage * num_labels)

    rand_index = np.random.randint(low=0, high=num_labels-1, size=num_test).tolist()
    print(len(rand_index))
    test_labels = []
    train_labels = []

    #print(labels)
    c = 0
    for index, label in labels.iterrows():
        if index < num_test:# rand_index.count(index):
            test_labels.append(label)
            c+=1
        else:
            train_labels.append(label)
            
    test_df = pd.DataFrame(test_labels, columns=column_name)
    test_df.to_csv('test.csv', index=0)

    train_df = pd.DataFrame(train_labels, columns=column_name)
    train_df.to_csv('train.csv', index=0)

    print("created train-test-split")



main(args)