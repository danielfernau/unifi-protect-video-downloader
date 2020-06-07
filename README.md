# UniFi Protect Video Downloader 

**Tool to download footage from a local UniFi Protect system**  

![GitHub release (latest by date)](https://img.shields.io/github/v/release/unifi-toolbox/unifi-protect-video-downloader?style=flat-square)
![GitHub Workflow Status](https://img.shields.io/github/workflow/status/unifi-toolbox/unifi-protect-video-downloader/Python%20package?style=flat-square)
![GitHub repo size](https://img.shields.io/github/repo-size/unifi-toolbox/unifi-protect-video-downloader?style=flat-square)
![GitHub stars](https://img.shields.io/github/stars/unifi-toolbox/unifi-protect-video-downloader?style=flat-square)
![Docker image size](https://img.shields.io/docker/image-size/unifitoolbox/protect-archiver/latest?style=flat-square)
![Docker pulls](https://img.shields.io/docker/pulls/unifitoolbox/protect-archiver?style=flat-square)
![License](https://img.shields.io/github/license/unifi-toolbox/unifi-protect-video-downloader?style=flat-square)


## :package: Releases

Latest release: https://github.com/unifi-toolbox/unifi-protect-video-downloader/releases/latest  
Docker image: https://hub.docker.com/r/unifitoolbox/protect-archiver  


## :arrow_right: Getting started

### For CloudKey-based Protect installations

`docker run --volume /path/on/host/machine:/downloads unifitoolbox/protect-archiver --help`

(replace `/path/on/host/machine` with an absolute path to your download directory and 
`--help` with one of the supported commands and its parameters as documented here: 
[wiki/Usage-(v2.x)](https://github.com/unifi-toolbox/unifi-protect-video-downloader/wiki/Usage-(v2.x)))

Example: `docker run --volume /path/on/host/machine:/downloads unifitoolbox/protect-archiver download [OPTIONS] /downloads`


### For UDM-based Protect installations

The `protect-archiver` can access UDM-based Protect installations by using [@Silvenga](https://github.com/Silvenga)'s 
[unifi-udm-api-proxy](https://github.com/Silvenga/unifi-udm-api-proxy).


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


## :link: Links

**Community post:**  
https://community.ui.com/questions/Tool-for-downloading-footage-from-UniFi-Protect/47057c1d-112b-4092-b488-a380286933df

**Reddit post:**  
https://www.reddit.com/r/Ubiquiti/comments/dhaxcq/tool_for_downloading_footage_from_unifi_protect/


## :warning: Important Information
This tool is neither supported nor endorsed by, and is in no way affiliated with Ubiquiti Inc.  
It is not guaranteed that it will always run flawlessly, so use this tool at your own risk.  
The software is provided without any warranty or liability, as stated in the [license](LICENSE).  
