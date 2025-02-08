# Chunking
Use powers of two as chunk sizes, specially 256 and 512 with an overlap of 20(test it more)
## 1. Fixed-Size Chunking
Fixed-size chunking splits documents into chunks of a predefined size, typically by word count, token count, or character count.

### When to Use:
When you need a simple, straightforward approach and the document structure isn’t critical. It works well when processing smaller, less complex documents.

#### Advantages:
Easy to implement.
Consistent chunk sizes.
Fast to compute.

#### Disadvantages:
May break sentences or paragraphs, losing context.
Not ideal for documents where maintaining meaning is important.
```python
def fixed_size_chunk(text, max_words=100):
    words = text.split()
    return [' '.join(words[i:i + max_words]) for i in range(0, len(words), 
    max_words)]

# Applying Fixed-Size Chunking
fixed_chunks = fixed_size_chunk(sample_text)
for chunk in fixed_chunks:
    print(chunk, '\n---\n')
```
## 2. Sentence-Based Chunking
This method chunks text based on natural sentence boundaries. Each chunk contains a set number of sentences, preserving semantic units.

### When to Use:
Maintaining coherent ideas is crucial, and splitting mid-sentence would result in losing meaning.

#### Advantages:
Preserves sentence-level meaning.
Better context preservation.

#### Disadvantages:
Uneven chunk sizes, as sentences vary in length.
May exceed token limits in models when sentences are too long.
```python
import spacy
nlp = spacy.load("en_core_web_sm")

def sentence_chunk(text):
    doc = nlp(text)
    return [sent.text for sent in doc.sents]

# Applying Sentence-Based Chunking
sentence_chunks = sentence_chunk(sample_text)
for chunk in sentence_chunks:
    print(chunk, '\n---\n')
```

## 3. Paragraph-Based Chunking 
This strategy splits text based on paragraph boundaries, treating each paragraph as a chunk.

### When to Use:
Best for structured documents like reports or essays where each paragraph contains a complete idea or argument.

#### Advantages:

Natural document segmentation.
Preserves larger context within a paragraph.
#### Disadvantages:

Paragraph lengths vary, leading to uneven chunk sizes.
Long paragraphs may still exceed token limits.

```python
def paragraph_chunk(text):
    paragraphs = text.split('\n\n')
    return paragraphs

#### Applying Paragraph-Based Chunking
paragraph_chunks = paragraph_chunk(sample_text)
for chunk in paragraph_chunks:
    print(chunk, '\n---\n')
```

#### Sample Text
```python
sample_text = """
Introduction

Data Science is an interdisciplinary field that uses scientific methods, processes,
 algorithms, and systems to extract knowledge and insights from structured and 
 unstructured data. It draws from statistics, computer science, machine learning, 
 and various data analysis techniques to discover patterns, make predictions, and 
 derive actionable insights.

Data Science can be applied across many industries, including healthcare, finance,
 marketing, and education, where it helps organizations make data-driven decisions,
  optimize processes, and understand customer behaviors.

Overview of Big Data

Big data refers to large, diverse sets of information that grow at ever-increasing 
rates. It encompasses the volume of information, the velocity or speed at which it 
is created and collected, and the variety or scope of the data points being 
covered.

Data Science Methods

There are several important methods used in Data Science:

1. Regression Analysis
2. Classification
3. Clustering
4. Neural Networks

Challenges in Data Science

- Data Quality: Poor data quality can lead to incorrect conclusions.
- Data Privacy: Ensuring the privacy of sensitive information.
- Scalability: Handling massive datasets efficiently.

Conclusion

Data Science continues to be a driving force in many industries, offering insights 
that can lead to better decisions and optimized outcomes. It remains an evolving 
field that incorporates the latest technological advancements.
"""
```
## 4. Semantic-Based Chunking
This method uses machine learning models (like transformers) to split text into chunks based on semantic meaning. This version use sentence-based chunking

### When to Use:
When preserving the highest level of context is critical, such as in complex, technical documents.

#### Advantages:
Contextually meaningful chunks.
Captures semantic relationships between sentences.

#### Disadvantages:
Requires advanced NLP models, which are computationally expensive.
More complex to implement.
```python
def semantic_chunk(text, max_len=512):
    doc = nlp(text)
    chunks = []
    current_chunk = []
    for sent in doc.sents:
        current_chunk.append(sent.text)
        if len(' '.join(current_chunk)) > max_len:
            chunks.append(' '.join(current_chunk))
            current_chunk = []
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    return chunks

# Applying Semantic-Based Chunking
semantic_chunks = semantic_chunk(sample_text)
for chunk in semantic_chunks:
    print(chunk, '\n---\n')
```
Next is at example of sentece-based chunking with overlap
```python
def semantic_chunk(text, max_len=512):
    doc = nlp(text)
    chunks = []
    current_chunk = []
    for sent in doc.sents:
        current_chunk.append(sent.text)
        if len(' '.join(current_chunk)) > max_len:
            chunks.append(' '.join(current_chunk))
            current_chunk = [sent]
    if len(current_chunk)>1:
        chunks.append(' '.join(current_chunk))
    return chunks

# Applying Semantic-Based Chunking
semantic_chunks = semantic_chunk(sample_text)
for chunk in semantic_chunks:
    print(chunk, '\n---\n')
```

## 5. Hierarchical Chunking
Hierarchical chunking breaks down documents at multiple levels, such as sections, subsections, and paragraphs.

### When to Use:
For highly structured documents like academic papers or legal texts, where maintaining hierarchy is essential.

#### Advantages:
Preserves document structure.
Maintains context at multiple levels of granularity.

#### Disadvantages:
More complex to implement.
May lead to uneven chunks.
```python
def hierarchical_chunk(text, section_keywords):
    sections = []
    current_section = []
    for line in text.splitlines():
        if any(keyword in line for keyword in section_keywords):
            if current_section:
                sections.append("\n".join(current_section))
            current_section = [line]
        else:
            current_section.append(line)
    if current_section:
        sections.append("\n".join(current_section))
    return sections

# Applying Hierarchical Chunking
section_keywords = ["Introduction", "Overview", "Methods", "Conclusion"]
hierarchical_chunks = hierarchical_chunk(sample_text, section_keywords)
for chunk in hierarchical_chunks:
    print(chunk, '\n---\n')
```