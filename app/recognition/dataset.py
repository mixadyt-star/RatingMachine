import PIL.Image
import cv2
import PIL
from torch.utils.data import Dataset
from torchvision import transforms 

default_transform = transforms.Compose([
    transforms.Resize((80, 180)),
    transforms.Grayscale(),
    transforms.ToTensor(),
])

class CellsDataset(Dataset):
    def __init__(self, transform, images):
        super().__init__()
        self.classes = "123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        self.transform = transform
        self.images = images

    def __len__(self):
        return len(self.images)

    def __getitem__(self, index: int):
        image = PIL.Image.fromarray(cv2.cvtColor(self.images[index], cv2.COLOR_BGR2RGB))
        return self.transform(image) / 255