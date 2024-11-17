import os
import cv2
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from tensorflow.keras.layers import *
from tensorflow.keras.models import Sequential
from keras.applications.mobilenet_v2 import MobileNetV2
from tensorflow.keras.utils import to_categorical, plot_model
from tensorflow.keras.callbacks import EarlyStopping

IMAGE_HEIGHT, IMAGE_WIDTH = 64, 64
SEQUENCE_LENGTH = 16
DATASET_DIR = "./dataset"
CLASSES_LIST = ["NonViolence", "Violence"]


def frames_extraction(video_path):
    frames_list = []
    video_reader = cv2.VideoCapture(video_path)
    video_frames_count = int(video_reader.get(cv2.CAP_PROP_FRAME_COUNT))
    skip_frames_window = max(1, video_frames_count // SEQUENCE_LENGTH)

    for frame_counter in range(SEQUENCE_LENGTH):
        video_reader.set(cv2.CAP_PROP_POS_FRAMES, frame_counter * skip_frames_window)
        success, frame = video_reader.read()
        if not success:
            break
        frame = cv2.resize(frame, (IMAGE_HEIGHT, IMAGE_WIDTH))
        frame = frame / 255.0
        frames_list.append(frame)

    video_reader.release()
    return frames_list


def create_model():
    mobilenet = MobileNetV2(include_top=False, weights="imagenet")
    mobilenet.trainable = True

    for layer in mobilenet.layers[:-40]:
        layer.trainable = False

    model = Sequential()

    model.add(Input(shape=(SEQUENCE_LENGTH, IMAGE_HEIGHT, IMAGE_WIDTH, 3)))

    model.add(TimeDistributed(mobilenet))
    model.add(Dropout(0.25))
    model.add(TimeDistributed(Flatten()))

    lstm_fw = LSTM(units=32)
    lstm_bw = LSTM(units=32, go_backwards=True)

    model.add(Bidirectional(lstm_fw, backward_layer=lstm_bw))
    model.add(Dropout(0.25))
    model.add(Dense(256, activation='relu'))
    model.add(Dropout(0.25))
    model.add(Dense(128, activation='relu'))
    model.add(Dropout(0.25))
    model.add(Dense(64, activation='relu'))
    model.add(Dropout(0.25))
    model.add(Dense(32, activation='relu'))
    model.add(Dropout(0.25))

    model.add(Dense(len(CLASSES_LIST), activation='softmax'))

    model.compile(loss='categorical_crossentropy', optimizer='sgd', metrics=["accuracy"])
    return model


def plot_metric(model_training_history, metric_name_1, metric_name_2, plot_name, file_name):
    metric_value_1 = model_training_history.history[metric_name_1]
    metric_value_2 = model_training_history.history[metric_name_2]

    epochs = range(len(metric_value_1))
    plt.plot(epochs, metric_value_1, 'blue', label=metric_name_1)
    plt.plot(epochs, metric_value_2, 'orange', label=metric_name_2)
    plt.title(str(plot_name))
    plt.legend()

    plt.savefig(file_name)


def build_model():
    model = create_model()
    model.summary()

    features, labels = [], []
    for class_index, class_name in enumerate(CLASSES_LIST):
        class_dir = os.path.join(DATASET_DIR, class_name)
        for file_name in os.listdir(class_dir):
            video_path = os.path.join(class_dir, file_name)
            frames = frames_extraction(video_path)
            if len(frames) == SEQUENCE_LENGTH:
                features.append(frames)
                labels.append(class_index)

    features = np.array(features)
    labels = np.array(labels)

    one_hot_encoded_labels = to_categorical(labels)

    features_train, features_test, labels_train, labels_test = train_test_split(
        features,
        one_hot_encoded_labels,
        test_size=0.1,
        shuffle=True,
        random_state=42)

    early_stopping_callback = EarlyStopping(
        monitor='val_accuracy',
        patience=10,
        restore_best_weights=True)

    reduce_lr = tf.keras.callbacks.ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.6,
        patience=5,
        min_lr=0.00005,
        verbose=1)

    model.compile(loss='categorical_crossentropy', optimizer='sgd', metrics=["accuracy"])

    MobBiLSTM_model_history = model.fit(
        x=features_train,
        y=labels_train,
        epochs=50,
        batch_size=8,
        shuffle=True,
        validation_split=0.2,
        callbacks=[early_stopping_callback, reduce_lr])

    # model.fit(features, labels, epochs=50, validation_split=0.2, batch_size=8, shuffle=True)

    model.save('violence_detection_model.keras')

    model_evaluation_history = model.evaluate(features_test, labels_test)

    plot_metric(MobBiLSTM_model_history, 'loss', 'val_loss', 'Total Loss vs Total Validation Loss',
                'total_loss_vs_val_loss.png')
    plot_metric(MobBiLSTM_model_history, 'accuracy', 'val_accuracy', 'Accuracy vs Validation Accuracy',
                'accuracy_vs_val_accuracy.png')
