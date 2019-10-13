# UniFi Protect Video Downloader
Tool to download footage from a local UniFi Protect system

---

##### Important Information
This tool is neither supported nor endorsed by, and is in no way affiliated with Ubiquiti.  
It is not guaranteed that it will always run flawlessly, so use this tool at your own risk.  
The software is provided without any warranty or liability, as stated in sections 15 and 16 of the [license](LICENSE).  

---

### Installation
#### Requirements
- git
- python3
- python3-pip

#### Download  
`git clone git@github.com:danielfernau/unifi-protect-video-downloader.git`

#### Enter project folder  
`cd unifi-protect-video-downloader`

#### Install modules  
`pip3 install -r requirements.txt`

---

### Usage
#### General
1. add a new local user to the UniFi Protect system
    - open https://\<cloud-key-ip\>:7443/ in your browser
    - log in with an administrator account
    - go to "Users"
    - click on "Invite User"
    - select _Invite Type_ "Local Access Only"
    - enter _Local Username_ and _Local Password_ for the new user
    - select the default _View Only_ role
    - click "Add User"
    
2. run the script with the login information of the newly created user (see example below)

#### Example  
`python3 main.py --address=10.100.0.1 --username="local_user" --password="local_user_password" --cameras="all" --start="2019-10-12 00:00:00+0200" --end="2019-10-13 00:00:00+0200" --dest=./download --skip-existing-files --touch-files --use-subfolders`

#### Command line arguments
```
usage: main.py [-h] --address ADDRESS [--port PORT] [--verify-ssl] --username
               USERNAME --password PASSWORD --cameras CAMERA_IDS
               [--channel CHANNEL] --start START --end END
               [--dest DESTINATION_PATH]
               [--wait-between-downloads DOWNLOAD_WAIT]
               [--downloads-before-key-refresh MAX_DOWNLOADS_WITH_KEY]
               [--downloads-before-auth-refresh MAX_DOWNLOADS_WITH_AUTH]
               [--ignore-failed-downloads] [--skip-existing-files]
               [--touch-files] [--use-subfolders]
               [--download-request-timeout DOWNLOAD_TIMEOUT]

Tool to download footage from a local UniFi Protect system

optional arguments:
  -h, --help            show this help message and exit
  --address ADDRESS     CloudKey IP address or hostname
  --port PORT           UniFi Protect service port
  --verify-ssl          Verify CloudKey SSL certificate
  --username USERNAME   Username of user with local access
  --password PASSWORD   Password of user with local access
  --cameras CAMERA_IDS  Comma-separated list of one or more camera IDs ('--
                        cameras="id_1,id_2,id_3,..."'). Use '--cameras=all' to
                        download footage of all available cameras.
  --channel CHANNEL     Channel
  --start START         Start time in format "YYYY-MM-DD HH:MM:SS+0000"
  --end END             End time in format "YYYY-MM-DD HH:MM:SS+0000"
  --dest DESTINATION_PATH
                        Destination directory path
  --wait-between-downloads DOWNLOAD_WAIT
                        Time to wait between file downloads, in seconds
                        (Default: 0)
  --downloads-before-key-refresh MAX_DOWNLOADS_WITH_KEY
                        Maximum number of downloads with the same API Access
                        Key (Default: 3)
  --downloads-before-auth-refresh MAX_DOWNLOADS_WITH_AUTH
                        Maximum number of downloads with the same API
                        Authentication Token (Default: 10)
  --ignore-failed-downloads
                        Ignore failed downloads and continue with next
                        download (Default: False)
  --skip-existing-files
                        Skip downloading files which already exist on disk
                        (Default: False)
  --touch-files         Create local file without content for current download
                        (Default: False) - useful in combination with '--skip-
                        existing-files' to skip problematic segments
  --use-subfolders      Save footage to folder structure with format
                        'YYYY/MM/DD/camera_name/' (Default: False)
  --download-request-timeout DOWNLOAD_TIMEOUT
                        Time to wait before aborting download request, in
                        seconds (Default: 60)
```

---

### How the program works (simplified)
1. Check if all required parameters are set
2. Check if local target directory exists
3. POST to **/api/auth** with _username_ and _password_ to retrieve API Bearer Token
4. POST to **/api/auth/access-key** with _Bearer Token Authorization header_ to retrieve API Access Key
5. GET from **/api/bootstrap** with _Bearer Token Authorization header_ to retrieve camera list
6. Split the given time range into one-hour segments to prevent too large files
7. GET video segments from **/api/video/export** using _accessKey_, _camera_, _start_, _end_ parameters

---

### How the API for video downloads works (simplified)
1. POST to **/api/auth** with JSON payload `{"username": "your_username", "password":"your_password"}``
    - returns status code 401 if credentials are wrong
    - returns status code 200, some JSON data with information about the authenticated user and an _Authorization_ header containing an OAuth Bearer Token
2. POST to **/api/auth/access-key** with _Authorization_ header containing the previously requested Bearer Token
    - returns status code 401 if token is invalid
    - returns status code 200 and JSON data containing the _accessKey_
3. GET from **/api/bootstrap**  with _Authorization_ header containing the previously requested Bearer Token
    - returns status code 401 if token is invalid / user is not authorized
    - returns status code 200 and JSON data with information about the system, the cameras, etc.
4. GET from **/api/video/export** with parameters `?accessKey=<the_access_key>&camera=<camera_id>&start=<segment_start_as_unix_time_in_milliseconds>&end=<segment_end_as_unix_time_in_milliseconds>`
    - returns a video file containing the available footage within the requested time frame in `.mp4` format
    - additional optional parameters include `channel=<channel_id>`, `filename=<output_filename.mp4>`, ...

---

### Software Credits
The development of this software was made possible using the following components:  
  
Certifi by Kenneth Reitz  
Licensed Under: Mozilla Public License 2.0  
https://pypi.org/project/certifi/  
  
Chardet by Daniel Blanchard  
Licensed Under: GNU Library or Lesser General Public License (LGPL)  
https://pypi.org/project/chardet/  
  
IDNA by Kim Davies  
Licensed Under: BSD License (BSD-like)  
https://pypi.org/project/idna/  
  
Requests by Kenneth Reitz  
Licensed Under: Apache Software License (Apache 2.0)  
https://pypi.org/project/requests/  
  
urllib3 by Andrey Petrov  
Licensed Under: MIT License (MIT)  
https://pypi.org/project/urllib3/  
