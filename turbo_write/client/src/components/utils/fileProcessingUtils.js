import b64toBlob from "b64-to-blob";

// function for making online file
export function makeOnlineFile(fig, key) {
  // convert to image file
  const filename = "figure_" + key;
  const image_blob = b64toBlob(fig.data, fig.contentType);
  const image_file = new File([image_blob], filename, {
    type: fig.contentType,
    lastModified: Date.now()
  });

  const online_image_file = {
    uid: "previously_uploaded_" + key,
    lastModified: image_file.lastModified,
    lastModifiedDate: image_file.lastModifiedDate,
    name: filename,
    originFileObj: image_file,
    size: image_file.size,
    type: image_file.type,
    thumbUrl: "data:" + image_file.type + ";base64," + fig.data
  };

  return online_image_file;
}

// function for getting image size from a thumbUrl
export function getImageSize(thumbUrl) {
  var image = new Image();
  image.src = thumbUrl;
  return { width: image.width, height: image.height };
}
