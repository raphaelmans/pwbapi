import torch
from torchvision import transforms as T
import torch.nn.functional as F


class AIModel:

    model = None

    def __init__(self):
        self.model = self.load_model()

    def load_model(self):
        run_model_path = './model-weights.pt'
        model = torch.hub.load('ultralytics/yolov5',
                               'custom', path=run_model_path)
        print("🚀 ~ file: ai_model.py:17 ~ model:", model)

        return model

    def classify(self, image):

        IMAGENET_MEAN = 0.485, 0.456, 0.406
        IMAGENET_STD = 0.229, 0.224, 0.225

        # Remove alpha channel if it exists
        if image.mode != 'RGB':
            image = image.convert('RGB')

        def classify_transforms(size=224):
            return T.Compose([T.ToTensor(), T.Resize(size), T.CenterCrop(size), T.Normalize(IMAGENET_MEAN, IMAGENET_STD)])

        transformations = classify_transforms()
        convert_tensor = transformations(image)
        convert_tensor = convert_tensor.unsqueeze(0)

        output = self.model(convert_tensor)
        return output

    def evaluate(self, result) -> dict:
        pred = F.softmax(result, dim=1)

        for i, prob in enumerate(pred):
            top5i = prob.argsort(0, descending=True)[:1].tolist()
            test_res = top5i[0]
            label = self.model.names[test_res]
            prob_result = prob[test_res]
            eval_result = {
                "label": label,
                "probability": prob_result.item()
            }
            return eval_result
