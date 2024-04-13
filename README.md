# Cachyos-Deckify-Edition

Deckify Edition of CachyOS for Handhelds

ETA for a Handheld ISO May 2024.
This will include a own Calamares, adjusted Desktop and Scripts for proper Installation on Handhelds
We will provide only the Online Installation, so an internet connection will be mandatory.

Currently it is not planned to support more Bootloaders, but if there is any interest we can simply add them as in our default ISOs, for now we will default to systemd-boot.
There will be support for 5 different filesystems:

- xfs
- ext4
- btrfs (default)
- zfs
- bcachefs

There will be also automatic snapshotting implemented, to make it easy for users to rollback if they run into issues.
bcachefs could be generally a good idea for the Handhelds, but it is not fully ready yet and we don't suggest it for now.

## Features
- scx_lavd used as default scheduler - LAVD is a latency sensitive scheduler, which is intended to be used for handhelds and gaming
- Steam Deck like Steam Expierence
- Gamescope Session proper implemented 
- Kernel Patched to have support for Steam Deck OLED
- Steam Deck OLED Firmware included as default
- HDR correctly implemented via kerel patches
- All dependecies and packages bundled for a proper gaming expierence (cachyos-gaming-meta)
- Support for Winesync/Fastsync/NTSync (proton-cachyos provides a fastsync patched proton)
- BBRv3 used as default
- OpenRGB Patches included
- Screensharing for Discord (via xwaylandvideobridge)
- CachyOS Kernel
- CachyOS Repository (all packages compiled with avx2/avx512 including auto detection for cpu support)


## Planned
- Improve further the expierence to provide a Steam Deck Similar Expierence
- Provide the Steam Deck Themes
- Enhance Hardware Support


## Additonal Information

### How can I disable scx_lavd and use the BORE/EEVDF Scheduler?

This can be simply done with following:
```
sudo systemctl disable scx.service
sudo systemctl mask scx.service
```

## Credit to:
- ChimeraOS
- Ripplingsnake
- Manjaro (Phillip Müller for the base deckify package)
