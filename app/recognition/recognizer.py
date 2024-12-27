import numpy as np
import torch
import cv2
from torch.utils.data import DataLoader
from cv2.typing import MatLike

from recognition.dataset import CellsDataset, default_transform
from recognition.model import RecognitionModel
from recognition import preprocess

model = RecognitionModel()
model.load("./recognition/trainedmodel.pt")
model.eval()

def recognize(image: MatLike):
    table_contour = preprocess.find_table(image)
    table_image = preprocess.crop_table(image, table_contour)
    cell_contours = preprocess.find_cells(table_image)
    cell_images = preprocess.crop_cells(table_image, cell_contours)

    dataset = CellsDataset(transform = default_transform, images = cell_images)
    dataloader = DataLoader(dataset, batch_size = len(cell_images), shuffle = False)

    with torch.no_grad():
        images = next(iter(dataloader))
        predictions = model(images)
        labels_index = torch.argmax(predictions, dim = 1)
        labels = [dataset.classes[ind.item()] for ind in labels_index]
    
    
    # import matplotlib.pyplot as plt
    # plt.figure(figsize=(12, 12))
    # for i in range(52):
    #     plt.subplot(13, 4, i + 1)  # 8 строк и 4 колонки
    #     plt.imshow(images[i].reshape(80, 180, 1), cmap="gray")  # показываем изображение
    #     plt.title(f'Pred: {labels[i]}')  # отображаем предсказание
    #     plt.axis('off')  # отключаем оси

    # plt.tight_layout()
    # plt.show()


    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    answers = {}

    for i in range(len(cell_contours)):
        min_distance = np.inf
        for j in range(len(cell_contours)):
            if j == i or not(labels[i] in letters) or labels[j] in letters:
                continue

            rect1 = cv2.boundingRect(cell_contours[i])
            rect2 = cv2.boundingRect(cell_contours[j])
            
            distance = abs(rect1[0] - rect2[0]) + abs(rect1[1] + rect1[3] - rect2[1])
            if distance < min_distance:
                min_distance = distance
                answers[labels[i]] = labels[j]

    print(answers)