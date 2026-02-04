# Contributing to RustMatch

Thank you for your interest in contributing to RustMatch!

## Development Setup

### Prerequisites

1. **Rust toolchain** (1.70+)
   ```bash
   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
   ```

2. **Python** (3.8+) with pip

3. **maturin** for building
   ```bash
   pip install maturin
   ```

### Clone and Build

```bash
git clone https://github.com/JunjieDuan/rustmatch.git
cd rustmatch

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install development dependencies
pip install -e ".[dev]"

# Build the Rust extension
maturin develop --release
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=rustmatch

# Run benchmarks
pytest tests/test_benchmark.py --benchmark-only
```

## Code Style

### Rust

- Follow standard Rust formatting (`cargo fmt`)
- Run clippy for lints (`cargo clippy`)
- Document public APIs with doc comments

### Python

- Follow PEP 8
- Use type hints
- Format with ruff (`ruff format`)

## Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Update documentation if needed
7. Commit with clear messages
8. Push and create a Pull Request

## Reporting Issues

When reporting bugs, please include:
- Python version
- Operating system
- Minimal reproduction code
- Expected vs actual behavior

## License

By contributing, you agree that your contributions will be licensed under the MIT/Apache-2.0 dual license.
