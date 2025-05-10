import torch
from transformers import T5Tokenizer, T5ForConditionalGeneration
import os

# Đường dẫn và thiết lập
ORIGINAL_MODEL_NAME = "VietAI/envit5-translation"
QUANTIZED_MODEL_DIR = "./quantized_model"
os.makedirs(QUANTIZED_MODEL_DIR, exist_ok=True)

# Chọn thiết bị
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Sử dụng thiết bị: {device}")

# Tải mô hình và tokenizer
print("Đang tải mô hình gốc...")
tokenizer = T5Tokenizer.from_pretrained(ORIGINAL_MODEL_NAME)
model = T5ForConditionalGeneration.from_pretrained(ORIGINAL_MODEL_NAME)

# Lưu tokenizer
print(f"Đang lưu tokenizer vào {QUANTIZED_MODEL_DIR}...")
tokenizer.save_pretrained(QUANTIZED_MODEL_DIR)

# Chuyển mô hình sang CPU để quantize
model = model.to("cpu")
model.eval()

# Thực hiện dynamic quantization
print("Đang thực hiện dynamic quantization...")
quantized_model = torch.quantization.quantize_dynamic(
    model,
    {torch.nn.Linear},  # Quantize các lớp Linear
    dtype=torch.qint8  # Sử dụng int8
)

# Kiểm tra mô hình quantize
print("Kiểm tra mô hình quantize với văn bản mẫu...")
test_input = "en: VietAI is a non-profit organization with a mission to nurture AI talent."
inputs = tokenizer(test_input, return_tensors="pt")
with torch.no_grad():
    outputs = quantized_model.generate(inputs.input_ids, max_length=512)
translation = tokenizer.decode(outputs[0], skip_special_tokens=True)
print(f"Văn bản gốc: {test_input}")
print(f"Bản dịch: {translation}")

# Lưu mô hình quantize
print(f"Đang lưu mô hình quantize vào {QUANTIZED_MODEL_DIR}...")
# Lưu state_dict
torch.save(quantized_model.state_dict(), os.path.join(QUANTIZED_MODEL_DIR, "pytorch_model.bin"))
# Lưu toàn bộ mô hình
torch.save(quantized_model, os.path.join(QUANTIZED_MODEL_DIR, "full_quantized_model.pt"))
# Lưu cấu hình mô hình
quantized_model.config.save_pretrained(QUANTIZED_MODEL_DIR)
print(f"Đã lưu mô hình quantize và tokenizer vào {QUANTIZED_MODEL_DIR}")

# Kiểm tra kích thước mô hình
def get_model_size_mb(model):
    temp_path = "temp_model.pt"
    torch.save(model.state_dict(), temp_path)
    size_bytes = os.path.getsize(temp_path)
    os.remove(temp_path)
    return size_bytes / (1024 * 1024)

original_size = get_model_size_mb(model)
quantized_size = get_model_size_mb(quantized_model)
print(f"Kích thước mô hình gốc: {original_size:.2f} MB")
print(f"Kích thước mô hình quantize: {quantized_size:.2f} MB")
print(f"Giảm: {(original_size - quantized_size) / original_size * 100:.2f}%")