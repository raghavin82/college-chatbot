from pypdf import PdfReader

pdf_path = "data/raw/semester_3.pdf"
output_path = "data/processed/semester_3.text"

reader = PdfReader(pdf_path)

with open(output_path, "w", encoding="utf-8") as file:
    for page_number, page in enumerate(reader.pages, start=1):

        text = page.extract_text()

        file.write(f"\n---PAGE {page_number}---\n")

        if text:
            file.write(text)
        else:
            file.write("[No text found on this page.\n")

print("PDF is extracted successfully!")
print(f"Saved to: {output_path}")