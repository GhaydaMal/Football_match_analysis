import pickle
import cv2 #OpenCV library for computer vision
import numpy as np
import os
import sys 
sys.path.append('../')
from utils import measure_distance,measure_xy_distance

# estimates how much the camera has moved between video frames.
# used to adjust the positions of objects, ensuring that their movements are accurately represented.

class CameraMovementEstimator():
    def __init__(self,frame):
        self.minimum_distance = 5 #consider movements larger than this threshold (5 pixels). 

        # Lucas-Kanade Optical Flow Parameters for tracking points between frames in a video
        self.lk_params = dict(
            winSize = (15,15),
            maxLevel = 2,
            #process stops when the specified accuracy (epsilon) is reached or specified number of iterations
            criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT,10,0.03)
        )

        # converts frame of the video from color (BGR format) to grayscale.
        first_frame_grayscale = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        mask_features = np.zeros_like(first_frame_grayscale)
        mask_features[:,0:20] = 1
        mask_features[:,900:1050] = 1

        # detecting features (corners) in the frame.
        self.features = dict(
            maxCorners = 100,
            qualityLevel = 0.3,
            minDistance =3,
            blockSize = 7,
            mask = mask_features
        )
    
    # adjusts the positions of tracked objects based on the estimated camera movement.
    def add_adjust_positions_to_tracks(self,tracks, camera_movement_per_frame):
        for object, object_tracks in tracks.items():
            for frame_num, track in enumerate(object_tracks):
                for track_id, track_info in track.items():
                    position = track_info['position'] # get current position of the object
                    camera_movement = camera_movement_per_frame[frame_num] # Get the camera movement for the current frame.
                    ##subtracting the camera movement for that frame to get the actual movement of the object
                    position_adjusted = (position[0]-camera_movement[0],position[1]-camera_movement[1]) 
                    tracks[object][frame_num][track_id]['position_adjusted'] = position_adjusted
                    

    def get_camera_movement(self,frames,read_from_stub=False, stub_path=None):
        # Read the stub 
        if read_from_stub and stub_path is not None and os.path.exists(stub_path):
            with open(stub_path,'rb') as f:
                return pickle.load(f)

         #Initialize Camera Movement, zero = no movement
        camera_movement = [[0,0]]*len(frames)

        # Convert the First Frame from BGR to GrayScale
        old_gray = cv2.cvtColor(frames[0],cv2.COLOR_BGR2GRAY)
        # Optical flow helps estimate how objects have moved between two frames.
        old_features = cv2.goodFeaturesToTrack(old_gray,**self.features) #extract corners

        # Loop and Calculate Optical Flow for New Frame
        for frame_num in range(1,len(frames)):
            frame_gray = cv2.cvtColor(frames[frame_num],cv2.COLOR_BGR2GRAY)
            new_features, _,_ = cv2.calcOpticalFlowPyrLK(old_gray,frame_gray,old_features,None,**self.lk_params)
           
           #Initialize Variables for Maximum Movement
            max_distance = 0
            camera_movement_x, camera_movement_y = 0,0

# loop over each pair of new and old feature points(tracked between frames)and calculates the distance each feature moved between frames.
            for i, (new,old) in enumerate(zip(new_features,old_features)):
                new_features_point = new.ravel()
                old_features_point = old.ravel()

                distance = measure_distance(new_features_point,old_features_point)
                if distance>max_distance:
                    max_distance = distance
                    camera_movement_x,camera_movement_y = measure_xy_distance(old_features_point, new_features_point ) 
            
            if max_distance > self.minimum_distance:
                camera_movement[frame_num] = [camera_movement_x,camera_movement_y]
                old_features = cv2.goodFeaturesToTrack(frame_gray,**self.features)

            old_gray = frame_gray.copy()
        
        if stub_path is not None:
            with open(stub_path,'wb') as f:
                pickle.dump(camera_movement,f)

        return camera_movement
    
    def draw_camera_movement(self,frames, camera_movement_per_frame):
        output_frames=[]

        for frame_num, frame in enumerate(frames):
            frame= frame.copy()

            overlay = frame.copy()
            cv2.rectangle(overlay,(0,0),(500,100),(255,255,255),-1)
            alpha =0.6
            cv2.addWeighted(overlay,alpha,frame,1-alpha,0,frame)

            x_movement, y_movement = camera_movement_per_frame[frame_num]
            frame = cv2.putText(frame,f"Camera Movement X: {x_movement:.2f}",(10,30), cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,0),3)
            frame = cv2.putText(frame,f"Camera Movement Y: {y_movement:.2f}",(10,60), cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,0),3)

            output_frames.append(frame) 

        return output_frames