# unifi-protect-video-downloader
Tool to download footage from a local UniFi Protect system

### Usage

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
