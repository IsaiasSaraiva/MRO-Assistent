from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import os
import fitz  # PyMuPDF
from pdf2image import convert_from_path
import pytesseract
from config import CHUNK_SIZE, CHUNK_OVERLAP, UPLOAD_DIR

class PDFProcessor:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            length_function=len,
        )
    
    def save_uploaded_file(self, uploaded_file):
        """Salva o arquivo PDF enviado"""
        file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return file_path
    
    def is_scanned_pdf(self, file_path):
        """Verifica se o PDF é escaneado (sem texto)"""
        doc = fitz.open(file_path)
        total_text = 0
        
        # Verificar primeiras 3 páginas
        for page_num in range(min(3, len(doc))):
            page = doc[page_num]
            text = page.get_text()
            total_text += len(text.strip())
        
        doc.close()
        
        # Se tem menos de 100 caracteres nas primeiras páginas, provavelmente é escaneado
        return total_text < 100
    
    def extract_text_with_ocr(self, file_path):
        """Extrai texto de PDF escaneado usando OCR"""
        print(f"🔍 PDF escaneado detectado. Usando OCR...")
        
        # Converter PDF para imagens
        images = convert_from_path(file_path, dpi=400)
        
        documents = []
        for i, image in enumerate(images):
            # OCR em português
            text = pytesseract.image_to_string(
                image, 
                lang='por',
                config='--psm 6 --oem 3'  # Melhor para blocos de texto
            )
            
            # Criar documento
            doc = Document(
                page_content=text,
                metadata={
                    "source": file_path,
                    "page": i + 1
                }
            )
            documents.append(doc)
            print(f"   ✅ Página {i+1}/{len(images)} processada ({len(text)} chars)")
        
        return documents
    
    def load_and_split_pdf(self, file_path):
        """Carrega PDF e divide em chunks (com OCR se necessário)"""
        
        # Verificar se precisa de OCR
        if self.is_scanned_pdf(file_path):
            documents = self.extract_text_with_ocr(file_path)
        else:
            # PDF com texto normal
            loader = PyMuPDFLoader(file_path)
            documents = loader.load()
        
        # Dividir em chunks
        chunks = self.text_splitter.split_documents(documents)
        
        return chunks
    
    def process_pdf(self, uploaded_file):
        """Processa PDF completo: salva, carrega e divide"""
        file_path = self.save_uploaded_file(uploaded_file)
        chunks = self.load_and_split_pdf(file_path)
        
        return {
            "file_path": file_path,
            "chunks": chunks,
            "num_chunks": len(chunks),
            "file_name": uploaded_file.name
        }