import re
import io
import markitdown

class HierarchicalChunker():
    
    def __init__(self, max_chunk_size: int = 2000, chunk_overlap: int = 200, other_headers: list[tuple[str,str]] = None):
        """
        Initialize the HierarchicalChunker with custom headers and chunking parameters.
        
        :param max_chunk_size: Maximum size of each chunk in words.
        :param chunk_overlap: Number of words to overlap between chunks.
        :param other_headers: Additional headers to include in the chunking process.
        """
        
        
        # Define default headers
        self.headers = [(r"#{1,6} ", "header")]
        if other_headers :
            self.headers.extend(other_headers)

        #self.headers.append((r"\n\n", "parrafo"))  # Add paragraph as a header for text chunks
        self.max_chunk_size = max_chunk_size
        self.chunk_overlap = chunk_overlap
    
    
    def clean_text(self, text: str) -> str:
        RESOLUTION_SEP = r"^___+\n"
        pages = re.split(RESOLUTION_SEP, text, flags=re.MULTILINE)
        new_pages = []
    
        for page in pages[1:]:
            # Before chunking, clean the text
            # Header
            page = re.sub(r"\*\*Gaceta Oficial de la República\*\*","",page)
            page = re.sub(r"GACETA OFICIAL", "", page)
            # Page Number
            page = re.sub(r"\*\*\d+\*\*","",page)

            # Dates
            page = re.sub(r"\*\*\d{2}/\d{2}/\d{4}\*\*","",page)

            page = re.sub(r'GOC-\d{4}-.+',"",page)
            # In case de some asterics left
            page = re.sub(r"\*{2,4}","",page)

            # Multiple lines
            page = re.sub(r"\n{3,}","\n\n",page)
            new_pages.append(page.strip())

        return "\n".join(new_pages)

    
    def table2text(self, rows: list[str]):
        patterns = r"\| Unnamed: \d \||\| \-{3,} \||\|\s+\||\| NaN \|"
        new_rows = []
        print(rows)
        for row in rows:
            if not re.search(patterns,row):
                new_rows.append(row)

        rows_name = new_rows[0].strip("|").split("|")
        end_lines = []
        for new_row  in new_rows[1:]:
            elemns  = new_row.strip("|").split("|")
            line = " ".join(f"{i.strip()} {j.strip()}" for i,j in zip(rows_name,elemns))#type: ignore
            end_lines.append(line)
        return "\n".join(end_lines)


    def markdown2tree(self,text: str) -> list[dict]:
        """
        Convert a markdown text to a tree structure.
        Returns a list of dictionaries representing the markdown hierarchy.
        Each node has:
        - level: int (header level, inf for text)
        - content: str (header text without # or text content)
        - children: list[dict] (child nodes)
        """
        if not text.strip():
            return []

        text = self.clean_text(text)
        # Initialize the tree and stack for parent nodes
        tree = []
        node_stack = []  # Stack to track parent nodes
        current_text = []

        lines = text.split("\n")
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            print(line)
            if any(re.match(pattern, line) for pattern, _ in self.headers):  # Check if line matches any header pattern
                
                current_header_type = ""
                current_pattern = r""
                index = float("inf")  # Default to inf for text nodes
                for header_index, pattern in enumerate(self.headers):
                    if re.match(pattern[0], line):
                        current_header_type = pattern[1]
                        current_pattern = pattern[0]
                        index = header_index + 1
                        break
                    
                # If there's accumulated text, add it to the current node or root
                if current_text:
                    text_node = {
                        "level": float("inf"),  # Text nodes have level inf
                        "content": "\n".join(current_text).strip(),
                        "children": [],
                        "type": "text"
                    }
                    
                    if node_stack:
                        node_stack[-1]["children"].append(text_node)
                    else:
                        tree.append(text_node)
                    current_text = []

                level = index
                content =re.sub(current_pattern,"",line).strip()
                node = {"level": index, "content": content, "children": [], "type": current_header_type}

                # Find the appropriate parent node
                while node_stack and node_stack[-1]["level"] >= level:
                    node_stack.pop()

                if node_stack:
                    node_stack[-1]["children"].append(node)
                else:
                    tree.append(node)

                node_stack.append(node)

            # Table start (opcional, puedes mantenerlo si lo necesitas)
            elif line.startswith("|") and line.endswith("|"):
                j = i + 1
                table_lines = [line]
                # Find all the lines that are part of the current table
                for temp_line in lines[j:]:
                    strip_line = temp_line.strip()
                    if strip_line.startswith("|") and strip_line.endswith("|"):
                        j += 1
                        table_lines.append(strip_line)
                    else:
                        break
                
                print(table_lines)
                # Once the search ends, create the text from the table
                table_text = self.table2text(table_lines)  # Simulación, puedes usar table2text si existe
                current_text.append(table_text)
                i = j - 1

            elif line:
                current_text.append(line)

            elif current_text:  # Empty line after text
                text_node = {
                    "level": float("inf"),
                    "content": "\n".join(current_text).strip(),
                    "children": []
                }
                if node_stack:
                    node_stack[-1]["children"].append(text_node)
                else:
                    tree.append(text_node)
                current_text = []

            i += 1

        # Handle any remaining text (al final del archivo)
        if current_text:
            text_node = {
                "level": float("inf"),
                "content": "\n".join(current_text).strip(),
                "children": []
            }
            if node_stack:
                node_stack[-1]["children"].append(text_node)
            else:
                tree.append(text_node)

        return tree


    def hierarchial_markdown_chunker(self,max_chunk_size: int = 2000):
        """
        Chunker function that splits text based on markdown hierarchy.
        Each chunk is a tuple of (header_path, content).
        - header_path: string with headers separated by newlines
        - content: text content of the chunk
        """
        def chunker(text: str) -> list[tuple[str, str]]:
            tree = self.markdown2tree(text)
            chunks = []

            def process_node(node: dict, current_header_path: str = ""):
                nonlocal chunks

                # Add current node's content
                if node["level"] != float("inf"):
                    current_header = f"{current_header_path}\n{node['content']}" if current_header_path else node["content"]

                    # Process children
                    for child in node["children"]:
                        process_node(child, current_header)
                else:
                    # Text node
                    content = node["content"]
                    words = content.split()
                    current_chunk = []
                    current_size = 0

                    for word in words:
                        if current_size + len(word.split()) > max_chunk_size:
                            if current_chunk:  # Only append if we have content
                                chunks.append((current_header_path.strip(), " ".join(current_chunk).strip()))
                            current_chunk = [word]
                            current_size = len(word.split())
                        else:
                            current_chunk.append(word)
                            current_size += len(word.split())

                    if current_chunk:  # Append any remaining content
                        chunks.append((current_header_path.strip(), " ".join(current_chunk).strip()))

            for node in tree:
                process_node(node, "")

            return chunks

        return chunker
    
    
    
if __name__ == "__main__":
    path = "/home/alejbv/Projects/RAG-AssistBot/test/"
    document = "GO_151_29_Diciembre_2021_ordinaria.md"#"GO_17_20_Febrero_2024_ordinaria.md"
    DOCUMENT_SEP = [
            (r"CAP[IÍ]TULO","Capitulo"),
            (r"ART[IÍ]CULO","Articulo"),
            (r"ACUERDO","Acuerdo"),
            (r"ANEXO","Anexo"),
            (r"^[A-Z]+:","Declaración"),
            (r"\d+\.\s","Numeración"),
            (r"[a-z]\)","Inciso"),
        ]
    chunker = HierarchicalChunker(other_headers=DOCUMENT_SEP).hierarchial_markdown_chunker()
    
    with open(path+document,mode='b+r') as fd:
        converter = markitdown.MarkItDown()
        result = converter.convert_stream(
            io.BytesIO(fd.read()), file_extension=document.split(".")[-1]
        )
        text = result.markdown
        for chunk in chunker(text):
            header_path, content = chunk
            print(f"Header Path: {header_path}")
            print(f"Content:\n{content}\n")
            print("-----")