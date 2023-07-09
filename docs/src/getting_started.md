# Getting started

Running this tool directly on your UniFi console is theoretically possible, but it is neither recommended nor tested.
Instead, it is advisable to use a separate system such as a server, NAS, or PC. Keep in mind your network setup,
including firewall and other network restrictions, to ensure successful connection to your UniFi console. To verify if
the tool can establish a connection, try accessing the console's web interface through either the command-line
interface (CLI) or a web browser installed on the same machine. If you can reach the console's web interface, it
indicates that the tool should be able to establish a connection. Refer to the 'Troubleshooting/Connectivity Check'
section for additional instructions.

## Using Docker (recommended)

> Refer to [this documentation](https://docs.docker.com/get-docker/) on how to set up Docker on your machine.
> 
> If you prefer to use Podman, you can find the installation instructions [here](https://podman.io/docs/installation).
> 
> A collection of hints related to using this tool's Docker image can be found under the `FAQ/Docker` section.

### For downloading clips from consoles running UniFi OS

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

### For downloading clips from consoles with older firmware (<= v?.?.?)

To use the tool with older systems, just add the `--not-unifi-os` flag to your options list.

Example:

```shell
docker run --volume /path/on/host/machine:/downloads unifitoolbox/protect-archiver download --not-unifi-os [OPTIONS] /downloads
```
