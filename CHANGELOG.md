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



## [2.0.0] - 2020-04-06
### Added
- add Docker images for linux/amd64
([#24](https://github.com/danielfernau/unifi-protect-video-downloader/pull/24) by
[@danielfernau](https://github.com/danielfernau))
- add Dockerfile and Makefile
([d5e881b](https://github.com/danielfernau/unifi-protect-video-downloader/commit/d5e881b61b976fd8eea93329fec613483577ed80) by
[@danielfernau](https://github.com/danielfernau))
- add Poetry configuration 
([#10](https://github.com/danielfernau/unifi-protect-video-downloader/pull/10)
by [@dcramer](https://github.com/dcramer))
- add code formatting rules using Black
([#10](https://github.com/danielfernau/unifi-protect-video-downloader/pull/10) by
[@dcramer](https://github.com/dcramer))
- add tests
([#10](https://github.com/danielfernau/unifi-protect-video-downloader/pull/10) by
[@dcramer](https://github.com/dcramer))
- add support for Motion events
([#3](https://github.com/danielfernau/unifi-protect-video-downloader/issues/3) by
[@peteytoo](https://github.com/peteytoo) and
[#20](https://github.com/danielfernau/unifi-protect-video-downloader/pull/20) by
[@danielfernau](https://github.com/danielfernau))
- add option to download Motion event Heat Maps
([#20](https://github.com/danielfernau/unifi-protect-video-downloader/pull/20) by
[@danielfernau](https://github.com/danielfernau))
- add `sync` command for resuming downloads "rsync style"
([#5](https://github.com/danielfernau/unifi-protect-video-downloader/issues/5) by
[@purpleidea](https://github.com/purpleidea) and
[#18](https://github.com/danielfernau/unifi-protect-video-downloader/pull/18) by
[@dcramer](https://github.com/dcramer))
- add support for UDM-based installations using 
[@Silvenga/unifi-udm-api-proxy](https://github.com/Silvenga/unifi-udm-api-proxy)
([#27](https://github.com/danielfernau/unifi-protect-video-downloader/pull/27) by
[@danielfernau](https://github.com/danielfernau))
- add CI via GitHub Actions 
([adff6a8](https://github.com/danielfernau/unifi-protect-video-downloader/commit/adff6a804b30150799875ac33cd5bc83030ca4c5) by
[@dcramer](https://github.com/dcramer))

### Changed
- switch from GPLv3 to MIT License 
(as suggested in [#8](https://github.com/danielfernau/unifi-protect-video-downloader/issues/8) by
[@dcramer](https://github.com/dcramer))
- change API URL in get_camera_list function 
([#15](https://github.com/danielfernau/unifi-protect-video-downloader/issues/15) by
[@danielfernau](https://github.com/danielfernau))
- make video file names more readable 
([#23](https://github.com/danielfernau/unifi-protect-video-downloader/pull/23) by
[@danielfernau](https://github.com/danielfernau))
- change top level signature to be `protect-archiver download [--options] [dest]` 
([#10](https://github.com/danielfernau/unifi-protect-video-downloader/pull/10) by
[@dcramer](https://github.com/dcramer))
- replace accessKey authorization with Bearer Token Authorization header
([#20](https://github.com/danielfernau/unifi-protect-video-downloader/pull/20) by
[@danielfernau](https://github.com/danielfernau))
- update README to include more useful information, badges and links
([#28](https://github.com/danielfernau/unifi-protect-video-downloader/pull/28) by
[@danielfernau](https://github.com/danielfernau))

### Removed 
- remove download counting
([#10](https://github.com/danielfernau/unifi-protect-video-downloader/pull/10) by
[@dcramer](https://github.com/dcramer))
- remove auto-reauth on failure
([#10](https://github.com/danielfernau/unifi-protect-video-downloader/pull/10) by
[@dcramer](https://github.com/dcramer))


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
