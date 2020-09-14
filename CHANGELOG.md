# Changelog

All notable changes to this project will be documented in this file. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 2.2.0

### Added in v2.2.0

- **Themes:** you can now apply a theme to your devices instead of a transition.

### Fixed in v2.2.0

- Recreate crontab on startup instead of reading existing crontab file.

### Changed in v2.2.0

- Updated to [Photons](https://github.com/delfick/photons) v0.30.0
- Switched from S6-overlay to Supercronic to reduce image size and memory consumption

## 2.1.0

### Added in v2.1.0

- Added the ability to set `transform_options` for each schedule.

### Changed in v2.1.0

- Minor formatting changes to various Markdown files to fix linting issues.

## 2.0.0

> **BREAKING CHANGES!**
> This release contains **breaking changes** since the 1.1.0 release. An existing `daydusk.json` configuration will no longer work.

- Switched to using YAML configuration to take advantage of the underlying Photons library validation capabilities
- A new `sample-daydusk.yml` is provided that matches the default Day & Dusk funtionality provided by LIFX
- Updated documentation for the new YAML format
- Bulbs can be specified on a per event basis in a far more flexible manner either within the configuration or via external files or filters.

### Added in v2.0.0

- Hue and saturation can be set for each event along with brightness and kelvin.
  Note that if hue and/or saturation are set to any value greater than `0`,
  the kelvin value is ignored.
- Events can be limited to specific days or will run on every day (default)

### Changed in v2.0.0

- Logging configuration modified so that only LIFX-related errors are logged.

## 1.1.0

### Added in v1.1.0

- Bulbs can now be targeted per event using `<event>-bulbs.conf` files.

### Removed in v1.1.0

- A work-in-progress script was committed accidentally and has been removed.

## 1.0.0

Initial stable release.

### Added in v1.0.0

- Basic LIFX Day & Dusk functionality
- Ability to specify target bulbs
- Ability to configure each transition, including power state
- Multi-arch image build support via Travis CI
- Manifest support on Docker Hub
