// pop an image in the new window
export function popImage(image_thumbUrl) {
  const popup = window.open("", "_blank", "width=800, height=800");
  popup.document.write("<title>放大的图片</title>");
  popup.document.write(
    "<img src='" +
      image_thumbUrl +
      "' max-width:100%'" +
      "' max-heigh:100%'" +
      "' onclick='window.close()' style='position:absolute;left:0;top:0'>"
  );
}

// pop text
export function popText(text) {
  const popup = window.open("", "_blank", "width=800, height=800");
  popup.document.write("<title>全文</title>");
  popup.document.write("<div>" + text + "</div>");
}
