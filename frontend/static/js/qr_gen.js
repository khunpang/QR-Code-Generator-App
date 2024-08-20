function generateQRCode() {
    var text = document.querySelector(".message-box textarea").value;
    var qrCodeContainer = document.getElementById("qr-code-container");

    if (text) {
        qrCodeContainer.style.display = 'flex';  // ทำให้ qrCodeContainer แสดงผล

        qrCodeContainer.innerHTML = '';  // เคลียร์เนื้อหาก่อนสร้าง QR Code

        var qrCode = new QRCode(qrCodeContainer, {
            text: text,
            width: 180,
            height: 180
        });

        // รอให้ QR Code ถูกสร้างเสร็จ
        setTimeout(() => {
            var canvas = qrCodeContainer.querySelector('canvas');
            if (canvas) {
                // ดึงข้อมูลภาพ QR Code เป็น Base64
                var qrCodeImageBase64 = canvas.toDataURL('image/png');
                console.log("QR Code Image Base64:", qrCodeImageBase64);  // ตรวจสอบ Base64 ของภาพ QR Code

                // สร้างชื่อไฟล์
                var now = new Date();
                var qrCodeFilename = 'qr_code_' + now.toISOString().replace(/:/g, '-') + '.png';

                // เปลี่ยนให้รับ user_id จากเซสชันหรือการเข้าสู่ระบบจริง
                var userId = getUserId();  // ฟังก์ชันเพื่อดึง user_id ที่แท้จริงจากเซสชัน

                // ส่งข้อมูล QR Code ไปยังเซิร์ฟเวอร์
                fetch("/save_qr_history", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        text: text,
                        qr_code_image_filename: qrCodeFilename,
                        qr_code_image_base64: qrCodeImageBase64,
                        user_id: userId
                    })
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    console.log("QR Code history saved:", data);
                })
                .catch(error => {
                    console.error('There was a problem with the fetch operation:', error);
                });
            } else {
                console.error("Canvas not found!");
            }
        }, 100);
    } else {
        qrCodeContainer.style.display = "none";
    }
}

// ฟังก์ชันตัวอย่างเพื่อดึง user_id จากเซสชัน
function getUserId() {
    // แทนที่ด้วยวิธีการดึง user_id ที่แท้จริงจากเซสชันหรือการเข้าสู่ระบบ
    return 1;  // เปลี่ยนตามค่า user_id ที่แท้จริง
}
