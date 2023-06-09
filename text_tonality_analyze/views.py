import numpy as np
import os

from django.conf import settings
from navec import Navec
from string import punctuation

import torch
import torch.nn as nn
from torch.nn import functional as f

device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')


class MultiLayerPerceptron(nn.Module):

    def __init__(self):
        super(MultiLayerPerceptron, self).__init__()
        self.fc1 = nn.Linear(300, 4096)
        self.fc2 = nn.Linear(4096, 3)

    def forward(self, x):
        x = torch.mean(x, dim=2)
        x = f.leaky_relu(self.fc1(x))
        return f.softmax(self.fc2(x), dim=1)


# load pretrained Model and go straight to evaluation mode for inference
# load as global variable here, to avoid expensive reloads with each request
model_path = os.path.join(settings.STATIC_ROOT, "logreg.pth")

model = MultiLayerPerceptron()
model.load_state_dict(torch.load(model_path))
model.eval()

embeddings_path = os.path.join(settings.STATIC_ROOT,
                               "navec_hudlit_v1_12B_500K_300d_100q.tar")
navec = Navec.load(embeddings_path)


def preprocess_data(sentences: np.ndarray):
    def sentence_split(sentence_, separator):
        for k in range(len(sentence_)):
            a = sentence_[k].split(separator)
            while '' in a:
                a.remove('')
            if a:
                sentence_[k] = a[0].lower()

    embeddings = np.zeros((len(sentences), 100, 300))

    for i in range(len(sentences)):
        sentence = sentences[i].split()
        for sep in punctuation:
            sentence_split(sentence, sep)
        for j in range(len(sentence)):
            if sentence[j] in navec:
                embeddings[i][j] = navec[sentence[j]]
    return embeddings


def get_prediction(sentences: np.ndarray) -> np.ndarray:
    with torch.no_grad():
        probs = model(
            torch.permute(torch.FloatTensor(preprocess_data(sentences)), (0, 2, 1))
        )
    _, pred = torch.max(probs, dim=-1)
    return pred.numpy()
