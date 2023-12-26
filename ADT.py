# -*- coding: utf-8 -*-
"""Mini_project2.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/17F9nnKTJ6mWCCVliTTz_HhvBaVWw4qbH
"""

from google.colab import drive
drive.mount('/content/drive')

! python --version

! pip install -q git+https://github.com/keras-team/keras-cv

import os

import keras_cv
import keras_core as keras
from keras_core import layers

import numpy as np
import pandas as pd
import tensorflow as tf
from matplotlib import pyplot as plt
from sklearn.model_selection import train_test_split



PATH = "/content/drive/MyDrive/archive"

IMAGE_SIZE = [512, 512]
  BATCH_SIZE = 64
  EPOCHS = 8
  TARGET_COLS  = [
      "bowel_injury", "extravasation_injury",
      "kidney_healthy", "kidney_low", "kidney_high",
      "liver_healthy", "liver_low", "liver_high",
      "spleen_healthy", "spleen_low", "spleen_high",
  ]
  AUTOTUNE = tf.data.AUTOTUNE

dataframe = pd.read_csv(f"{PATH}/train.csv")
dataframe["image_path"] = f"{PATH}/train_images" + "/" + dataframe.patient_id.astype(str) + "/" + dataframe.series_id.astype(str) + "/" + dataframe.instance_number.astype(str) +".png"
dataframe = dataframe.drop_duplicates()

dataframe.tail(10)

dataframe.head(10)

dataframe.groupby('bowel_injury').first()

dataframe.groupby( TARGET_COLS).first()

for key, group in dataframe.groupby(TARGET_COLS):
    print (group ) ;
    break ;

train_data = pd.DataFrame()
val_data = pd.DataFrame()


for key, group in dataframe.groupby(TARGET_COLS):
    test_size = 0.2
    if len(group) == 1:
        train_group, val_group = (group, pd.DataFrame()) if np.random.rand() < test_size else (pd.DataFrame(), group)
    else:
        train_group, val_group = train_test_split(group, test_size=test_size, random_state=42)
    train_data = pd.concat([train_data, train_group], ignore_index=True)
    val_data = pd.concat([val_data, val_group], ignore_index=True)

train_data = train_data.drop_duplicates()
val_data = val_data.drop_duplicates()

def decode_image_and_label(image_path, label):
    file_bytes = tf.io.read_file(image_path)
    image = tf.io.decode_png(file_bytes, channels=3, dtype=tf.uint8)
    image = tf.image.resize(image, IMAGE_SIZE, method="bilinear")
    image = tf.cast(image, tf.float32) / 255.0

    label = tf.cast(label, tf.float32)
    #         bowel       fluid       kidney      liver       spleen
    labels = (label[0:1], label[1:2], label[2:5], label[5:8], label[8:11])

    return (image, labels)


def build_dataset(image_paths, labels):
    ds = (
        tf.data.Dataset.from_tensor_slices((image_paths, labels))
        .map(decode_image_and_label, num_parallel_calls=AUTOTUNE)
        .shuffle(BATCH_SIZE * 10)
        .batch(BATCH_SIZE)
        .prefetch(AUTOTUNE)
    )
    return ds


def augment_dataset(ds):
    augmenter = keras_cv.layers.Augmenter(
        [
            keras_cv.layers.RandomFlip(mode="horizontal_and_vertical"),
            keras_cv.layers.RandomCutout(height_factor=0.2, width_factor=0.2),
        ]
    )

    def apply_augmentation(images, labels):
        return (augmenter(images), labels)

    ds = ds.map(apply_augmentation, num_parallel_calls=AUTOTUNE)
    return ds


paths = train_data.image_path.tolist()
labels = train_data[TARGET_COLS].values

# Build the dataset first
ds = build_dataset(image_paths=paths, labels=labels)

# Then augment the dataset
ds = augment_dataset(ds)

# Now you can iterate through the dataset and access images and labels
images, labels = next(iter(ds))
images.shape, [label.shape for label in labels]

import matplotlib.pyplot as plt
import numpy as np

# Assuming 'images' is a NumPy array containing your images

# Define the number of rows and columns for the gallery
rows = 4
cols = 4

# Create a figure and a set of subplots
fig, axes = plt.subplots(rows, cols, figsize=(8, 8))

# Flatten axes to iterate through them
axes = axes.flatten()

# Iterate through images and plot them
for i in range(rows * cols):
    if i < len(images):
        ax = axes[i]
        ax.imshow(images[i], cmap='gray')  # You may need to specify a colormap based on your image data
        ax.axis('off')  # Turn off axis labels and ticks

# Adjust spacing between subplots
plt.tight_layout()

# Display the gallery
plt.show()

# get image_paths and labels
print("[INFO] Building the dataset...")
train_paths = train_data.image_path.values;
train_labels = train_data[TARGET_COLS].values.astype(np.float32)

valid_paths = val_data.image_path.values;
valid_labels = val_data[TARGET_COLS].values.astype(np.float32)

# train and valid dataset
train_ds = build_dataset(image_paths=train_paths, labels=train_labels)
val_ds = build_dataset(image_paths=valid_paths, labels=valid_labels)

total_train_steps = train_ds.cardinality().numpy() * BATCH_SIZE * EPOCHS
warmup_steps = int(total_train_steps * 0.10)
decay_steps = total_train_steps - warmup_steps

print(f"{total_train_steps=}")
print(f"{warmup_steps=}")
print(f"{decay_steps=}")

# def build_model(warmup_steps, decay_steps):
#     # Define Input
#     inputs = keras.Input(shape=(IMAGE_SIZE[0], IMAGE_SIZE[1], 3), batch_size=BATCH_SIZE)

#     # Define Backbone
#     backbone = keras_cv.models.ResNetBackbone.from_preset("resnet50_imagenet")
#     backbone.trainable = False
#     backbone.include_rescaling = False
#     x = backbone(inputs)

#     # GAP to get the activation maps
#     gap = keras.layers.GlobalAveragePooling2D()
#     x = gap(x)

#     # Define 'necks' for each head
#     x_bowel = keras.layers.Dense(32, activation='silu')(x)
#     x_extra = keras.layers.Dense(32, activation='silu')(x)
#     x_liver = keras.layers.Dense(32, activation='silu')(x)
#     x_kidney = keras.layers.Dense(32, activation='silu')(x)
#     x_spleen = keras.layers.Dense(32, activation='silu')(x)

#     # Define heads
#     out_bowel = keras.layers.Dense(1, name='bowel', activation='sigmoid')(x_bowel) # use sigmoid to convert predictions to [0-1]
#     out_extra = keras.layers.Dense(1, name='extra', activation='sigmoid')(x_extra) # use sigmoid to convert predictions to [0-1]
#     out_liver = keras.layers.Dense(3, name='liver', activation='softmax')(x_liver) # use softmax for the liver head
#     out_kidney = keras.layers.Dense(3, name='kidney', activation='softmax')(x_kidney) # use softmax for the kidney head
#     out_spleen = keras.layers.Dense(3, name='spleen', activation='softmax')(x_spleen) # use softmax for the spleen head

#     # Concatenate the outputs
#     outputs = [out_bowel, out_extra, out_liver, out_kidney, out_spleen]

#     # Create model
#     print("[INFO] Building the model...")
#     model = keras.Model(inputs=inputs, outputs=outputs)

#     # Cosine Decay
#     cosine_decay = keras.optimizers.schedules.CosineDecay(
#         initial_learning_rate=1e-4,
#         decay_steps=decay_steps,
#         alpha=0.0,
#         warmup_target=1e-3,
#         warmup_steps=warmup_steps,
#     )

#     # Compile the model
#     optimizer = keras.optimizers.Adam(learning_rate=cosine_decay)
#     loss = {
#         "bowel":keras.losses.BinaryCrossentropy(),
#         "extra":keras.losses.BinaryCrossentropy(),
#         "liver":keras.losses.CategoricalCrossentropy(),
#         "kidney":keras.losses.CategoricalCrossentropy(),
#         "spleen":keras.losses.CategoricalCrossentropy(),
#     }
#     metrics = {
#         "bowel":["accuracy"],
#         "extra":["accuracy"],
#         "liver":["accuracy"],
#         "kidney":["accuracy"],
#         "spleen":["accuracy"],
#     }
#     print("[INFO] Compiling the model...")
#     model.compile(
#         optimizer=optimizer,
#       loss=loss,
#       metrics=metrics
#     )

#     return model

"""# RESNET MODEL"""

# better resnet model

import tensorflow as tf
from tensorflow import keras

def build_model(warmup_steps, decay_steps):
    # Define Input
    inputs = keras.Input(shape=(IMAGE_SIZE[0], IMAGE_SIZE[1], 3), batch_size=BATCH_SIZE)

    # Define Backbone (You can replace this with any other backbone)
    backbone = keras.applications.ResNet50(include_top=False, weights='imagenet', input_tensor=inputs, input_shape=(IMAGE_SIZE[0], IMAGE_SIZE[1], 3))
    backbone.trainable = False
    x = backbone(inputs, training=False )

    # GAP to get the activation maps
    gap = keras.layers.GlobalAveragePooling2D()
    x = gap(x)

    # Define 'necks' for each head
    x_bowel = keras.layers.Dense(32, activation='selu')(x)
    x_extra = keras.layers.Dense(32, activation='selu')(x)
    x_liver = keras.layers.Dense(32, activation='selu')(x)
    x_kidney = keras.layers.Dense(32, activation='selu')(x)
    x_spleen = keras.layers.Dense(32, activation='selu')(x)

    # Define heads
    out_bowel = keras.layers.Dense(1, name='bowel', activation='sigmoid')(x_bowel)
    out_extra = keras.layers.Dense(1, name='extra', activation='sigmoid')(x_extra)
    out_liver = keras.layers.Dense(3, name='liver', activation='softmax')(x_liver)
    out_kidney = keras.layers.Dense(3, name='kidney', activation='softmax')(x_kidney)
    out_spleen = keras.layers.Dense(3, name='spleen', activation='softmax')(x_spleen)

    # Concatenate the outputs
    outputs = [out_bowel, out_extra, out_liver, out_kidney, out_spleen]

    # Create model
    print("[INFO] Building the model...")
    model = keras.Model(inputs=inputs, outputs=outputs)

    # Cosine Decay
    cosine_decay = keras.optimizers.schedules.CosineDecay(
        initial_learning_rate=1e-4,
        decay_steps=decay_steps,
        alpha=0.0,
        warmup_target=1e-3,
        warmup_steps=warmup_steps,
    )

    # Compile the model
    optimizer = keras.optimizers.Adam(learning_rate=cosine_decay)
    loss = {
        "bowel": keras.losses.BinaryCrossentropy(),
        "extra": keras.losses.BinaryCrossentropy(),
        "liver": keras.losses.CategoricalCrossentropy(),
        "kidney": keras.losses.CategoricalCrossentropy(),
        "spleen": keras.losses.CategoricalCrossentropy(),
    }
    metrics = {
        "bowel": ["accuracy"],
        "extra": ["accuracy"],
        "liver": ["accuracy"],
        "kidney": ["accuracy"],
        "spleen": ["accuracy"],
    }
    print("[INFO] Compiling the model...")
    model.compile(
        optimizer=optimizer,
        loss=loss,
        metrics=metrics
    )

    return model

# build the model
print("[INFO] Building the model...")
model = build_model(warmup_steps, decay_steps)
model.summary()

# train
print("[INFO] Training...")
# history = model.fit(
#     train_ds,
#     epochs=EPOCHS,
#     validation_data=val_ds,
# )

from keras.utils import plot_model
plot_model(model , to_file= 'modelplot.png' , show_shapes= 'True' , show_layer_names = True )

# Create a 3x2 grid for the subplots
fig, axes = plt.subplots(5, 1, figsize=(5, 15))

# Flatten axes to iterate through them
axes = axes.flatten()

# Iterate through the metrics and plot them
for i, name in enumerate(["bowel", "extra", "kidney", "liver", "spleen"]):
    # Plot training accuracy
    axes[i].plot(history.history[name + '_accuracy'], label='Training ' + name)
    # Plot validation accuracy
    axes[i].plot(history.history['val_' + name + '_accuracy'], label='Validation ' + name)
    axes[i].set_title(name)
    axes[i].set_xlabel('Epoch')
    axes[i].set_ylabel('Accuracy')
    axes[i].legend()

plt.tight_layout()
plt.show()

plt.plot(history.history["loss"], label="loss")
plt.plot(history.history["val_loss"], label="val loss")
plt.legend()
plt.show()

# store best results
best_epoch = np.argmin(history.history['val_loss'])
best_loss = history.history['val_loss'][best_epoch]
best_acc_bowel = history.history['val_bowel_accuracy'][best_epoch]
best_acc_extra = history.history['val_extra_accuracy'][best_epoch]
best_acc_liver = history.history['val_liver_accuracy'][best_epoch]
best_acc_kidney = history.history['val_kidney_accuracy'][best_epoch]
best_acc_spleen = history.history['val_spleen_accuracy'][best_epoch]

# Find mean accuracy
best_acc = np.mean(
    [best_acc_bowel,
     best_acc_extra,
     best_acc_liver,
     best_acc_kidney,
     best_acc_spleen
])


print(f'>>>> BEST Loss  : {best_loss:.3f}\n>>>> BEST Acc   : {best_acc:.3f}\n>>>> BEST Epoch : {best_epoch}\n')
print('ORGAN Acc:')
print(f'  >>>> {"Bowel".ljust(15)} : {best_acc_bowel:.3f}')
print(f'  >>>> {"Extravasation".ljust(15)} : {best_acc_extra:.3f}')
print(f'  >>>> {"Liver".ljust(15)} : {best_acc_liver:.3f}')
print(f'  >>>> {"Kidney".ljust(15)} : {best_acc_kidney:.3f}')
print(f'  >>>> {"Spleen".ljust(15)} : {best_acc_spleen:.3f}')

# Save the model
model.save(PATH+"/resnet.keras")

"""# EFFICIENTNET MODEL"""

! pip install -q efficientnet

from efficientnet.tfkeras import EfficientNetB0  # variant (B0, B1, B2, etc.)


def build_model(warmup_steps, decay_steps):
    # Define Input
    inputs = keras.Input(shape=(IMAGE_SIZE[0], IMAGE_SIZE[1], 3), batch_size=BATCH_SIZE)

    # Define EfficientNet as the backbone
    base_model = EfficientNetB0(input_shape=(IMAGE_SIZE[0], IMAGE_SIZE[1], 3), include_top=False, weights='imagenet')
    x = base_model(inputs)

    # GAP to get the activation maps
    gap = keras.layers.GlobalAveragePooling2D()
    x = gap(x)

    # Define 'necks' for each head
    x_bowel = keras.layers.Dense(32, activation='selu')(x)
    x_extra = keras.layers.Dense(32, activation='selu')(x)
    x_liver = keras.layers.Dense(32, activation='selu')(x)
    x_kidney = keras.layers.Dense(32, activation='selu')(x)
    x_spleen = keras.layers.Dense(32, activation='selu')(x)

    # Define heads
    out_bowel = keras.layers.Dense(1, name='bowel', activation='sigmoid')(x_bowel)
    out_extra = keras.layers.Dense(1, name='extra', activation='sigmoid')(x_extra)
    out_liver = keras.layers.Dense(3, name='liver', activation='softmax')(x_liver)
    out_kidney = keras.layers.Dense(3, name='kidney', activation='softmax')(x_kidney)
    out_spleen = keras.layers.Dense(3, name='spleen', activation='softmax')(x_spleen)

    # Concatenate the outputs
    outputs = [out_bowel, out_extra, out_liver, out_kidney, out_spleen]

    # Create model
    print("[INFO] Building the model...")
    model = keras.Model(inputs=inputs, outputs=outputs)

    # Cosine Decay
    cosine_decay = keras.optimizers.schedules.CosineDecay(
        initial_learning_rate=1e-4,
        decay_steps=decay_steps,
        alpha=0.0,
        warmup_target=1e-3,
        warmup_steps=warmup_steps,
    )

    # Compile the model
    optimizer = keras.optimizers.Adam(learning_rate=cosine_decay)
    loss = {
        "bowel": keras.losses.BinaryCrossentropy(),
        "extra": keras.losses.BinaryCrossentropy(),
        "liver": keras.losses.CategoricalCrossentropy(),
        "kidney": keras.losses.CategoricalCrossentropy(),
        "spleen": keras.losses.CategoricalCrossentropy(),
    }
    metrics = {
        "bowel": ["accuracy"],
        "extra": ["accuracy"],
        "liver": ["accuracy"],
        "kidney": ["accuracy"],
        "spleen": ["accuracy"],
    }
    print("[INFO] Compiling the model...")
    model.compile(
        optimizer=optimizer,
        loss=loss,
        metrics=metrics
    )

    return model

# build the model
print("[INFO] Building the model...")
model = build_model(warmup_steps, decay_steps)
model.summary()

# train
print("[INFO] Training...")
# history = model.fit(
#     train_ds,
#     epochs=EPOCHS,
#     validation_data=val_ds,
# )

from keras.utils import plot_model
plot_model(model , to_file= 'modelplot.png' , show_shapes= 'True' , show_layer_names = True )

# Create a 3x2 grid for the subplots
fig, axes = plt.subplots(5, 1, figsize=(5, 15))

# Flatten axes to iterate through them
axes = axes.flatten()

# Iterate through the metrics and plot them
for i, name in enumerate(["bowel", "extra", "kidney", "liver", "spleen"]):
    # Plot training accuracy
    axes[i].plot(history.history[name + '_accuracy'], label='Training ' + name)
    # Plot validation accuracy
    axes[i].plot(history.history['val_' + name + '_accuracy'], label='Validation ' + name)
    axes[i].set_title(name)
    axes[i].set_xlabel('Epoch')
    axes[i].set_ylabel('Accuracy')
    axes[i].legend()

plt.tight_layout()
plt.show()

plt.plot(history.history["loss"], label="loss")
plt.plot(history.history["val_loss"], label="val loss")
plt.legend()
plt.show()

# store best results
best_epoch = np.argmin(history.history['val_loss'])
best_loss = history.history['val_loss'][best_epoch]
best_acc_bowel = history.history['val_bowel_accuracy'][best_epoch]
best_acc_extra = history.history['val_extra_accuracy'][best_epoch]
best_acc_liver = history.history['val_liver_accuracy'][best_epoch]
best_acc_kidney = history.history['val_kidney_accuracy'][best_epoch]
best_acc_spleen = history.history['val_spleen_accuracy'][best_epoch]

# Find mean accuracy
best_acc = np.mean(
    [best_acc_bowel,
     best_acc_extra,
     best_acc_liver,
     best_acc_kidney,
     best_acc_spleen
])


print(f'>>>> BEST Loss  : {best_loss:.3f}\n>>>> BEST Acc   : {best_acc:.3f}\n>>>> BEST Epoch : {best_epoch}\n')
print('ORGAN Acc:')
print(f'  >>>> {"Bowel".ljust(15)} : {best_acc_bowel:.3f}')
print(f'  >>>> {"Extravasation".ljust(15)} : {best_acc_extra:.3f}')
print(f'  >>>> {"Liver".ljust(15)} : {best_acc_liver:.3f}')
print(f'  >>>> {"Kidney".ljust(15)} : {best_acc_kidney:.3f}')
print(f'  >>>> {"Spleen".ljust(15)} : {best_acc_spleen:.3f}')

# Save the model
model.save(PATH+"/efficientnet.keras")

"""# VGG 16 MODEL"""

def build_model(warmup_steps, decay_steps):
    # Define Input
    inputs = keras.Input(shape=(IMAGE_SIZE[0], IMAGE_SIZE[1], 3), batch_size=BATCH_SIZE)

    # Define Backbone (Use VGG16)
    backbone = keras.applications.VGG16(weights='imagenet', include_top=False, input_tensor=inputs, input_shape=(IMAGE_SIZE[0], IMAGE_SIZE[1], 3))
    backbone.trainable = False
    x = backbone(inputs, training=False)

    # GAP to get the activation maps
    gap = keras.layers.GlobalAveragePooling2D()
    x = gap(x)

    # Define 'necks' for each head
    x_bowel = keras.layers.Dense(32, activation='selu')(x)
    x_extra = keras.layers.Dense(32, activation='selu')(x)
    x_liver = keras.layers.Dense(32, activation='selu')(x)
    x_kidney = keras.layers.Dense(32, activation='selu')(x)
    x_spleen = keras.layers.Dense(32, activation='selu')(x)

    # Define heads
    out_bowel = keras.layers.Dense(1, name='bowel', activation='sigmoid')(x_bowel)
    out_extra = keras.layers.Dense(1, name='extra', activation='sigmoid')(x_extra)
    out_liver = keras.layers.Dense(3, name='liver', activation='softmax')(x_liver)
    out_kidney = keras.layers.Dense(3, name='kidney', activation='softmax')(x_kidney)
    out_spleen = keras.layers.Dense(3, name='spleen', activation='softmax')(x_spleen)

    # Concatenate the outputs
    outputs = [out_bowel, out_extra, out_liver, out_kidney, out_spleen]

    # Create the model
    print("[INFO] Building the model...")
    model = keras.Model(inputs=inputs, outputs=outputs)

    # Cosine Decay
    cosine_decay = keras.optimizers.schedules.CosineDecay(
        initial_learning_rate=1e-4,
        decay_steps=decay_steps,
        alpha=0.0,
        warmup_target=1e-3,
        warmup_steps=warmup_steps,
    )

    # Compile the model
    optimizer = keras.optimizers.Adam(learning_rate=cosine_decay)
    loss = {
        "bowel": keras.losses.BinaryCrossentropy(),
        "extra": keras.losses.BinaryCrossentropy(),
        "liver": keras.losses.CategoricalCrossentropy(),
        "kidney": keras.losses.CategoricalCrossentropy(),
        "spleen": keras.losses.CategoricalCrossentropy(),
    }
    metrics = {
        "bowel": ["accuracy"],
        "extra": ["accuracy"],
        "liver": ["accuracy"],
        "kidney": ["accuracy"],
        "spleen": ["accuracy"],
    }
    print("[INFO] Compiling the model...")
    model.compile(
        optimizer=optimizer,
        loss=loss,
        metrics=metrics
    )

    return model

# build the model
print("[INFO] Building the model...")
model = build_model(warmup_steps, decay_steps)
model.summary()

# train
print("[INFO] Training...")
# history = model.fit(
#     train_ds,
#     epochs=EPOCHS,
#     validation_data=val_ds,
# )

from keras.utils import plot_model
plot_model(model , to_file= 'modelplot.png' , show_shapes= 'True' , show_layer_names = True )

# Create a 3x2 grid for the subplots
fig, axes = plt.subplots(5, 1, figsize=(5, 15))

# Flatten axes to iterate through them
axes = axes.flatten()

# Iterate through the metrics and plot them
for i, name in enumerate(["bowel", "extra", "kidney", "liver", "spleen"]):
    # Plot training accuracy
    axes[i].plot(history.history[name + '_accuracy'], label='Training ' + name)
    # Plot validation accuracy
    axes[i].plot(history.history['val_' + name + '_accuracy'], label='Validation ' + name)
    axes[i].set_title(name)
    axes[i].set_xlabel('Epoch')
    axes[i].set_ylabel('Accuracy')
    axes[i].legend()

plt.tight_layout()
plt.show()

plt.plot(history.history["loss"], label="loss")
plt.plot(history.history["val_loss"], label="val loss")
plt.legend()
plt.show()

# store best results
best_epoch = np.argmin(history.history['val_loss'])
best_loss = history.history['val_loss'][best_epoch]
best_acc_bowel = history.history['val_bowel_accuracy'][best_epoch]
best_acc_extra = history.history['val_extra_accuracy'][best_epoch]
best_acc_liver = history.history['val_liver_accuracy'][best_epoch]
best_acc_kidney = history.history['val_kidney_accuracy'][best_epoch]
best_acc_spleen = history.history['val_spleen_accuracy'][best_epoch]

# Find mean accuracy
best_acc = np.mean(
    [best_acc_bowel,
     best_acc_extra,
     best_acc_liver,
     best_acc_kidney,
     best_acc_spleen
])


print(f'>>>> BEST Loss  : {best_loss:.3f}\n>>>> BEST Acc   : {best_acc:.3f}\n>>>> BEST Epoch : {best_epoch}\n')
print('ORGAN Acc:')
print(f'  >>>> {"Bowel".ljust(15)} : {best_acc_bowel:.3f}')
print(f'  >>>> {"Extravasation".ljust(15)} : {best_acc_extra:.3f}')
print(f'  >>>> {"Liver".ljust(15)} : {best_acc_liver:.3f}')
print(f'  >>>> {"Kidney".ljust(15)} : {best_acc_kidney:.3f}')
print(f'  >>>> {"Spleen".ljust(15)} : {best_acc_spleen:.3f}')

# Save the model
model.save(PATH+"/vgg16.keras")












