# UniFi Protect Video Downloader

**Tool to download footage from a local UniFi Protect system**

![GitHub release (latest by date)](https://img.shields.io/github/v/release/danielfernau/unifi-protect-video-downloader?style=flat-square&label=stable%20release)
![GitHub release (latest by date)](https://img.shields.io/github/v/release/danielfernau/unifi-protect-video-downloader?include_prereleases&sort=semver&style=flat-square&label=latest%20release)
![GitHub Workflow Status](https://img.shields.io/github/workflow/status/danielfernau/unifi-protect-video-downloader/Python%20package/master?style=flat-square)
![GitHub repo size](https://img.shields.io/github/repo-size/danielfernau/unifi-protect-video-downloader?style=flat-square)
![GitHub stars](https://img.shields.io/github/stars/danielfernau/unifi-protect-video-downloader?style=flat-square)
[![GitHub issues](https://img.shields.io/github/issues/danielfernau/unifi-protect-video-downloader?style=flat-square)](https://github.com/danielfernau/unifi-protect-video-downloader/issues)
![Docker image size](https://img.shields.io/docker/image-size/unifitoolbox/protect-archiver/latest?style=flat-square)
![Docker pulls](https://img.shields.io/docker/pulls/unifitoolbox/protect-archiver?style=flat-square)
![License](https://img.shields.io/github/license/danielfernau/unifi-protect-video-downloader?style=flat-square)
![Codecov](https://img.shields.io/codecov/c/github/danielfernau/unifi-protect-video-downloader?style=flat-square&token=QV50XU5J0O)


## :package: Releases

Releases: https://github.com/danielfernau/unifi-protect-video-downloader/releases  
Docker images: https://hub.docker.com/r/unifitoolbox/protect-archiver  

:file_folder: Version 1.x code: https://github.com/danielfernau/unifi-protect-video-downloader/tree/2165204442d30676f3f48ad445c0211c6e5c00c1


<!--
## :vertical_traffic_light: Compatibility

| UniFi Cloud Key | :white_check_mark: mostly stable |
| :---: | :---: |
| Firmware | >= 1.1.6 |
| Protect | >= 1.11.3 |


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
[wiki/Usage-(v2.x)](https://github.com/danielfernau/unifi-protect-video-downloader/wiki/Usage-(v2.x)))

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


### Finding cameras and choosing a stream per camera

Each camera records up to three video streams: High, Medium and Low. The `cameras` command lists
every camera with its ID, recording mode and streams:

```shell
docker run -it unifitoolbox/protect-archiver cameras --address 192.168.1.1 --username [USER]
```

```
Front door
  ID:         6a9eef70004eed03e40003f8
  Recording:  adaptive
  Streams:    0  High      2688x1512   30 fps    8.0 Mbps
              1  Medium     1280x720   30 fps    2.0 Mbps
              2  Low         640x360   15 fps    0.3 Mbps
```

Add `--json` for output a script can read.

By default, `download`, `events` and `sync` export the stream Protect picks (High). Use `--stream`
to choose one, by name or number, for every camera or per camera (by ID or name):

```shell
# Low for every camera
--stream low
# Medium for one camera, the rest unchanged
--stream "6a9eef70004eed03e40003f8=medium"
# High for the front door, Low for every other camera
--stream "low,Front door=high"
```

Files from a stream other than High get the stream's name in their file name, for example
`Front door (03f8) - 2024-01-01 - 09.00.00+0100 (Low).mp4`. A camera that doesn't have the stream
chosen for every camera keeps the default stream; a stream chosen for one camera must exist on it.

A camera only has footage of a stream for the times Protect recorded that stream. In *Adaptive*
recording mode, for example, Protect records the High stream only around motion and smart
detections, so a High export of an hour can be much shorter than an hour.

Protect doesn't always record every stream. When a stream wasn't recorded, Protect exports another
stream instead without reporting an error, so a file marked `(Medium)` can contain Low footage.
Check the resolution of a downloaded file if it matters. In Adaptive mode, for example, some systems
record only High and Low, and a Medium export returns the Low footage.


## :thought_balloon: Questions, ideas, support and more...

For everything that isn't a bug, issue or error, feel free to use the project's Discussions tab:  
https://github.com/danielfernau/unifi-protect-video-downloader/discussions


## :hammer_and_wrench: Development and Build Instructions

If you want to make changes, build you own version, test things or contribute to the project, you can find all the relevant Development and Build Instructions in the [BUILD.md](https://github.com/danielfernau/unifi-protect-video-downloader/blob/master/BUILD.md) file. Pull requests are welcome!


## :link: Links

**Community post:**  
https://community.ui.com/questions/Tool-for-downloading-footage-from-UniFi-Protect/47057c1d-112b-4092-b488-a380286933df

**Reddit post:**  
https://www.reddit.com/r/Ubiquiti/comments/dhaxcq/tool_for_downloading_footage_from_unifi_protect/



## :warning: Important Information
This tool is neither supported nor endorsed by, and is in no way affiliated with Ubiquiti Inc.  
It is not guaranteed that it will always run flawlessly, so use this tool at your own risk.  
The software is provided without any warranty or liability, as stated in the [license](LICENSE).  


