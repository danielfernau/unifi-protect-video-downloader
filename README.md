# UniFi Protect Video Downloader

**Tool to download footage from a local UniFi Protect system**

![GitHub release (latest by date)](https://img.shields.io/github/v/release/unifi-toolbox/unifi-protect-video-downloader?style=flat-square&label=stable%20release)
![GitHub release (latest by date)](https://img.shields.io/github/v/release/unifi-toolbox/unifi-protect-video-downloader?include_prereleases&sort=semver&style=flat-square&label=latest%20release)
![GitHub Workflow Status](https://img.shields.io/github/workflow/status/unifi-toolbox/unifi-protect-video-downloader/Python%20package/master?style=flat-square)
![GitHub repo size](https://img.shields.io/github/repo-size/unifi-toolbox/unifi-protect-video-downloader?style=flat-square)
![GitHub stars](https://img.shields.io/github/stars/unifi-toolbox/unifi-protect-video-downloader?style=flat-square)
[![GitHub issues](https://img.shields.io/github/issues/unifi-toolbox/unifi-protect-video-downloader?style=flat-square)](https://github.com/unifi-toolbox/unifi-protect-video-downloader/issues)
![Docker image size](https://img.shields.io/docker/image-size/unifitoolbox/protect-archiver/latest?style=flat-square)
![Docker pulls](https://img.shields.io/docker/pulls/unifitoolbox/protect-archiver?style=flat-square)
![License](https://img.shields.io/github/license/unifi-toolbox/unifi-protect-video-downloader?style=flat-square)
![Codecov](https://img.shields.io/codecov/c/github/unifi-toolbox/unifi-protect-video-downloader?style=flat-square&token=QV50XU5J0O)


## :package: Releases

Releases: https://github.com/unifi-toolbox/unifi-protect-video-downloader/releases  
Docker images: https://hub.docker.com/r/unifitoolbox/protect-archiver  

:file_folder: Version 1.x code: https://github.com/unifi-toolbox/unifi-protect-video-downloader/tree/2165204442d30676f3f48ad445c0211c6e5c00c1


<!--
## :vertical_traffic_light: Compatibility

| UniFi Cloud Key | :white_check_mark: mostly stable |
| :---: | :---: |
| Firmware | >= 1.1.6 |
| Protect | >= 1.11.3 |


| UniFi Dream Machine Pro | :warning: experimental/beta |
| :---: | :---: |
| Firmware | >= v1.7.0 |
| Protect | >= v1.14.10 |
-->


## :arrow_right: Getting started

### For Protect servers with UniFi OS

```shell
docker run --volume /path/on/host/machine:/downloads unifitoolbox/protect-archiver --help
```

(replace `/path/on/host/machine` with an absolute path to your download directory and
`--help` with one of the supported commands and its parameters as documented here:
[wiki/Usage-(v2.x)](https://github.com/unifi-toolbox/unifi-protect-video-downloader/wiki/Usage-(v2.x)))

Example:
```shell
docker run --volume /path/on/host/machine:/downloads unifitoolbox/protect-archiver download [OPTIONS] /downloads
```


### For Protect systems with older firmware

To use the tool with older systems, just add the `--not-unifi-os` flag to your options list.

Example:
```shell
docker run --volume /path/on/host/machine:/downloads unifitoolbox/protect-archiver download --not-unifi-os [OPTIONS] /downloads
```


## :thought_balloon: Questions, ideas, support and more...

For everything that isn't a bug, issue or error, feel free to use the project's Discussions tab:  
https://github.com/unifi-toolbox/unifi-protect-video-downloader/discussions


## :hammer_and_wrench: Development and Build Instructions

If you want to make changes, build you own version, test things or contribute to the project, you can find all the relevant Development and Build Instructions in the [BUILD.md](https://github.com/unifi-toolbox/unifi-protect-video-downloader/blob/master/BUILD.md) file. Pull requests are welcome!


## :link: Links

**Community post:**  
https://community.ui.com/questions/Tool-for-downloading-footage-from-UniFi-Protect/47057c1d-112b-4092-b488-a380286933df

**Reddit post:**  
https://www.reddit.com/r/Ubiquiti/comments/dhaxcq/tool_for_downloading_footage_from_unifi_protect/



## :warning: Important Information
This tool is neither supported nor endorsed by, and is in no way affiliated with Ubiquiti Inc.  
It is not guaranteed that it will always run flawlessly, so use this tool at your own risk.  
The software is provided without any warranty or liability, as stated in the [license](LICENSE).  
