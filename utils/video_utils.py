import cv2

#reading frames from a video
def read_video(video_path):
    cap = cv2.VideoCapture(video_path) #Opens the video file 
    frames = []
    while True:
        #ret is boolean tells if frame was read successfully or video ended, frame contains the current frame.
        ret, frame = cap.read() #Reads the video frame-by-frame
        if not ret:
            break
        frames.append(frame)
    return frames

#saving frames into a new video
def save_video(ouput_video_frames,output_video_path):
    #use the XVID codec for compressing the video.
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(output_video_path, fourcc, 24, (ouput_video_frames[0].shape[1], ouput_video_frames[0].shape[0])) #24frames per sec , wedith, height 
    for frame in ouput_video_frames:
        out.write(frame)
    out.release() 