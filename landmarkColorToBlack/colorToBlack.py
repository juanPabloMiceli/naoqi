from os.path import join
from tempfile import TemporaryDirectory
from pdf2image import convert_from_path # https://pypi.org/project/pdf2image/
from img2pdf import convert # https://pypi.org/project/img2pdf/
from PIL import Image 

with TemporaryDirectory() as temp_dir: # Saves images temporarily in disk rather than RAM to speed up parsing
    # Converting pages to images
    print("Parsing pages to grayscale images. This may take a while")
    images = convert_from_path(
        "NAOmark.pdf",
        output_folder=temp_dir,
        grayscale=True,
        fmt="jpeg",
        thread_count=4
    )
    thresh = 200
    fn = lambda x : 255 if x > thresh else 0
    images2 = []
    for image in images:
        images2.append(image.convert('L').point(fn, mode='1'))

    images = images2

    image_list = list()
    for page_number in range(1, len(images) + 1):
        path = join(temp_dir, "page_" + str(page_number) + ".jpeg")
        image_list.append(path)
        images[page_number-1].save(path, "JPEG") # (page_number - 1) because index starts from 0

    with open("Gray_PDF.pdf", "bw") as gray_pdf:
        gray_pdf.write(convert(image_list))

    print("The new page is saved as Gray_PDF.pdf in the current directory.")