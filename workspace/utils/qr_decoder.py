import numpy as np
from pyzbar.pyzbar import decode
from workspace.utils.qr_data import QrData

class QrDecoder:
    
    @classmethod
    def decode(cls, image):
        binary_image = cls.__binarize_image(image)
        decoded_qrs = decode(binary_image)
        return [QrData(decoded_qr) for decoded_qr in decoded_qrs]


    @staticmethod
    def __binarize_image(image):
        alpha = 1.5
        beta = 50
        gray_image = np.array(np.clip(alpha*image + beta, 0, 255),np.uint8)
        return gray_image
