.PHONY: build dev test bench lint fmt clean docs publish

# Development build
dev:
	maturin develop --release

# Release build
build:
	maturin build --release

# Run tests
test:
	pytest tests/ -v

# Run benchmarks
bench:
	pytest tests/test_benchmark.py --benchmark-only

# Lint Rust code
lint:
	cargo fmt --check
	cargo clippy -- -D warnings

# Format code
fmt:
	cargo fmt
	ruff format python/

# Clean build artifacts
clean:
	cargo clean
	rm -rf dist/ build/ *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.so" -delete
	find . -type f -name "*.pyd" -delete

# Build documentation
docs:
	cd docs && sphinx-build -b html . _build/html

# Publish to PyPI (requires authentication)
publish:
	maturin publish
