from torch.utils.data import DataLoader, random_split
from torch.nn import CrossEntropyLoss
from torch.optim import Adam
from torchvision import transforms
import matplotlib.pyplot as plt
import numpy as np
import torch
from tqdm import tqdm
from torchmetrics import functional

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

batch_size = 32
epochs = 150
lr = 0.001

set_seed(512)
transform = transforms.Compose([
    transforms.Resize((80, 180)),
    transforms.Grayscale(),
    transforms.ToTensor(),
])

dataset = CellsDataset(transform)

train_dataset, valid_dataset = random_split(dataset, [0.8, 0.2])
train_dataloader = DataLoader(train_dataset, batch_size = batch_size, shuffle = True)
valid_dataloader = DataLoader(valid_dataset, batch_size = batch_size, shuffle = True)

model = RecognitionModel()

loss_func = CrossEntropyLoss()
optimizer = Adam(model.parameters(), lr = lr)

train_losses = []
valid_losses = []
train_accurs = []
valid_accurs = []
# plt.imshow(next(iter(train_dataloader))[0][0].reshape(80, 180, 1), cmap="gray")
# plt.show()
# '''
for epoch in range(epochs):
    total_loss = 0
    total_accuracy_valid = []
    total_accuracy_train = []
    num_batches = 0

    samples = train_dataloader
    bar = tqdm(total = len(samples), desc=f"Epoch {epoch + 1}/{epochs}")

    for image, label in samples:
        # Train
        optimizer.zero_grad()

        pred = model(image)
        total_accuracy_train.append(functional.accuracy(torch.argmax(pred, dim = 1), torch.argmax(label, dim = 1), task = "multiclass", num_classes = 35))
        loss = loss_func(pred, label)
        
        total_loss += loss.item()
        num_batches += 1

        # Backward
        loss.backward()
        optimizer.step()

        bar.set_description(f"Epoch: {epoch + 1}/{epochs} Train loss: {round(total_loss / num_batches, 3)} Train accuracy: {round(np.mean(total_accuracy_train).item(), 2)}")
        bar.update()
    
    train_accurs.append(round(np.mean(total_accuracy_train).item(), 2))
    train_losses.append(total_loss / num_batches)

    # Validation
    model.eval()

    valid_temp = []
    for image, label in valid_dataloader:
        pred = model(image)
        total_accuracy_valid.append(functional.accuracy(torch.argmax(pred, dim = 1), torch.argmax(label, dim = 1), task = "multiclass", num_classes = 35))
        loss_ = loss_func(pred, label)
        valid_temp.append(loss_.item())

    valid_accurs.append(round(np.mean(total_accuracy_valid).item(), 2))
    valid_losses.append(np.mean(valid_temp))
    model.train()

    bar.set_description(f"Epoch: {epoch + 1}/{epochs} Train loss: {round(total_loss / num_batches, 3)} Validation loss: {round(valid_losses[-1], 3)} Train accuracy: {train_accurs[-1]} Validation ccuracy: {valid_accurs[-1]}")
    bar.refresh()

import numpy as np
from torchvision import utils
def visTensor(tensor, ch=0, allkernels=False, nrow=8, padding=1): 
    n,c,w,h = tensor.shape

    if nrow == None:
        nrow = w

    if allkernels: 
        tensor = tensor.view(n*c, -1, w, h)
    elif c != 3: tensor = tensor[:,ch,:,:].unsqueeze(dim=1)

    rows = np.min((tensor.shape[0] // nrow + 1, 64))    
    grid = utils.make_grid(tensor, nrow=nrow, normalize=True, padding=padding)
    plt.figure( figsize=(nrow,rows) )
    plt.imshow(grid.numpy().transpose((1, 2, 0)))
    plt.axis('off')
    plt.ioff()
    plt.show()

filter = model.block1.conv.weight.data.clone()
visTensor(filter, ch=0, allkernels=False)

plt.plot(range(epochs), train_losses)
plt.plot(range(epochs), valid_losses)
plt.show()

plt.plot(range(epochs), train_accurs)
plt.plot(range(epochs), valid_accurs)
plt.show()
model.save()
# '''