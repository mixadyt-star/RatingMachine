import json
import torch
from torch.utils.data import Dataset
from PIL import Image

class CellsDataset(Dataset):
    def __init__(self, transform):
        self.classes = "123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ "
        self.transform = transform

        with open("dataset/labels.json", 'r') as labels:
            self.labels = json.load(labels)

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, index: int):
        image_path = "dataset/images/" + self.labels[index]["image"]
        
        label = self.labels[index]["choice"]
        label_index = self.classes.index(label.upper())
        label_hot_encoding = torch.zeros(len(self.classes))
        label_hot_encoding[label_index] = 1

        image = Image.open(image_path)
        return self.transform(image) / 255, label_hot_encoding