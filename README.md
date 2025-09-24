# Tokenizer Verifier

A simple app to identify cases when tiktoken tokenizer makes mistakes.

## Overview

This tool helps identify potential issues with tiktoken tokenization by performing various verification checks:

- **Round-trip consistency**: Verifies that text → tokens → text → tokens produces consistent results
- **Token boundary analysis**: Analyzes how text is split into tokens and identifies unusual patterns
- **Character preservation**: Ensures original text is preserved through tokenization cycles
- **Substring analysis**: Finds specific substrings that cause tokenization issues

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Command Line Interface

Basic usage:
```bash
python tokenizer_verifier.py "Hello, world!"
```

Specify encoding:
```bash
python tokenizer_verifier.py --encoding gpt2 "Your text here"
```

Read from stdin:
```bash
echo "Your text" | python tokenizer_verifier.py
```

Verbose output with detailed token analysis:
```bash
python tokenizer_verifier.py --verbose "Complex text with émojis 🚀"
```

Find problematic substrings (useful for debugging):
```bash
python tokenizer_verifier.py --find-substrings "Text to analyze"
```

### Available Encodings

The tool supports all tiktoken encodings:
- `gpt2` - GPT-2 encoding
- `r50k_base` - Used by Ada and Babbage models  
- `p50k_base` - Used by Codex models
- `p50k_edit` - Used by edit models
- `cl100k_base` - Used by GPT-3.5/GPT-4 models
- `o200k_base` - Used by newer models

### Python API

```python
from tokenizer_verifier import TokenizerVerifier

# Create verifier instance
verifier = TokenizerVerifier(encoding_name="cl100k_base")

# Run comprehensive verification
result = verifier.comprehensive_verification("Your text here")

if result["overall_has_issues"]:
    print("Issues found!")
    for issue in result["summary"]:
        print(f"  {issue}")

# Check round-trip consistency
round_trip = verifier.verify_round_trip("Test text")
print(f"Round-trip consistent: {round_trip['round_trip_consistent']}")

# Analyze token boundaries  
boundaries = verifier.analyze_token_boundaries("Test text")
print(f"Token count: {boundaries['token_count']}")
```

## What Issues Can It Detect?

1. **Text Loss**: Cases where original text is not preserved after tokenization
2. **Token Inconsistency**: Different token sequences for the same text
3. **Boundary Problems**: Unexpected token splitting patterns
4. **Encoding Issues**: Characters that don't round-trip properly
5. **Whitespace Issues**: Problems with spaces, tabs, newlines
6. **Unicode Issues**: Problems with complex Unicode sequences

## Example Output

```
=== Tokenizer Verification Results ===
Encoding: cl100k_base
Text length: 13 characters
Token count: 4

=== Summary ===
✅ No issues detected

=== Token Boundary Analysis ===
Token breakdown:
    9906: 'Hello'
      11: ','
    1917: ' world'
       0: '!'
```

## Common Use Cases

- **Debugging tokenization issues** in NLP applications
- **Validating text preprocessing** pipelines
- **Finding edge cases** in tokenizer behavior  
- **Quality assurance** for text processing workflows
- **Research** into tokenizer reliability

## Examples

Run the examples script to see various test cases:

```bash
python examples.py
```

## Limitations

- Requires internet connection to download tiktoken encodings on first use
- Performance depends on text length and complexity
- Substring analysis can be slow for very long texts

## Contributing

Feel free to submit issues and enhancement requests!