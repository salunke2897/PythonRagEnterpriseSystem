import fitz


class ImageExtractor:
    def extract_image_metadata(self, file_path: str) -> list[dict]:
        metadata: list[dict] = []
        with fitz.open(file_path) as doc:
            for page_number, page in enumerate(doc, start=1):
                images = page.get_images(full=True)
                for img_index, img in enumerate(images, start=1):
                    xref = img[0]
                    image_info = doc.extract_image(xref)
                    metadata.append(
                        {
                            "page_number": page_number,
                            "image_index": img_index,
                            "xref": xref,
                            "width": image_info.get("width"),
                            "height": image_info.get("height"),
                            "ext": image_info.get("ext"),
                            "size_bytes": len(image_info.get("image", b"")),
                        }
                    )
        return metadata
