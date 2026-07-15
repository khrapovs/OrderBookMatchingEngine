#!/bin/bash

# Run pytest benchmark. Results are saved in .benchmarks
pytest tests/test_matching_engine.py::TestMatchingEngine::test_matching_with_benchmark \
  -o addopts="" \
  --benchmark-enable \
  --benchmark-autosave \
  --benchmark-json=benchmark.json

# Compare saved results
pytest-benchmark compare --histogram=benchmark_history
