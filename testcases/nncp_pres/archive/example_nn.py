import torch
from torch import nn
from torch.utils.data import DataLoader
from torchvision.datasets import MNIST
from torchvision.transforms import ToTensor

# Load MNIST dataset
mnist = MNIST(root='./data', download=True, transform=ToTensor())
train_loader = DataLoader(mnist, batch_size=32, shuffle=True)

# Define model
class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.fc1 = nn.Linear(28 * 28, 128)
        self.fc2 = nn.Linear(128, 64)
        self.fc3 = nn.Linear(64, 10)

    def forward(self, x):
        x = x.view(-1, 28 * 28)
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        x = self.fc3(x)
        return x

model = Net()

# Define loss and optimizer
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

# Train model
for epoch in range(5):
    for i, (x, y) in enumerate(train_loader):
        y_pred = model(x)
        loss = criterion(y_pred, y)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

# Evaluate model
correct = 0
total = 0
for x, y in train_loader:
    y_pred = model(x)
    _, predicted = torch.max(y_pred.data, 1)
    total += y.size(0)
    correct += (predicted == y).sum().item()

print('Test accuracy:', correct / total)

