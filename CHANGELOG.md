# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [v0.1.3] - 2026-01-21

### Added

- `__init__(self, **kwargs)` constructor added to `ExecutionHandler` with automatic attribute assignment for `job_id`, `outputs`, and `results`
- New `set_job_id(job_id)` method on `ExecutionHandler` for runtime job ID assignment

### Changed

- Package version is now dynamically retrieved from package metadata instead of being hardcoded in `__init__.py`
- Graceful fallback to `"unknown"` if package metadata is unavailable

## [v0.1.2] - 2026-01-19

### Added

- Created `zoo_runner_common/` package directory with proper `__init__.py` and explicit exports

### Changed

- Moved all modules (`base_runner.py`, `handlers.py`, `zoo_conf.py`, `zoostub.py`) into `zoo_runner_common/` package directory
- All imports updated to use package-style: `from zoo_runner_common import ...`
- Updated `pyproject.toml` with `setuptools.packages.find` configuration, switching from `py-modules` to package-based discovery

### Removed

- Root-level `__init__.py` removed for cleaner structure

## [v0.1.1] - 2026-01-18

### Added

- Added PyPI classifiers: Development Status (Beta), License, Python 3.10/3.11/3.12 support, Audience, Topic
- Added keywords: `zoo-project`, `cwl`, `runner`, `workflow`, `ogc`, `api`, `processes`
- Added project URLs for Homepage, Documentation, Issues, and Changelog
- Added Gérald Fenoy as co-author

### Changed

- License updated from BSD-3-Clause to Apache-2.0 for consistency across the ZOO-Project ecosystem

## [v0.1.0] - 2026-01-18

### Added

- Initial release of `zoo-runner-common` as a standalone Python package
- `BaseRunner` with 8+ shared methods: `get_workflow_id()`, `get_workflow_inputs()`, `get_max_cores()`, `get_max_ram()`, `get_volume_size()`, `assert_parameters()`, `get_processing_parameters()`, `get_namespace_name()`, `finalize()`
- New `ExecutionHandler` abstract class (`handlers.py`) with hooks: `pre_execution_hook()`, `post_execution_hook()`, `get_secrets()`, `get_pod_env_vars()`, `get_pod_node_selector()`, `handle_outputs()`, `get_additional_parameters()`
- `ZooConf` improvements: support for complex types (arrays, OGC bbox), NULL value handling, multiple file formats, CWL v1.2 parsing, scatter operation support
- `ZooStub` extended with all ZOO status codes (ACCEPTED, STARTED, PAUSED, DEPLOYED, etc.) and structured logging via `loguru`
- `loguru>=0.7.0` added as a dependency
- MkDocs Material documentation site with getting started guide, user guide, API reference, and developer guide
- GitHub Actions workflow for automatic documentation deployment to GitHub Pages
- GitHub Actions workflow for automated PyPI publishing on release with Trusted Publishing support
- `ruff.toml` configuration for linting (pycodestyle, pyflakes, isort, pyupgrade)
- Complete `.gitignore` for Python projects

[Unreleased]: https://github.com/ZOO-Project/zoo-runner-common/compare/v0.1.3...HEAD
[v0.1.3]: https://github.com/ZOO-Project/zoo-runner-common/compare/v0.1.2...v0.1.3
[v0.1.2]: https://github.com/ZOO-Project/zoo-runner-common/compare/v0.1.1...v0.1.2
[v0.1.1]: https://github.com/ZOO-Project/zoo-runner-common/compare/v0.1.0...v0.1.1
[v0.1.0]: https://github.com/ZOO-Project/zoo-runner-common/releases/tag/v0.1.0