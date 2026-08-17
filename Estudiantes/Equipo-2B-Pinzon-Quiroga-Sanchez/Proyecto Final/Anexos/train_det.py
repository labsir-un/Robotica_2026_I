from ultralytics import YOLO
import torch

torch.cuda.empty_cache()

torch.backends.cudnn.benchmark = False
torch.backends.cudnn.deterministic = True

def main():

    # Modelo preentrenado de detección
    #model = YOLO(r"C:\Users\david\Desktop\ROBOTICA\Proyecto\YOLO\runs\detect\runs\Detector_Componentes-7\weights\best.pt")
    model = YOLO(r"C:\Users\david\Desktop\ROBOTICA\Proyecto\YOLO\runs\detect\runs\Detector_Componentes_Nuevo\weights\best.pt")

    model.train(

        data="Dataset_prefinal/data.yaml",
        epochs=50,
        imgsz=640,
        batch=8,
        device=0,
        workers=0,
        amp=True,
        pretrained=True,
        cache=False,
        project="runs",
        name="Detector_prefinal"
    )

if __name__ == "__main__":
    main()