import torch
from transformers import T5Tokenizer, T5ForConditionalGeneration
import os
import re

class Translator:
    def __init__(self):
        self.model_dir = "./quantized_model"
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Khởi tạo translator với thiết bị: {self.device}")
        
        try:
            # Tải tokenizer và mô hình gốc
            self.tokenizer = T5Tokenizer.from_pretrained("VietAI/envit5-translation")
            print("Tải tokenizer thành công")
            
            print("Đang tải mô hình gốc...")
            self.model = T5ForConditionalGeneration.from_pretrained("VietAI/envit5-translation")
            self.model = self.model.to(self.device)
            
            # Chuyển mô hình sang chế độ đánh giá
            self.model.eval()
            print("Khởi tạo translator hoàn tất")
        except Exception as e:
            print(f"Lỗi khi khởi tạo: {str(e)}")
            raise
    
    def translate(self, text, direction='en_to_vi'):
        """
        Dịch văn bản giữa tiếng Anh và tiếng Việt
        """
        print(f"Đang dịch: '{text}' ({direction})")
        # Chuẩn bị văn bản đầu vào
        if direction == 'en_to_vi':
            input_text = f"en: {text}"
        else:  # vi_to_en
            input_text = f"vi: {text}"
        
        print(f"Input sau xử lý: '{input_text}'")
        # Mã hóa văn bản
        inputs = self.tokenizer(input_text, return_tensors="pt").to(self.device)
        
        # Tạo bản dịch
        try:
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs.input_ids,
                    max_length=512,
                    num_beams=4,
                    early_stopping=True
                )
            # Giải mã kết quả
            translation = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            # Loại bỏ tiền tố 'vi: ' hoặc 'en: ' nếu có
            translation = re.sub(r'^(vi|en):\s*', '', translation, flags=re.IGNORECASE)
            print(f"Kết quả dịch: '{translation}'")
            return translation
        except Exception as e:
            print(f"Lỗi khi tạo bản dịch: {str(e)}")
            return ""



class TranslatorQuantized:
    def __init__(self):
        self.model_dir = "./quantized_model"
        self.device = "cpu"  # Luôn dùng CPU cho mô hình quantize
        print(f"Khởi tạo translator với thiết bị: {self.device}")
        
        try:
            # Tải tokenizer từ mô hình gốc
            self.tokenizer = T5Tokenizer.from_pretrained("VietAI/envit5-translation")
            print("Tải tokenizer thành công")
            
            # Tải mô hình quantize từ state_dict
            print("Đang tải mô hình quantize...")
            base_model = T5ForConditionalGeneration.from_pretrained("VietAI/envit5-translation")
            base_model = base_model.to("cpu")
            self.model = torch.quantization.quantize_dynamic(
                base_model, {torch.nn.Linear}, dtype=torch.qint8
            )
            state_dict = torch.load(os.path.join(self.model_dir, "pytorch_model.bin"), weights_only=True)
            self.model.load_state_dict(state_dict)
            
            # Chuyển mô hình sang chế độ đánh giá
            self.model.eval()
            print("Khởi tạo translator hoàn tất")
        except Exception as e:
            print(f"Lỗi khi khởi tạo: {str(e)}")
            raise
    
    def translate(self, text, direction='en_to_vi'):
        """
        Dịch văn bản giữa tiếng Anh và tiếng Việt
        """
        print(f"Đang dịch: '{text}' ({direction})")
        # Chuẩn bị văn bản đầu vào
        if direction == 'en_to_vi':
            input_text = f"en: {text}"
        else:  # vi_to_en
            input_text = f"vi: {text}"
        
        print(f"Input sau xử lý: '{input_text}'")
        # Mã hóa văn bản
        inputs = self.tokenizer(input_text, return_tensors="pt").to(self.device)
        
        # Tạo bản dịch
        try:
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs.input_ids,
                    max_length=512,
                    num_beams=4,
                    early_stopping=True
                )
            # Giải mã kết quả
            translation = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            # Loại bỏ tiền tố 'vi: ' hoặc 'en: ' nếu có
            translation = re.sub(r'^(vi|en):\s*', '', translation, flags=re.IGNORECASE)
            print(f"Kết quả dịch: '{translation}'")
            return translation
        except Exception as e:
            print(f"Lỗi khi tạo bản dịch: {str(e)}")
            return ""