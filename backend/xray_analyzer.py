import io
import numpy as np
from PIL import Image

import torch
import torchxrayvision as xray

Enfermedades = {
    "Atelectasis": "Atelectasia",
    "Cardiomegaly": "Cardiomegalia",
    "Effusion": "Derrame Pleural",
    "Infiltration": "Infiltración Pulmonar",
    "Mass": "Masa Pulmonar",
    "Nodule": "Nódulo",
    "Pneumonia": "Neumonía",
    "Pneumothorax": "Neumotórax",
    "Consolidation": "Consolidación",
    "Edema": "Edema Pulmonar",
    "Emphysema": "Enfisema",
    "Fibrosis": "Fibrosis Pulmonar",
    "Pleural_Thickening": "Engrosamiento Pleural",
    "Hernia": "Hernia Diafragmática",
}

descripciones = {
    "Atelectasis": {
        "es": "Colapso parcial o total de un pulmón o lóbulo pulmonar.",
        "en": "Partial or complete collapse of a lung or lobe.",
    },
    "Cardiomegaly": {
        "es": "El corazón aparece agrandado en la radiografía.",
        "en": "The heart appears enlarged on the X-ray.",
    },
    "Effusion": {
        "es": "Acumulación de líquido entre el pulmón y la pared torácica.",
        "en": "Fluid buildup between the lung and chest wall.",
    },
    "Infiltration": {
        "es": "Densidad anormal en el tejido pulmonar.",
        "en": "Abnormal density in lung tissue.",
    },
    "Mass": {
        "es": "Lesión sólida mayor de 3 cm en el pulmón.",
        "en": "Solid lesion larger than 3 cm in the lung.",
    },
    "Nodule": {
        "es": "Pequeña mancha redondeada en el pulmón (< 3 cm).",
        "en": "Small rounded spot in the lung (< 3 cm).",
    },
    "Pneumonia": {
        "es": "Infección del tejido pulmonar.",
        "en": "Infection of the lung tissue.",
    },
    "Pneumothorax": {
        "es": "Presencia de aire entre el pulmón y la pared torácica.",
        "en": "Air between the lung and chest wall.",
    },
    "Consolidation": {
        "es": "Los alvéolos se llenan de líquido u otro material.",
        "en": "Alveoli filled with fluid or other material.",
    },
    "Edema": {
        "es": "Exceso de líquido acumulado en el tejido pulmonar.",
        "en": "Excess fluid accumulated in lung tissue.",
    },
    "Emphysema": {
        "es": "Daño en los sacos de aire de los pulmones.",
        "en": "Damage to the air sacs in the lungs.",
    },
    "Fibrosis": {
        "es": "Tejido cicatricial en los pulmones.",
        "en": "Scar tissue in the lungs.",
    },
    "Pleural_Thickening": {
        "es": "Engrosamiento de la membrana que rodea los pulmones.",
        "en": "Thickening of the membrane surrounding the lungs.",
    },
    "Hernia": {
        "es": "Protrusión de un órgano a través del diafragma.",
        "en": "Protrusion of an organ through the diaphragm.",
    },
}


def _severity(confidence: float) -> str:
    if confidence >= 0.60:
        return "Critico"
    if confidence >= 0.35:
        return "Moderado"
    return "low"


class XrayAnalyzer:
    def __init__(self):
        self.model = xray.models.DenseNet(weights="densenet121-res224-all")
        self.model.eval()

    def preprocesamiento(self, image_btyes: bytes) -> torch.Tensor:
        img = Image.open(io.BytesIO(image_btyes)).convert("L")
        array = np.array(img).astype(np.float32)
        array = xray.datasets.normalize(array, 255)

        if array.ndim == 2:
            array = array[np.newaxis, ...]

        array = xray.datasets.XRayCenterCrop()(array)
        array = xray.datasets.XRayResizer(224)(array)

        return torch.from_numpy(array).unsqueeze(0).float()

    def analyze(self, image_bytes: bytes) -> dict:
        tensor = self.preprocesamiento(image_bytes)

        with torch.no_grad():
            raw = self.model(tensor).cpu().numpy()[0]

        etiquetas = []
        for i, label in enumerate(self.model.pathologies):
            if label not in Enfermedades:
                continue
            conf = float(raw[i])
            etiquetas.append(
                {
                    "condition": label,
                    "condition_es": Enfermedades[label],
                    "confidence": round(conf * 100, 1),
                    "confidence_raw": conf,
                    "severity": _severity(conf),
                    "description_es": descripciones[label]["es"],
                    "description_en": descripciones[label]["en"],
                }
            )

        etiquetas.sort(key=lambda x: x["confidence_raw"], reverse=True)

        for f in etiquetas:
            del f["confidence_raw"]

        significant = [f for f in etiquetas if f["confidence"] >= 20]
        normal = all(f["confidence"] < 30 for f in etiquetas)

        return {
            "findings": etiquetas,
            "significant": significant,
            "is_normal": normal,
            "top": etiquetas[0] if etiquetas else None,
            "analysis_complete": True,
        }
