import os
from typing import List
from pypdf import PdfReader
from langdetect import detect
from src.core.interfaces import IDocumentLoader
from src.core.models import Document

class UnifiedDocumentLoader(IDocumentLoader):
    def get_supported_formats(self) -> List[str]:
        return ["pdf", "md", "txt"]

    def load(self, source: str, **kwargs) -> List[Document]:
        all_documents = []
        if os.path.isdir(source):
            files_to_process = [os.path.join(source,f) for f in os.listdir(source)]
        else:
            files_to_process = [source]  

        for file_path in files_to_process:
            ext = source.split('.')[-1].lower()
            if ext not in self.get_supported_formats():
                continue # ici on va ignorer les fichers qui ont une extension autres que pdf,txt et md
    

            content = ""
            if ext == 'pdf':
                 reader = PdfReader(source)
                 content = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
            elif ext in ['md', 'txt']:
                with open(source, 'r', encoding='utf-8') as f:
                    content = f.read()

            if content.strip():
                try: lang = detect(content[:1000])
                except: lang = "unknown"

                all_documents.append(Document(
                    content=content,
                    metadata={"source": file_path, "format": ext, "lang": lang}
                ))
        
        return all_documents