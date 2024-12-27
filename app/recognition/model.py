import torch
from torch.nn import Module, Conv2d, MaxPool2d, ReLU, BatchNorm2d, BatchNorm1d, Linear, LeakyReLU, Softmax, AdaptiveMaxPool2d, Dropout

class CNNBlock(Module):
    def __init__(self, in_channels, out_channels):
        super().__init__()
        self.conv = Conv2d(
            in_channels = in_channels,
            out_channels = out_channels,
            kernel_size = 3,
            padding = "same"
        )
        self.dropout = Dropout(0)
        self.skip = Conv2d(
            in_channels = in_channels,
            out_channels = 1,
            kernel_size = 1,
            padding = "same"
        )
        self.batchnorm = BatchNorm2d(num_features = out_channels)
        self.act = ReLU()
        self.maxpool = MaxPool2d(
            kernel_size = 2,
            stride = 2
        )

    def forward(self, x):
        skip = self.dropout(self.conv(x)) + self.skip(x)
        return self.maxpool(self.act(self.batchnorm(skip)))

class RecognitionModel(Module):
    def __init__(self):
        super().__init__()
        
        # Input 1x80x180
        self.block1 = CNNBlock(1, 32) # Block1 32x40x90
        self.block2 = CNNBlock(32, 64) # Block2 64x20x45
        self.block3 = CNNBlock(64, 128) # Block3 128x10x22
        self.block4 = CNNBlock(128, 200) # Block4 200x10x22
        self.gmp = AdaptiveMaxPool2d(output_size = 1) # GlobalMaxPool 200x1x1
        self.rshp = lambda x: x.reshape(-1, 200) # Reshape 200
        self.linear1 = Linear(
            in_features = 200,
            out_features = 64
        )
        self.batchnorm = BatchNorm1d(num_features = 64)
        self.act1 = LeakyReLU()
        self.dropout = Dropout(0)
        self.linear2 = Linear(
            in_features = 64,
            out_features = 35
        )
        self.act2 = Softmax(dim = 1)

    def forward(self, x):
        x = self.block1(x)
        x = self.block2(x)
        x = self.block3(x)
        x = self.block4(x)
        x = self.gmp(x)
        x = self.rshp(x)
        x = self.dropout(self.act1(self.batchnorm(self.linear1(x))))
        y = self.act2(self.linear2(x))

        return y

    def load(self, model_file: str):
        self.load_state_dict(torch.load(model_file, weights_only = True))

if __name__ == "__main__":
    print(RecognitionModel())