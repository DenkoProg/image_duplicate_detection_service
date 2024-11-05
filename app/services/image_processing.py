import io
import requests
from PIL import Image
import torch
from torchvision import models, transforms


class ImageProcessor:
    def __init__(self, device: str = 'cpu'):
        self.device = device
        model = models.resnet50(pretrained=True)
        self.model = torch.nn.Sequential(*list(model.children())[:-1])
        self.model.eval()
        self.model.to(self.device)
        self.transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])

    def preprocess_image(self, image: Image.Image) -> torch.Tensor:
        return self.transform(image).unsqueeze(0).to(self.device)

    def get_embedding(self, image: Image.Image) -> torch.Tensor:
        with torch.no_grad():
            input_tensor = self.preprocess_image(image)
            embedding = self.model(input_tensor)
            embedding = embedding.squeeze().cpu().numpy().tolist()
        return embedding

    @staticmethod
    def load_image_from_url(url: str) -> Image.Image:
        response = requests.get(url)
        response.raise_for_status()
        return Image.open(io.BytesIO(response.content)).convert('RGB')
