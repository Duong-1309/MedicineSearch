import google.generativeai as genai
import os, json
from dotenv import load_dotenv

load_dotenv(".env")
genai.configure(api_key=os.environ.get("GEMINI_KEY", "AIzaSyDYo8DACHJKhZEgacClZvbikfTRz3wJbro"))

def parse_query_dimensions(question: str) -> str:
    model = genai.GenerativeModel('gemini-2.0-flash')
    prompt = f"""
Input: Một câu hỏi bằng tiếng Việt về thuốc (ví dụ: “Thuốc nào dạng tiêm chữa nhiễm trùng?”)
Output:
•   Trích xuất các thuộc tính liên quan đến thuốc để tìm kiếm theo dữ liệu sau: Medicine Name, Composition, Uses, Side_effects, Manufacturer.
•	Mỗi thuộc tính ghi rõ tên bằng tiếng Anh chuẩn như cột dữ liệu.
•	Chỉ điền giá trị nếu câu hỏi có nhắc đến hoặc có thể suy luận trực tiếp, không suy diễn thêm.
•	Dịch các thuật ngữ y tế/pháp lý sang tiếng Anh chuyên ngành.
Ví dụ:
Input: “Thuốc nào dạng tiêm chữa nhiễm trùng?”
Output: uses: bacterial infections
Input: “Thuốc nào trị ung thư buồng trứng hiệu quả?”
Output: uses: ovarian cancer
Câu hỏi: {question}
    """
    response = model.generate_content(prompt)
    return response.text.strip()

def summarize_results(question: str, documents: list) -> str:
    model = genai.GenerativeModel('gemini-2.0-flash')
    docs_text = "\\n".join(documents)
#     prompt = f"""
# Dựa trên các thông tin thuốc sau đây:
# {docs_text}
# Hãy trả lời câu hỏi sau một cách ngắn gọn và súc tích, không cần giải thích thêm:
# Lưu ý: tôi chỉ muốn câu trả lời pục vụ tra cứu, không tư vấn cho bệnh nhân
# và trả response dưới dạng html được đặt trong thẻ div. ví dụ <div>`your html`</div>.
# {question}
#     """
    prompt = f"""
    Dựa trên danh sách thông tin thuốc sau đây:
{docs_text}
Hãy thực hiện các bước sau:
1. Trả lời câu hỏi {question} một cách ngắn gọn, súc tích, chỉ tập trung vào thông tin liên quan đến tra cứu thuốc, không tư vấn y khoa.
2. Trả kết quả dưới dạng text thuần, không cần bọc HTML.
3. Dịch nội dung câu trả lời sang tiếng Việt, sử dụng đúng thuật ngữ chuyên ngành y tế (ví dụ: "Uses" dịch thành "Chỉ định", "Side effects" dịch thành "Tác dụng phụ", v.v.).
4. Trả kết quả cuối cùng là bản dịch tiếng Việt, không cẩn bản tiếng anh.

Quy tắc:
- Không thêm giải thích ngoài yêu cầu.
- Nếu nhiều thuốc phù hợp, liệt kê ngắn gọn tất cả.
- Nếu không tìm thấy thuốc phù hợp, ghi rõ: "Không tìm thấy thuốc phù hợp."
    """
    response = model.generate_content(prompt)
    print(f"🔍 Summarized Response: {response.text.strip()}")
    return response.text.strip()

def translate_results(results: list[dict]) -> list[dict]:
    model = genai.GenerativeModel('gemini-2.0-flash')
    prompt = """
    Bạn được cung cấp một danh sách dữ liệu dạng JSON như sau:
[
  {
    "id": 7493,
    "uses": " Bacterial infections",
    "side_effects": "Vomiting Nausea Diarrhea Taste change"
  }
]`

Yêu cầu:
- Dịch các giá trị text trong trường "uses" và "side_effects" sang tiếng Việt bằng từ chuyên ngành y dược.
- Giữ nguyên cấu trúc JSON, đúng format, đúng "id".
- Nếu có từ ngữ không chắc chắn hoặc không dịch được, giữ nguyên từ tiếng Anh ban đầu.
- Không thay đổi key hay thêm bớt dữ liệu.
- Trả về đúng kết quả dạng JSON. Không được phép thay đổi định dạng JSON.

Ví dụ:
- "Bacterial infections" ➔ "Nhiễm khuẩn"
- "Vomiting" ➔ "Nôn mửa"
- "Nausea" ➔ "Buồn nôn"
- "Diarrhea" ➔ "Tiêu chảy"
- "Taste change" ➔ "Thay đổi vị giác"

Bây giờ, hãy tiến hành dịch dữ liệu sau:
    """ + str(results)
    response = model.generate_content(prompt)
    text = response.text.strip()
    print(f"🔍 Summarized Response: {response.text.strip()}")
    text = text.replace('```', '').replace('json', '')
    return json.loads(text)