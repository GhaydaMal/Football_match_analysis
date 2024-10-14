from ultralytics import YOLO

#download the best weight of yolov5 model
model = YOLO('models/best.pt')

results = model.predict('input_videos/08fd33_4.mp4', save=True)

#print the first frame only
print(results[0])
print("---------------------------------------------------------")
#print all boxes info in first frame
for box in results[0].boxes:
    print(box)

