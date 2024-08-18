import qrcode
from fastapi.responses import StreamingResponse
from io import BytesIO

@app.post("/generate_qr_code")
def generate_qr_code(data: str):
    img = qrcode.make(data)
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")