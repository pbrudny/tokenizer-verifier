#!/usr/bin/env python3
"""
Tokenizer Verifier - A simple app to identify cases when tiktoken tokenizer makes mistakes.

This module provides functionality to verify tokenization results and identify potential
issues with tiktoken tokenization, such as:
- Round-trip consistency (encode -> decode -> encode)
- Token boundary issues
- Unexpected token splits
- Character encoding problems
"""

import argparse
import sys
from typing import List, Dict, Any, Optional, Tuple
import tiktoken


class TokenizerVerifier:
    """Main class for verifying tokenizer behavior and identifying potential mistakes."""
    
    def __init__(self, encoding_name: str = "cl100k_base"):
        """Initialize with a specific tiktoken encoding."""
        try:
            self.encoding = tiktoken.get_encoding(encoding_name)
            self.encoding_name = encoding_name
        except ValueError as e:
            raise ValueError(f"Invalid encoding '{encoding_name}': {e}")
    
    def verify_round_trip(self, text: str) -> Dict[str, Any]:
        """
        Verify round-trip consistency: text -> tokens -> text -> tokens
        
        Returns:
            Dict with verification results including any detected issues
        """
        # First tokenization
        tokens1 = self.encoding.encode(text)
        
        # Decode back to text
        decoded_text = self.encoding.decode(tokens1)
        
        # Second tokenization of decoded text
        tokens2 = self.encoding.encode(decoded_text)
        
        # Check for inconsistencies
        round_trip_consistent = tokens1 == tokens2
        text_preserved = text == decoded_text
        
        return {
            "original_text": text,
            "decoded_text": decoded_text,
            "original_tokens": tokens1,
            "reencoded_tokens": tokens2,
            "round_trip_consistent": round_trip_consistent,
            "text_preserved": text_preserved,
            "has_issues": not (round_trip_consistent and text_preserved)
        }
    
    def analyze_token_boundaries(self, text: str) -> Dict[str, Any]:
        """
        Analyze how text is split into tokens and identify potential boundary issues.
        
        Returns:
            Analysis of tokenization boundaries and potential issues
        """
        tokens = self.encoding.encode(text)
        token_texts = []
        
        # Decode each token individually to see the boundaries
        for i, token in enumerate(tokens):
            try:
                token_text = self.encoding.decode([token])
                token_texts.append({
                    "token_id": token,
                    "token_text": token_text,
                    "position": i,
                    "repr": repr(token_text)
                })
            except Exception as e:
                token_texts.append({
                    "token_id": token,
                    "token_text": f"<ERROR: {e}>",
                    "position": i,
                    "repr": f"<ERROR: {e}>"
                })
        
        # Reconstruct text from individual tokens
        reconstructed = "".join([t["token_text"] for t in token_texts if not t["token_text"].startswith("<ERROR")])
        
        # Look for potential issues
        issues = []
        
        # Check for unexpected whitespace handling
        if text.strip() != reconstructed.strip() and text == reconstructed:
            issues.append("Whitespace handling differences detected")
        
        # Check for single characters being split unexpectedly
        single_char_tokens = [t for t in token_texts if len(t["token_text"]) == 1 and t["token_text"].isalnum()]
        if len(single_char_tokens) > len(text) * 0.3:  # Arbitrary threshold
            issues.append(f"High number of single-character tokens: {len(single_char_tokens)}")
        
        # Check for empty tokens
        empty_tokens = [t for t in token_texts if len(t["token_text"]) == 0]
        if empty_tokens:
            issues.append(f"Found {len(empty_tokens)} empty tokens")
        
        return {
            "original_text": text,
            "reconstructed_text": reconstructed,
            "token_count": len(tokens),
            "tokens": token_texts,
            "text_matches": text == reconstructed,
            "issues": issues,
            "has_issues": len(issues) > 0 or text != reconstructed
        }
    
    def find_problematic_substrings(self, text: str, min_length: int = 1, max_length: int = 10) -> List[Dict[str, Any]]:
        """
        Find substrings that might cause tokenization issues.
        
        Args:
            text: Text to analyze
            min_length: Minimum substring length to test
            max_length: Maximum substring length to test
            
        Returns:
            List of problematic substrings with details
        """
        problematic = []
        
        for start in range(len(text)):
            for length in range(min_length, min(max_length + 1, len(text) - start + 1)):
                substring = text[start:start + length]
                
                # Test this substring
                result = self.verify_round_trip(substring)
                boundary_result = self.analyze_token_boundaries(substring)
                
                if result["has_issues"] or boundary_result["has_issues"]:
                    problematic.append({
                        "substring": substring,
                        "start_pos": start,
                        "length": length,
                        "round_trip_issues": result["has_issues"],
                        "boundary_issues": boundary_result["has_issues"],
                        "round_trip_details": result,
                        "boundary_details": boundary_result
                    })
        
        return problematic
    
    def comprehensive_verification(self, text: str) -> Dict[str, Any]:
        """
        Run all verification checks on the given text.
        
        Returns:
            Comprehensive analysis results
        """
        round_trip = self.verify_round_trip(text)
        boundaries = self.analyze_token_boundaries(text)
        
        return {
            "text": text,
            "encoding": self.encoding_name,
            "round_trip_analysis": round_trip,
            "boundary_analysis": boundaries,
            "overall_has_issues": round_trip["has_issues"] or boundaries["has_issues"],
            "summary": self._generate_summary(round_trip, boundaries)
        }
    
    def _generate_summary(self, round_trip: Dict[str, Any], boundaries: Dict[str, Any]) -> List[str]:
        """Generate a human-readable summary of issues found."""
        summary = []
        
        if not round_trip["text_preserved"]:
            summary.append("❌ Text not preserved during tokenization round-trip")
        
        if not round_trip["round_trip_consistent"]:
            summary.append("❌ Token sequence not consistent across round-trip")
        
        if boundaries["issues"]:
            summary.extend([f"❌ {issue}" for issue in boundaries["issues"]])
        
        if not boundaries["text_matches"]:
            summary.append("❌ Reconstructed text doesn't match original")
        
        if not summary:
            summary.append("✅ No issues detected")
        
        return summary


def main():
    """CLI interface for the tokenizer verifier."""
    parser = argparse.ArgumentParser(description="Verify tiktoken tokenizer behavior")
    parser.add_argument("text", nargs="?", help="Text to verify (or read from stdin)")
    parser.add_argument("--encoding", default="cl100k_base", 
                       help="Tiktoken encoding to use (default: cl100k_base)")
    parser.add_argument("--find-substrings", action="store_true",
                       help="Find problematic substrings (slow for long texts)")
    parser.add_argument("--max-substring-length", type=int, default=10,
                       help="Maximum substring length to test (default: 10)")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Show detailed output")
    
    args = parser.parse_args()
    
    # Get text input
    if args.text:
        text = args.text
    else:
        print("Enter text to verify (Ctrl+D to finish):")
        text = sys.stdin.read()
    
    if not text.strip():
        print("No text provided")
        return 1
    
    try:
        verifier = TokenizerVerifier(args.encoding)
        
        # Run comprehensive verification
        result = verifier.comprehensive_verification(text)
        
        # Display results
        print(f"\n=== Tokenizer Verification Results ===")
        print(f"Encoding: {result['encoding']}")
        print(f"Text length: {len(result['text'])} characters")
        print(f"Token count: {result['boundary_analysis']['token_count']}")
        
        print(f"\n=== Summary ===")
        for item in result["summary"]:
            print(item)
        
        if args.verbose or result["overall_has_issues"]:
            print(f"\n=== Round-trip Analysis ===")
            rt = result["round_trip_analysis"]
            print(f"Text preserved: {rt['text_preserved']}")
            print(f"Tokens consistent: {rt['round_trip_consistent']}")
            
            if not rt["text_preserved"]:
                print(f"Original: {repr(rt['original_text'])}")
                print(f"Decoded:  {repr(rt['decoded_text'])}")
            
            if not rt["round_trip_consistent"]:
                print(f"Original tokens: {rt['original_tokens']}")
                print(f"Reencoded tokens: {rt['reencoded_tokens']}")
            
            print(f"\n=== Token Boundary Analysis ===")
            ba = result["boundary_analysis"]
            if ba["issues"]:
                for issue in ba["issues"]:
                    print(f"Issue: {issue}")
            
            if args.verbose:
                print(f"\nToken breakdown:")
                for token in ba["tokens"]:
                    print(f"  {token['token_id']:5d}: {token['repr']}")
        
        # Find problematic substrings if requested
        if args.find_substrings:
            print(f"\n=== Searching for Problematic Substrings ===")
            problematic = verifier.find_problematic_substrings(
                text, max_length=args.max_substring_length
            )
            
            if problematic:
                print(f"Found {len(problematic)} problematic substrings:")
                for item in problematic[:10]:  # Limit output
                    print(f"  '{item['substring']}' at position {item['start_pos']}")
                    if item['round_trip_issues']:
                        print(f"    - Round-trip issues")
                    if item['boundary_issues']:
                        print(f"    - Boundary issues")
                if len(problematic) > 10:
                    print(f"  ... and {len(problematic) - 10} more")
            else:
                print("No problematic substrings found")
        
        # Return exit code based on whether issues were found
        return 1 if result["overall_has_issues"] else 0
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    exit(main())