import gradio as gr
import PyPDF2
import fitz  # PyMuPDF
import requests
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from claude_api import Client
from api_key import claude_cookie

claude = Client(claude_cookie)

def process_pdf(file):
    doc = fitz.open(file.name)
    
    # 提取所有頁面的文字
    text_contents = []
    for page in doc:
        text_contents.append(page.get_text("text"))

    # 創建新的 PDF 並寫入提取的文字
    output_pdf = "processed_pdf_text_only.pdf"
    c = canvas.Canvas(output_pdf, pagesize=letter)
    width, height = letter
    for text in text_contents:
        y_position = height - 100  # 這可以根據需要調整
        for line in text.splitlines():
            c.drawString(100, y_position, line)  # x, y, text
            y_position -= 14  # 行間距，可以根據需要調整
        c.showPage()  # 結束當前頁並開始新的頁面
    c.save()

    doc.close()
    
    # 回傳處理後的 PDF 檔案路徑
    return output_pdf


def call_api(text, pdf):
    # 假設這裡是呼叫 API 的程式碼
    # response = requests.post("YOUR_API_ENDPOINT", data={"text": text})
    # return response.text
    # res = claude.send_message(prompt, conversation_id, it, timeout=6000)
    conversation_id = claude.create_new_chat()['uuid']

    res = claude.send_message(text, conversation_id, pdf, timeout=6000)
    claude.delete_conversation(conversation_id)
    return res

def app(pdf_file, user_input):
    processed_pdf = process_pdf(pdf_file)
    api_response = call_api(user_input, processed_pdf)
    return api_response

iface = gr.Interface(
    fn=app,
    inputs=[
        gr.inputs.File(label="上傳論文 PDF"),
        gr.inputs.Textbox(lines=5, placeholder="輸入文字..."),
    ],
    outputs=[
        # gr.outputs.File(label="處理後的 PDF"),
        gr.outputs.Textbox(label="API 回應")
    ],
    title="Talk to Paper"
)

iface.launch(share=True)
