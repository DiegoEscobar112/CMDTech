import torch
import torch.nn as nn

class SiameseNetwork(nn.Module):
    def __init__(self):
        super(SiameseNetwork, self).__init__()
        self.cnn = nn.Sequential(
            nn.Conv2d(3, 64, kernel_size=10),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2),
            nn.Conv2d(64, 128, kernel_size=7),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2),
            nn.Conv2d(128, 256, kernel_size=5),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2),
            nn.Conv2d(256, 512, kernel_size=3),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2)
        )
        
        # Ajusta el tamaño de entrada en la capa totalmente conectada
        self.fc = nn.Sequential(
            nn.Linear(2048, 4096),  # Cambia 512*5*5 por 2048
            nn.Sigmoid()
        )
    
    def forward_once(self, x):
        output = self.cnn(x)
        output = output.view(output.size()[0], -1)  # Aplana el tensor
        print("Tamaño después de CNN y aplanado:", output.shape)  # Verifica el tamaño
        output = self.fc(output)
        return output
    
    def forward(self, img1, img2):
        output1 = self.forward_once(img1)
        output2 = self.forward_once(img2)
        return output1, output2
