# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
> TODO


## [2.0.2] - 2021-05-09
### Changed
- improve console output of 'events' command ([#51](https://github.com/danielfernau/unifi-protect-video-downloader/pull/51))

### Fixed
- fix 'sync' command not working with updated 'ProtectClient' ([#50](https://github.com/danielfernau/unifi-protect-video-downloader/pull/50))


## [2.0.1] - 2020-05-02
### Added
- add Docker images for linux/arm64
- add support for Protect servers running on UniFi OS


## [2.0.0-beta] - 2020-04-06
### Added
- add Docker images for linux/amd64

> TODO


## [1.1.1] - 2019-11-30
### Fixed
- fix "First time range is negative if start time doesn't start at 0 minutes" ([#2](https://github.com/danielfernau/unifi-protect-video-downloader/issues/2))


## [1.1.0] - 2019-11-09
### Added
- add option to download `.jpg` snapshots using `--snapshot` (see README)
- add exit code `6` to indicate that either the `--snapshot` or the `--start` and `--end` command line arguments are missing

### Changed
- use `dateutil.parser` instead of `datetime.strptime` to parse start and end timestamps
- use `timestamp()` instead of `strftime("%s")` to get unix timestamp


## [1.0.0] - 2019-11-09
### Added
- main.py
- requirements.txt
- README
- LICENSE
