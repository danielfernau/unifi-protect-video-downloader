# Welcome to the unifi-protect-video-downloader documentation!

---

# UniFi Protect Video Downloader

First of all, thank you for your interest in this project! Over the past few years, I have developed and maintained it,
together with the help of a small group
of [contributors](https://github.com/danielfernau/unifi-protect-video-downloader/graphs/contributors), aiming to provide
users in the UniFi Protect ecosystem with some additional features that can commonly be found in many other enterprise
surveillance systems. Some of us have just a single camera at home to keep an eye on their pets, others use it to
protect their businesses using dozens of cameras. And no matter which of these scenarios (or anything in between) might
apply to you, it is highly likely that you came across this tool because you need an automated way to archive, export,
or back up your recordings and store or share them outside your UniFi console.

The reason why this project (still) exists is twofold:

On the one hand, as of mid-2023, including the 2.8.x versions, there is no way to automatically download footage from
multiple cameras at once, within a specified date and time range, using the web interface. However, being able to do so
can be highly valuable when you need to download recordings from multiple or all cameras connected to the system for a
specific time range, such as capturing an event, archiving it for later reference, or providing it to a security company
or law enforcement.

On the other hand, the UniFi Protect system does not officially provide any methods to interact with the system or
easily back up recordings, apart from using the web interface or mobile apps. Therefore, this program utilizes the same
API used by the web interface and mobile apps to access settings and recordings. It's important to note that the API is
not an officially documented method for interacting with the UniFi Protect system. As a result, it is subject to change
across different versions and may not have official support. Any updates to the Protect app on the UniFi console could
potentially render this tool inoperable until an update is provided. If you rely on this tool in any way (after ensuring
that it suits your specific use case - as the software is provided "as-is," without any warranty, as stated in the
[LICENSE](https://github.com/danielfernau/unifi-protect-video-downloader/blob/master/LICENSE) file of the project), it
is advisable to test your desired combination of Protect/Downloader versions on a staging system (such as a separate
UniFi Protect setup that is not critical) before upgrading your important setup(s).

This project is written in Python 2.x and the CI/CD conveniently bundles everything into a Docker image, eliminating the
need for manual installation of Python packages and dependencies. This way, you can quickly get started using the tool
to download footage from your UniFi console.

---

Latest release: https://github.com/danielfernau/unifi-protect-video-downloader/releases/latest

---

Community post:  
https://community.ui.com/questions/Tool-for-downloading-footage-from-UniFi-Protect/47057c1d-112b-4092-b488-a380286933df

Reddit post:  
https://www.reddit.com/r/Ubiquiti/comments/dhaxcq/tool_for_downloading_footage_from_unifi_protect/

---

##### Important Information

This tool is neither supported nor endorsed by, and is in no way affiliated with Ubiquiti Inc.  
It is not guaranteed that it will always run flawlessly, so use this tool at your own risk.  
The software is provided without any warranty or liability, as stated in
the [LICENSE](https://github.com/danielfernau/unifi-protect-video-downloader/blob/master/LICENSE).  