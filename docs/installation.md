# Installation

## From PyPI

The easiest way to install RustMatch:

```bash
pip install rustmatch
```

**Zero dependencies!** No numpy or pillow required.

Pre-built wheels are available for:
- Linux (x86_64, aarch64)
- macOS (x86_64, arm64)
- Windows (x86_64)

## From Source

Building from source requires the Rust toolchain.

### Prerequisites

1. **Install Rust**:
   ```bash
   # Linux/macOS
   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
   
   # Windows
   # Download from https://rustup.rs
   ```

2. **Install maturin**:
   ```bash
   pip install maturin
   ```

### Build Steps

```bash
# Clone repository
git clone https://github.com/JunjieDuan/rustmatch.git
cd rustmatch

# Development build
maturin develop --release

# Or build wheel
maturin build --release
pip install target/wheels/rustmatch-*.whl
```

## Dependencies

### Required
- Python >= 3.8
- Rust >= 1.70 (for building from source only)

### Optional (for development)
- pytest >= 7.0.0
- pillow >= 9.0.0 (for testing only)

## Verifying Installation

```python
import rustmatch

print(rustmatch.version())  # Should print version number

# Quick test with file paths
result = rustmatch.find("source.png", "template.png")
print(f"Match found: {result is not None}")
```

## Troubleshooting

### ImportError: DLL not found (Windows)

Install Visual C++ Redistributable:
- Download from [Microsoft](https://aka.ms/vs/17/release/vc_redist.x64.exe)

### Rust compilation errors

Ensure you have the latest Rust:
```bash
rustup update stable
```
