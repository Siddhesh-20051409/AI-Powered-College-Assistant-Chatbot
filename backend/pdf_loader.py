import fitz  # PyMuPDF

def extract_pdf(file_path):
    doc = fitz.open(file_path)
    text = ""

    for page in doc:
        text += page.get_text()

    return text

if __name__ == "__main__":
    text = extract_pdf("../data/prospectus.pdf")

    with open("../data/pdf.txt", "w", encoding="utf-8") as f:
        f.write(text)

    print("PDF data extracted!")