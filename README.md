# UniFi Protect Video Downloader 

**Tool to download footage from a local UniFi Protect system**  

![GitHub release (latest by date)](https://img.shields.io/github/v/release/unifi-toolbox/unifi-protect-video-downloader?style=flat-square&label=stable)
![GitHub release (latest by date)](https://img.shields.io/github/v/release/unifi-toolbox/unifi-protect-video-downloader?include_prereleases&sort=semver&style=flat-square&label=beta)
![GitHub Workflow Status](https://img.shields.io/github/workflow/status/unifi-toolbox/unifi-protect-video-downloader/Python%20package/v2.0.0?style=flat-square&label=build%20(v2.0.0))
![GitHub repo size](https://img.shields.io/github/repo-size/unifi-toolbox/unifi-protect-video-downloader?style=flat-square)
![GitHub stars](https://img.shields.io/github/stars/unifi-toolbox/unifi-protect-video-downloader?style=flat-square)
![Docker image size](https://img.shields.io/docker/image-size/unifitoolbox/protect-archiver/latest?style=flat-square)
![Docker pulls](https://img.shields.io/docker/pulls/unifitoolbox/protect-archiver?style=flat-square)
![License](https://img.shields.io/github/license/unifi-toolbox/unifi-protect-video-downloader?style=flat-square)



## :package: Releases

Releases: https://github.com/unifi-toolbox/unifi-protect-video-downloader/releases  
Docker images: https://hub.docker.com/r/unifitoolbox/protect-archiver  

:file_folder: Version 1.x code: https://github.com/unifi-toolbox/unifi-protect-video-downloader/tree/2165204442d30676f3f48ad445c0211c6e5c00c1



## :vertical_traffic_light: Compatibility  

| UniFi Cloud Key | :white_check_mark: mostly stable |
| :---: | :---: |
| Firmware | >= 1.1.6 |
| Protect | >= 1.11.3 |


| UniFi Dream Machine Pro | :warning: experimental/beta |  
| :---: | :---: |  
| Firmware | >= v1.7.0 |  
| Protect | >= v1.14.10 |  



## :arrow_right: Getting started

### For Cloud Key-based Protect installations

`docker run --volume /path/on/host/machine:/downloads unifitoolbox/protect-archiver --help`

(replace `/path/on/host/machine` with an absolute path to your download directory and 
`--help` with one of the supported commands and its parameters as documented here: 
[wiki/Usage-(v2.x)](https://github.com/unifi-toolbox/unifi-protect-video-downloader/wiki/Usage-(v2.x)))

Example: `docker run --volume /path/on/host/machine:/downloads unifitoolbox/protect-archiver download [OPTIONS] /downloads`


### For UDM-based Protect installations

The `protect-archiver` can access UDM-based Protect installations by using [@Silvenga](https://github.com/Silvenga)'s 
[unifi-udm-api-proxy](https://github.com/Silvenga/unifi-udm-api-proxy).  

:warning: This is only a work-around for now and might not always function as expected. There are known issues due to differences between CloudKey and UDM in terms of the APIs and authentication methods. We're aleady working on improving the session/authentication part of the software.

#### Download the project files

`git clone https://github.com/unifi-toolbox/unifi-protect-video-downloader.git`  
or  
`git clone git@github.com:unifi-toolbox/unifi-protect-video-downloader.git`


#### Start the UniFi UDM API Proxy

**Enter the project directory**  

`cd unifi-protect-video-downloader`
  
**Start the proxy**  

`UDM_URI=https://192.168.0.1 docker-compose up -d`  

(replace `192.168.0.1` with the IP address of your UDM)

_Hint:_ To stop the UniFi UDM API Proxy, run `docker-compose down` from within the project directory.


#### Run the protect-archiver
`docker run --network=unifi-protect-video-downloader_default --volume /path/on/host/machine:/downloads unifitoolbox/protect-archiver --help`

(replace `/path/on/host/machine` with an absolute path to your download directory and 
`--help` with one of the supported commands and its parameters as documented here: 
[wiki/Usage-(v2.x)](https://github.com/unifi-toolbox/unifi-protect-video-downloader/wiki/Usage-(v2.x)). The API proxy's address/hostname is `unifi-udm-api-proxy`.)

Example: `docker run --network=unifi-protect-video-downloader_default --volume /path/on/host/machine:/downloads unifitoolbox/protect-archiver download --address="unifi-udm-api-proxy" [OPTIONS] /downloads`

## :thought_balloon: Questions, ideas, support and more...

For everything that isn't a bug, issue or error, feel free to use the project's Discussions tab:  
https://github.com/unifi-toolbox/unifi-protect-video-downloader/discussions


## :link: Links

**Community post:**  
https://community.ui.com/questions/Tool-for-downloading-footage-from-UniFi-Protect/47057c1d-112b-4092-b488-a380286933df

**Reddit post:**  
https://www.reddit.com/r/Ubiquiti/comments/dhaxcq/tool_for_downloading_footage_from_unifi_protect/



## :warning: Important Information
This tool is neither supported nor endorsed by, and is in no way affiliated with Ubiquiti Inc.  
It is not guaranteed that it will always run flawlessly, so use this tool at your own risk.  
The software is provided without any warranty or liability, as stated in the [license](LICENSE).  
