### protect-archiver events

```text
Usage: protect-archiver events [OPTIONS] DEST

  Download event recordings from UniFi Protect to a local destination

Options:
  --address TEXT                  IP address or hostname of the UniFi Protect
                                  Server  [default: unifi; required]

  --not-unifi-os                  Use this for systems without UniFi OS
                                  [default: False]

  --username TEXT                 Username of user with local access
                                  [required]

  --password TEXT                 Password of user with local access
                                  [required]

  --verify-ssl                    Verify Protect SSL certificate  [default:
                                  False]

  --cameras TEXT                  Comma-separated list of one or more camera
                                  IDs ('--cameras="id_1,id_2,id_3,..."'). Use
                                  '--cameras=all' to download footage of all
                                  available cameras.  [default: all]

  --wait-between-downloads INTEGER
                                  Time to wait between file downloads, in
                                  seconds  [default: 0]

  --ignore-failed-downloads       Ignore failed downloads and continue with
                                  next download  [default: False]

  --skip-existing-files           Skip downloading files which already exist
                                  on disk  [default: False]

  --touch-files                   Create local file without content for
                                  current download - useful in combination
                                  with '--skip-existing-files' to skip
                                  problematic segments  [default: False]

  --use-subfolders / --no-use-subfolders
                                  Save footage to folder structure with format
                                  'YYYY/MM/DD/camera_name/'  [default: True]

  --download-request-timeout FLOAT
                                  Time to wait before aborting download
                                  request, in seconds  [default: 60.0]

  --start [%Y-%m-%d|%Y-%m-%dT%H:%M:%S|%Y-%m-%d %H:%M:%S|%Y-%m-%d %H:%M:%S%z]
                                  Download range start time.   [required]
  --end [%Y-%m-%d|%Y-%m-%dT%H:%M:%S|%Y-%m-%d %H:%M:%S|%Y-%m-%d %H:%M:%S%z]
                                  Download range end time.   [required]
  --download-motion-heatmaps      Also download motion heatmaps for event
                                  recordings  [default: False]

  --help                          Show this message and exit.
```
