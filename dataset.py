import os
from PIL import Image
import pandas as pd
import torch
from torch.utils.data import Dataset
import cv2
import numpy as np
from ast import literal_eval

import utils

class CustomDataset(Dataset):
    
    def __init__(self, CSV_PATH, input_height=360, input_width=640, scale=2, hp_radius=55):

        self.input_height = input_height
        self.input_width = input_width
        self.output_height = int(input_height/scale)
        self.output_width = int(input_width/scale)
        self.num_joints = 14
        self.hp_radius = hp_radius
        self.scale = scale
        # self.path_images = os.path.join(self.path_dataset, 'images')
        self.df = pd.read_csv(CSV_PATH, encoding='CP949', 
                              converters = { 'points': literal_eval,
                                    'p1':literal_eval,
                                    'p2':literal_eval,
                                    'p3':literal_eval,
                                    'p4':literal_eval,
                                    'p5':literal_eval,
                                    'p6':literal_eval,
                                    'p7':literal_eval,
                                    'p8':literal_eval}
                              )
        #print('len = {}'.format(len(self.data)))


    def filter_data(self):
        new_data = []
        for i in range(len(self.data)):
            max_elems = np.array(self.data[i]['points']).max(axis=0)
            min_elems = np.array(self.data[i]['points']).min(axis=0)
            if max_elems[0] < self.input_width and min_elems[0] > 0 and max_elems[1] < self.input_height and \
                    min_elems[1] > 0:
                new_data.append(self.data[i])
        return new_data

        
    def __getitem__(self, index):
        points = self.data['points'][index]

        img = utils._imread(self.data['frame_path'][index])
        img = cv2.resize(img, (self.output_width, self.output_height))
        inp = (img.astype(np.float32) / 255.)
        inp = np.rollaxis(inp, 2, 0)

        hm_hp = np.zeros((self.num_joints+1, self.output_height, self.output_width), dtype=np.float32)
        draw_gaussian = utils.draw_umich_gaussian

        for i in range(len(points)):
            if points[i][0] >=0 and points[i][0] <= self.input_width and points[i][1] >=0 and points[i][1] <= self.input_height:
            # if is_point_in_image(points[i][0], points[i][1], self.input_width, self.input_height):
                x_pt_int = int(points[i][0]/self.scale)
                y_pt_int = int(points[i][1]/self.scale)
                draw_gaussian(hm_hp[i], (x_pt_int, y_pt_int), self.hp_radius)

        # draw center point of tennis court
        x_ct, y_ct = utils.line_intersection((points[0][0], points[0][1], points[3][0], points[3][1]), (points[1][0], points[1][1],
                                                                                      points[2][0], points[2][1]))
        draw_gaussian(hm_hp[self.num_joints], (int(x_ct/self.scale), int(y_ct/self.scale)), self.hp_radius)
        
        return inp, hm_hp, np.array(points, dtype=int), img_name[:-4]
        
        
    def __len__(self):
        return len(self.data)


# __init__(self): 여기서 필요한 변수들을 선언한다. 전체 x_data와 y_data load하거나 파일목록을 load하자.
# __getitem__(self, index): index번째 data를 return하도록 코드를 짜야한다. (여기서 tensor를 return해야함)
# __len__(self): x_data나 y_data는 길이가 같으니까 아무 length나 return하면 된다

# class CustomDataset(Dataset):

#     def __init__(self, CSV_PATH):
#         super(CustomDataset, self).__init__()
#         self.height = 320
#         self.weight = 320
#         self.df = pd.read_csv(CSV_PATH, encoding='CP949', 
#                               converters = { 'points': literal_eval,
#                                     'p1':literal_eval,
#                                     'p2':literal_eval,
#                                     'p3':literal_eval,
#                                     'p4':literal_eval,
#                                     'p5':literal_eval,
#                                     'p6':literal_eval,
#                                     'p7':literal_eval,
#                                     'p8':literal_eval}
#                               )

#     def __getitem__(self, idx):
#         img_path = self.df['frame_path'][idx]
#         frame = utils._imread(img_path)
#         # h and w are swapped for landmarks because for images,
#         # x and y axes are axis 1 and 0 respectively
#         resizse_frame = cv2.resize(frame, (self.weight, self.height))
#         tensor_frame = (resizse_frame.astype(np.float32) / 255.)
#         # swap color axis because
#         # numpy image: H x W x C
#         # torch image: C x H x W
#         tensor_frame = np.rollaxis(tensor_frame, 2, 0)


#         points = list(self.df['points'][idx])
#         tensor_points = torch.FloatTensor(points)


#         hm_hp = np.zeros((self.num_joints+1, self.output_height, self.output_width), dtype=np.float32)
#         draw_gaussian = utils.draw_umich_gaussian

#         for i in range(len(points)):
#             if points[i][0] >=0 and points[i][0] <= self.input_width and points[i][1] >=0 and points[i][1] <= self.input_height:
#             # if is_point_in_image(points[i][0], points[i][1], self.input_width, self.input_height):
#                 x_pt_int = int(points[i][0]/self.scale)
#                 y_pt_int = int(points[i][1]/self.scale)
#                 draw_gaussian(hm_hp[i], (x_pt_int, y_pt_int), self.hp_radius)

#         # draw center point of tennis court
#         x_ct, y_ct = utils.line_intersection((points[0][0], points[0][1], points[3][0], points[3][1]), (points[1][0], points[1][1],
#                                                                                       points[2][0], points[2][1]))
#         draw_gaussian(hm_hp[self.num_joints], (int(x_ct/self.scale), int(y_ct/self.scale)), self.hp_radius)

#         return tensor_frame, hm_hp, tensor_points

#     def __len__(self):
#         return len(self.df['frame_path'])
    

