---
title: Style Guide
abstract: |
  Comprehensive style guide for maintaining consistency across structured markdown documentation. Covers writing style, formatting conventions, and presentation standards for professional documentation.
wc: 420
toc:
  - title: Writing Style
    abstract: |
      Guidelines for writing style, tone, and voice to ensure consistency across all documentation materials and maintain professional quality standards.
    wc: 150
    subsections:
      - title: Tone and Voice
        abstract: |
          Recommended tone and voice for different types of documentation content and target audiences.
        wc: 50
      - title: Language Usage
        abstract: |
          Guidelines for language choice, terminology, and communication clarity in technical documentation.
        wc: 55
      - title: Grammar and Punctuation
        abstract: |
          Standard grammar and punctuation rules specifically tailored for technical documentation contexts.
        wc: 45
  - title: Formatting Conventions
    abstract: |
      Standard formatting conventions for markdown elements, code blocks, tables, and other content components to ensure visual consistency.
    wc: 140
    subsections:
      - title: Markdown Elements
        abstract: |
          Proper usage of markdown syntax for headings, lists, emphasis, and other text formatting.
        wc: 50
      - title: Code Formatting
        abstract: |
          Standards for displaying code examples, syntax highlighting, and inline code elements.
        wc: 45
      - title: Tables and Lists
        abstract: |
          Guidelines for creating well-structured tables and lists that enhance readability.
        wc: 45
  - title: Visual Elements
    abstract: |
      Guidelines for using images, diagrams, and other visual elements to complement written content effectively.
    wc: 80
    subsections:
      - title: Image Usage
        abstract: |
          Best practices for selecting, formatting, and placing images within documentation.
        wc: 40
      - title: Diagram Standards
        abstract: |
          Standards for creating and integrating diagrams that clarify complex concepts.
        wc: 40
  - title: Accessibility Standards
    abstract: |
      Guidelines for ensuring documentation is accessible to users with disabilities and follows accessibility best practices.
    wc: 50
refs:
  - best_practices
  - getting_started_guide
  - templates
  - index
back_refs:
  - best_practices
---

# Writing Style

Consistent writing style is essential for professional documentation that communicates effectively with diverse audiences.

## Tone and Voice

### General Principles
- **Be Professional**: Maintain a professional, authoritative tone
- **Be Clear**: Use straightforward language that avoids ambiguity
- **Be Helpful**: Focus on assisting the reader achieve their goals
- **Be Consistent**: Maintain consistent tone throughout related content

### Audience-Specific Tone
- **Beginners**: Use encouraging, patient tone with detailed explanations
- **Technical Users**: Use precise, efficient tone with technical accuracy
- **Administrators**: Use formal, procedural tone with clear instructions

## Language Usage

### Terminology Standards
- **Define Terms**: Define technical terms on first use
- **Be Consistent**: Use the same term consistently throughout
- **Avoid Jargon**: Replace jargon with simpler alternatives when possible
- **Use Active Voice**: Prefer active voice over passive voice

### Clarity Guidelines
- **One Concept Per Sentence**: Keep sentences focused on single ideas
- **Short Paragraphs**: Limit paragraphs to 3-4 sentences maximum
- **Transitional Phrases**: Use transitions to guide readers through complex topics
- **Concrete Examples**: Provide specific examples to illustrate abstract concepts

## Grammar and Punctuation

### Grammar Rules
- **Subject-Verb Agreement**: Ensure proper agreement in all sentences
- **Tense Consistency**: Maintain consistent tense within sections
- **Pronoun Reference**: Ensure pronouns have clear antecedents
- **Parallel Structure**: Use parallel structure for lists and comparisons

### Punctuation Standards
- **Serial Comma**: Use Oxford comma for clarity in lists
- **Emphasis**: Use emphasis sparingly and consistently
- **Quotation Marks**: Use double quotes for quotations, single for technical terms
- **Hyphenation**: Follow standard hyphenation rules for compound terms

# Formatting Conventions

Consistent formatting enhances readability and professional appearance.

## Markdown Elements

### Heading Structure
- **H1 (#)**: Document title (only in YAML header)
- **H2 (##)**: Main sections
- **H3 (###)**: Subsections
- **H4 (####)**: Subsubsections (use sparingly)

### Text Formatting
- **Bold**: Use for key terms and emphasis (`**text**`)
- **Italic**: Use for foreign words and book titles (`*text*`)
- **Code**: Use for code elements and file names (`\`code\``)
- **Links**: Use descriptive link text, not raw URLs

## Code Formatting

### Inline Code
- Use backticks for short code elements: `\`function_name\``
- Include language context when helpful: `\`Python: import\``

### Code Blocks
- Specify language for syntax highlighting: ```python
- Keep code blocks focused and relevant
- Add comments to explain complex code
- Test all code examples

### File References
- Use consistent format: `filename.py`
- Include path when relevant: `src/main/filename.py`
- Use backticks for all file references

## Tables and Lists

### Table Standards
- **Headers**: Use clear, descriptive column headers
- **Alignment**: Left-align text, right-align numbers
- **Spacing**: Use consistent spacing for readability
- **Captions**: Add descriptive captions above tables

### List Guidelines
- **Parallel Structure**: Maintain consistent grammatical structure
- **Length**: Limit list items to single line when possible
- **Punctuation**: Use consistent punctuation at list ends
- **Hierarchy**: Use proper nesting for sublists

# Visual Elements

Visual elements should enhance, not replace, written content.

## Image Usage

### Image Selection
- **Relevance**: Ensure images directly support the text
- **Quality**: Use high-resolution, clear images
- **Consistency**: Maintain consistent style throughout
- **Accessibility**: Provide alt text for all images

### Image Formatting
- **Size**: Optimize for web display (max 800px width)
- **Format**: Use web-optimized formats (PNG, JPG, SVG)
- **Placement**: Place images close to relevant text
- **Captions**: Add descriptive captions below images

## Diagram Standards

### Diagram Types
- **Flowcharts**: For processes and workflows
- **Architecture Diagrams**: For system structures
- **Sequence Diagrams**: For interactions and timelines
- **Class Diagrams**: For object-oriented concepts

### Diagram Guidelines
- **Clarity**: Ensure diagrams are easy to understand
- **Consistency**: Use consistent styling and notation
- **Labels**: Label all elements clearly
- **Legend**: Include legends for complex diagrams

# Accessibility Standards

Ensure documentation is usable by everyone regardless of ability.

### General Accessibility
- **Alt Text**: Provide descriptive alt text for all images
- **Headers**: Use proper header hierarchy for screen readers
- **Links**: Use descriptive link text (avoid "click here")
- **Color**: Don't rely on color alone to convey information

### Technical Accessibility
- **Code Blocks**: Ensure code is readable by screen readers
- **Tables**: Add proper headers and captions for tables
- **Lists**: Use proper list markup for semantic structure
- **Language**: Specify document language in metadata

### Testing Accessibility
- **Screen Readers**: Test with popular screen reader software
- **Keyboard Navigation**: Ensure all content is keyboard accessible
- **Color Contrast**: Verify sufficient contrast ratios
- **Font Sizes**: Test with larger font sizes
