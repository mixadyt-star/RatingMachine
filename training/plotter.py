from torch.utils.data import DataLoader, random_split
import matplotlib.pyplot as plt
from torchvision import transforms
import numpy as np

from dataset.dataset import CellsDataset
from model import RecognitionModel

def set_seed(seed: int = 42) -> None:
    import numpy as np
    import random
    import torch
    import os

    np.random.seed(seed)
    random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    # When running on the CuDNN backend, two further options must be set
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    # Set a fixed value for the hash seed
    os.environ["PYTHONHASHSEED"] = str(seed)
    print(f"Random seed set as {seed}")

model = RecognitionModel()
model.load()
set_seed(512)
transform = transforms.Compose([
    transforms.Resize((80, 180)),
    transforms.Grayscale(),
    transforms.ToTensor(),
])

dataset = CellsDataset(transform)

train_dataset, valid_dataset = random_split(dataset, [0.8, 0.2])
train_dataloader = DataLoader(train_dataset, batch_size = 32, shuffle = True)
valid_dataloader = DataLoader(valid_dataset, batch_size = 32, shuffle = True)

images, labels = next(iter(valid_dataloader))

model.eval()
pred = model(images)
plt.figure(figsize=(12, 12))
for i in range(32):
    plt.subplot(8, 4, i + 1)  # 8 строк и 4 колонки
    plt.imshow(images[i].reshape(80, 180, 1), cmap="gray")  # показываем изображение
    plt.title(f'Pred: {dataset.classes[np.argmax(pred[i].detach().numpy())]}')  # отображаем предсказание
    plt.axis('off')  # отключаем оси

plt.tight_layout()
plt.show()