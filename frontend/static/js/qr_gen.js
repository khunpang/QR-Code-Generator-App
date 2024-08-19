function generateQRCode() {
    var text = document.querySelector(".message-box textarea").value;
    var qrCodeContainer = document.getElementById("qr-code-container");

    if (text) {
        qrCodeContainer.innerHTML = '';

        new QRCode(qrCodeContainer, {
            text: text,
            width: 180,
            height: 180
        });
        qrCodeContainer.style.display = "flex";
    } else {
        qrCodeContainer.style.display = "none";
    }
}
