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

class LinearBlock(Module):
    def __init__(self, in_features, out_features):
        pass

class RecognitionModel(Module):
    def __init__(self):
        super().__init__()
        
        # Input 1x80x180
        self.block1 = CNNBlock(1, 16) # Block1 16x40x90
        self.block2 = CNNBlock(16, 32) # Block2 32x20x45
        self.block3 = CNNBlock(32, 32) # Block3 32x10x22
        self.block4 = CNNBlock(32, 64) # Block4 200x10x22
        self.gmp = AdaptiveMaxPool2d(output_size = 1) # GlobalMaxPool 64x1x1
        self.rshp = lambda x: x.reshape(-1, 64) # Reshape 64
        self.linear1 = Linear(
            in_features = 64,
            out_features = 64
        )
        self.batchnorm = BatchNorm1d(num_features = 64)
        self.act1 = LeakyReLU()
        self.dropout = Dropout(0)
        self.linear2 = Linear(
            in_features = 64,
            out_features = 36
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
    
    def save(self):
        torch.save(self.state_dict(), './trainedmodel.pt')

    def load(self):
        self.load_state_dict(torch.load('./trainedmodel.pt', weights_only = True))

if __name__ == "__main__":
    print(RecognitionModel())