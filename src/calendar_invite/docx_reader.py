from docx import Document


def read_docx(file_path: str) -> str:
    doc = Document(file_path)
    return "\n".join(
        para.text.strip()
        for para in doc.paragraphs
        if para.text.strip()
    )
