from detetions.conter import ConterMaster
import torch
import numpy as np
import cv2 as cv
from ultralytics import YOLO
import supervision as sv
# from detectResults import DetectResultsMaster


'''
model = YOLO("yolov8n.pt")
results = model(frame)[0]
detections = sv.Detections.from_ultralytics(results)
'''
            
class ObjectDetectionMaster:
    def __init__(self,model_wights,dim=set()):
        self.model_wights=model_wights
        
        self.frame_width=dim[0]
        self.frame_height=dim[1]
        
        self.conter=ConterMaster()
        self.model = self.load_model()
        
        self.CLASS_NAMES_DICT = self.model.model.names
        
        self.box_annotator = sv.BoxAnnotator(
            thickness=2,
            text_thickness=2,
            text_scale=1
        )
        
        self.bounding_box_annotator = sv.BoundingBoxAnnotator()
        self.label_annotator = sv.LabelAnnotator()
        
    def load_model(self):
        
        model = YOLO(self.model_wights)
        model.fuse()
    
        return model

    def classNames(self):
        return self.CLASS_NAMES_DICT


    def model(self, frame,agnostic_nms):
        results = self.model(frame,agnostic_nms=agnostic_nms)
        return results
    
    def predictModel(self,source):
        resultsEggs= self.model.predict(source=source,conf=0.25,save=True)
        return resultsEggs

    def detectionSupervision(self,frame):
        results = self.model(frame)#, agnostic_nms=True
        result=results[0]
        detections = sv.Detections.from_ultralytics(result)
        
        # self.conter.conter(result,self.classNames())
        # print(bbox_id,"->id")
        labels = [
            self.model.model.names[class_id]
            for class_id
            in detections.class_id
        ]
        
        '''
        frame = self.box_annotator.annotate(
            scene=frame, 
            detections=detections, 
            labels=labels
        )
        '''
        
        annotated_image = self.bounding_box_annotator.annotate(
            scene=frame, detections=detections)
        annotated_image = self.label_annotator.annotate(
            scene=annotated_image, detections=detections, labels=labels)
        
        return annotated_image