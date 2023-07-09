### protect-archiver sync

```text
Usage: protect-archiver sync [OPTIONS] DEST

  Synchronize your UniFi Protect footage to a local destination

Options:
  --address TEXT             CloudKey IP address or hostname  [default: unifi;
                             required]

  --port INTEGER             UniFi Protect service port  [default: 7443]
  --username TEXT            Username of user with local access  [required]
  --password TEXT            Password of user with local access  [required]
  --statefile TEXT           [default: sync.state]
  --ignore-state             [default: False]
  --verify-ssl               Verify CloudKey SSL certificate  [default: False]
  --ignore-failed-downloads  Ignore failed downloads and continue with next
                             download  [default: False]

  --cameras TEXT             Comma-separated list of one or more camera IDs ('
                             --cameras="id_1,id_2,id_3,..."'). Use '--
                             cameras=all' to download footage of all available
                             cameras.  [default: all]

  --help                     Show this message and exit.
```
