#!/usr/bin/env python3
"""
Example usage of the tokenizer verifier.
This file demonstrates how the tokenizer verifier would work with various test cases.
"""

from tokenizer_verifier import TokenizerVerifier

def run_examples():
    """Run example verifications to demonstrate functionality."""
    
    print("=== Tokenizer Verifier Examples ===\n")
    
    # Note: These examples would work if tiktoken encodings were available
    examples = [
        "Hello, world!",
        "This is a test with émojis 🚀🎉",
        "Unicode: café, naïve, résumé", 
        "Numbers: 12345 and symbols: @#$%^&*()",
        "Mixed case: CamelCase and snake_case",
        "Whitespace:\ttabs\nand\r\nnewlines   ",
        "Special chars: ""''—–…",
        # Potentially problematic cases
        "a" * 100,  # Long repetition
        "🏳️‍🌈🏴‍☠️👨‍👩‍👧‍👦",  # Complex emoji sequences  
        "\x00\x01\x02",  # Control characters
        "مرحبا بالعالم",  # Arabic text
        "Здравствуй, мир!",  # Cyrillic text
        "こんにちは世界",  # Japanese text
    ]
    
    try:
        verifier = TokenizerVerifier()
        print(f"Using encoding: {verifier.encoding_name}\n")
        
        for i, text in enumerate(examples, 1):
            print(f"Example {i}: {repr(text)}")
            result = verifier.comprehensive_verification(text)
            
            print("Summary:")
            for item in result["summary"]:
                print(f"  {item}")
            
            if result["overall_has_issues"]:
                print("  ⚠️  Issues detected!")
            
            print()
            
    except Exception as e:
        print(f"Cannot run examples due to network/encoding issue: {e}")
        print("\nThis is expected in environments without internet access.")
        print("The tokenizer verifier would work with proper tiktoken setup.")
        
        # Show what the output structure would look like
        print("\n=== Sample Output Structure ===")
        sample_result = {
            "text": "Hello, world!",
            "encoding": "cl100k_base", 
            "round_trip_analysis": {
                "original_text": "Hello, world!",
                "decoded_text": "Hello, world!",
                "original_tokens": [9906, 11, 1917, 0],
                "reencoded_tokens": [9906, 11, 1917, 0], 
                "round_trip_consistent": True,
                "text_preserved": True,
                "has_issues": False
            },
            "boundary_analysis": {
                "original_text": "Hello, world!",
                "reconstructed_text": "Hello, world!",
                "token_count": 4,
                "text_matches": True,
                "issues": [],
                "has_issues": False
            },
            "overall_has_issues": False,
            "summary": ["✅ No issues detected"]
        }
        
        print(f"Sample verification result structure:")
        import json
        print(json.dumps(sample_result, indent=2))


if __name__ == "__main__":
    run_examples()