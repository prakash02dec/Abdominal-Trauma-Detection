# Abdominal Trauma Detection

## ResNet

![image](https://github.com/prakash02dec/Abdominal-Trauma-Detection/blob/main/manuscript/Fig%204.resnet.png)


## EfficientNet

<img width="875" alt="image" src="https://github.com/prakash02dec/Abdominal-Trauma-Detection/blob/main/manuscript/Fig%205.efficientnet.png">


## VGG-16

![image](https://github.com/prakash02dec/Abdominal-Trauma-Detection/blob/main/manuscript/Fig%206.%20VGG16.png)


Run the Abdominal_trauma_detection.ipynb or Abdominal_trauma_detection.py.

## Dataset
The [Dataset](https://www.kaggle.com/competitions/rsna-2023-abdominal-trauma-detection/data) is taken from the Kaggle website.

### Files
train.csv Target labels for the train set. Note that patients labeled healthy may still have other medical issues, such as cancer or broken bones, that don't happen to be covered by the competition labels.

[train/test]_images/[patient_id]/[series_id]/[image_instance_number].dcm The CT scan data, in DICOM format. Scans from dozens of different CT machines have been reprocessed to use the run length encoded lossless compression format but retain other differences such as the number of bits per pixel, pixel range, and pixel representation. Expect to see roughly 1,100 patients in the test set.

[train/test]_series_meta.csv Each patient may have been scanned once or twice. Each scan contains a series of images.

image_level_labels.csv Train only. Identifies specific images that contain either bowel or extravasation injuries.
