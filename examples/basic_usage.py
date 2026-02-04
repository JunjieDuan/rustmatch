"""
RustMatch Basic Usage Example
=============================

This example demonstrates the basic usage of RustMatch.
No numpy or pillow required!
"""
import rustmatch
import time
import os

# Get the images directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
IMAGES_DIR = os.path.join(PROJECT_DIR, "images")

SOURCE_IMAGE = os.path.join(IMAGES_DIR, "A.png")
TEMPLATE_IMAGE = os.path.join(IMAGES_DIR, "a3.png")


def main():
    print("=" * 60)
    print("RustMatch - Zero Dependency Template Matching")
    print("=" * 60)
    
    print(f"\nLibrary version: {rustmatch.version()}")
    
    # Get image info
    src_size = rustmatch.get_size(SOURCE_IMAGE)
    tpl_size = rustmatch.get_size(TEMPLATE_IMAGE)
    print(f"\nSource image: {src_size[0]}x{src_size[1]}")
    print(f"Template: {tpl_size[0]}x{tpl_size[1]}")
    
    # Example 1: Single match
    print("\n" + "-" * 40)
    print("Example 1: Find single best match")
    print("-" * 40)
    
    start = time.perf_counter()
    result = rustmatch.find(SOURCE_IMAGE, TEMPLATE_IMAGE, threshold=0.8)
    elapsed = (time.perf_counter() - start) * 1000
    
    if result:
        print(f"✓ Found match at ({result.x}, {result.y})")
        print(f"  Confidence: {result.confidence:.2%}")
        print(f"  Time: {elapsed:.2f}ms")
    else:
        print("✗ No match found")
    
    # Example 2: Multiple matches
    print("\n" + "-" * 40)
    print("Example 2: Find all matches")
    print("-" * 40)
    
    start = time.perf_counter()
    results = rustmatch.find_all(SOURCE_IMAGE, TEMPLATE_IMAGE, threshold=0.8, max_count=10)
    elapsed = (time.perf_counter() - start) * 1000
    
    print(f"✓ Found {len(results)} matches (Time: {elapsed:.2f}ms)")
    for i, r in enumerate(results[:5]):
        print(f"  {i+1}. ({r.x}, {r.y}) - {r.confidence:.2%}")
    if len(results) > 5:
        print(f"  ... and {len(results) - 5} more")
    
    # Example 3: Using bytes
    print("\n" + "-" * 40)
    print("Example 3: Match using image bytes")
    print("-" * 40)
    
    with open(SOURCE_IMAGE, "rb") as f:
        source_bytes = f.read()
    with open(TEMPLATE_IMAGE, "rb") as f:
        template_bytes = f.read()
    
    start = time.perf_counter()
    result = rustmatch.find_bytes(source_bytes, template_bytes, threshold=0.8)
    elapsed = (time.perf_counter() - start) * 1000
    
    if result:
        print(f"✓ Found match at ({result.x}, {result.y})")
        print(f"  Time: {elapsed:.2f}ms (excludes file I/O)")
    
    print("\n" + "=" * 60)
    print("Done! No numpy or pillow was needed.")
    print("=" * 60)


if __name__ == "__main__":
    main()
