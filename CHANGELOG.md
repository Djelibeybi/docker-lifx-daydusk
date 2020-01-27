# Changelog

All notable changes to this project will be documented in this file. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Develop branch

### Added
 - Hue and saturation can be set for each event along with brightness and kelvin.<br>Note that if hue and/or saturation are set to anything except `0`, the kelvin value is ignored.
 - Events can be limited to specific days or will run on every day (default) 

## 1.1.0

### Added
 - Bulbs can now be targeted per event using `<event>-bulbs.conf` files.
### Removed
 - A work-in-progress script was committed accidentally and has been removed.

## 1.0.0
Initial stable release.

### Added
 - Basic LIFX Day & Dusk functionality
 - Ability to specify target bulbs 
 - Ability to configure each transition, including power state
 - Multi-arch image build support via Travis CI
 - Manifest support on Docker Hub
