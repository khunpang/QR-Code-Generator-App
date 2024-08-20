function generateQRCode() {
  var text = document.querySelector(".message-box textarea").value;
  var qrCodeContainer = document.getElementById("qr-code-container");

  if (text) {
    qrCodeContainer.style.display = "flex";

    qrCodeContainer.innerHTML = "";

    var qrCode = new QRCode(qrCodeContainer, {
      text: text,
      width: 180,
      height: 180,
    });

    setTimeout(() => {
      var canvas = qrCodeContainer.querySelector("canvas");
      if (canvas) {
        // convert QR Code to Base64
        var qrCodeImageBase64 = canvas.toDataURL("image/png");
        console.log("QR Code Image Base64:", qrCodeImageBase64);

        // create file
        var now = new Date();
        var qrCodeFilename =
          "qr_code_" + now.toISOString().replace(/:/g, "-") + ".png";

        // send qr code file to server
        fetch("/save_qr_history", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            text: text,
            qr_code_image_filename: qrCodeFilename,
            qr_code_image_base64: qrCodeImageBase64,
            user_id: 1,
          }),
        })
          .then((response) => {
            if (!response.ok) {
              throw new Error("Network response was not ok");
            }
            return response.json();
          })
          .then((data) => {
            console.log("QR Code history saved:", data);
          })
          .catch((error) => {
            console.error(
              "There was a problem with the fetch operation:",
              error
            );
          });
      } else {
        console.error("Canvas not found!");
      }
    }, 100);
  } else {
    qrCodeContainer.style.display = "none";
  }
}
