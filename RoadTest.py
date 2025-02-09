import torch
from torchvision import models, transforms
from PIL import Image
import os

DEVICE = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
NUM_CLASSES = 3
MODEL_PATH = 'roadhazard_classifier.pth'
CATEGORIES = ["animal", "cone", "rock"]

data_transforms = transforms.Compose([
    transforms.Resize((720, 1280)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])
def load_model(model_path, num_classes):
    model = models.resnet18()
    num_ftrs = model.fc.in_features
    model.fc = torch.nn.Linear(num_ftrs, num_classes)
    model.load_state_dict(torch.load(model_path, map_location=DEVICE))
    model = model.to(DEVICE)
    model.eval()
    return model
def classify_image(model, image_path):
    image = Image.open(image_path).convert('RGB')
    image = data_transforms(image).unsqueeze(0).to(DEVICE)
    with torch.no_grad():
        outputs = model(image)
        _, predicted = torch.max(outputs, 1)
        probabilities = torch.nn.functional.softmax(outputs[0], dim=0)
    return predicted.item(), probabilities.cpu().numpy()

if __name__ == '__main__':
    model = load_model(MODEL_PATH, NUM_CLASSES)
    TEST_IMAGE_DIR = './photos/test/'
    correct_ans = [0, 2, 2, 2, 2, 1, 1, 1, 1, 0, 0, 0]
    correct_count = 0
    for i, correct_label in enumerate(correct_ans):
        image_path = os.path.join(TEST_IMAGE_DIR, f'image ({i+1}).jpg')
        if not os.path.exists(image_path):
            print(f"Nie mamy {image_path}")
            continue
        predicted_class, probabilities = classify_image(model, image_path)
        print("-" * 50)
        if predicted_class == correct_label:
            print("Poprawne")
        else:
            print("Niepoprawne")
        print(f"Prognozowane: {CATEGORIES[predicted_class]} (mozliwosc: {probabilities[predicted_class]:.4f})")
        print(f"Oczekowane: {CATEGORIES[correct_label]}")

        if predicted_class == correct_label:
            correct_count += 1
    print("-" * 50)
    print(f"Poprawnych: {correct_count} z {len(correct_ans)}")