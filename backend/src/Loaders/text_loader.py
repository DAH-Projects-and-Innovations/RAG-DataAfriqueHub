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
        if not os.path.exists(source):
            raise FileNotFoundError(f"Le fichier {source} n'est pas trouvé.")
            
        ext = source.split('.')[-1].lower()
        content = ""
        
        if ext == 'pdf':
            reader = PdfReader(source)
            content = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
        elif ext in ['md', 'txt']:
            with open(source, 'r', encoding='utf-8') as f:
                content = f.read()
        else:
            raise ValueError(f"Format .{ext} non supporté.")

        try:
            lang = detect(content[:1000])
        except:
            lang = "unknown"

        return [Document(
            content=content,
            metadata={"source": source, "format": ext, "lang": lang}
        )]