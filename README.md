# Cachyos-Handheld-Edition

Handheld Edition of CachyOS

This will include our own calamares, adjusted desktop and scripts for proper installation on handhelds.
We will provide only the online installation, so an internet connection will be mandatory.

Currently it is not planned to support more bootloaders, but if there is any interest we can simply add them as in our default ISOs, for now we will default to systemd-boot.
There will be support for 5 different filesystems:

- xfs
- ext4
- btrfs (default)
- zfs
- bcachefs

There will also be automatic snapshotting implemented, to make it easy for users to rollback if they run into issues.
Bcachefs could be generally a good idea for handhelds, but it is not fully ready yet and we don't suggest it for now.

## Features
- scx_lavd used as default scheduler - LAVD is a latency sensitive scheduler, which is intended to be used for handhelds and gaming
- Steam Deck like Steam Expierence
- Gamescope Session properly implemented 
- Kernel Patched to have support for Steam Deck OLED
- Steam Deck OLED Firmware included as default
- HDR correctly implemented via kernel patches
- All dependecies and packages bundled for a proper gaming expierence (cachyos-gaming-meta)
- Support for Winesync/Fastsync/NTSync
- BBRv3 used as default
- OpenRGB Patches included
- Screensharing for Discord (via xwaylandvideobridge)
- CachyOS Kernel
- CachyOS Repository (all packages compiled with avx2/avx512 including auto detection for cpu support)
- Orientation patches for several handheld devices
- Support for Rog Ally patched in the kernel
- Fixes and improvements for VRR on AMD

## Planned
- Improve the experience further to provide a Steam Deck similar experience to SteamOS
- Provide the Steam Deck Themes
- Enhance Hardware Support

## Device specific / Officially supported devices
Device specific customizations are mainly provided by the chwd profiles [Profiles](https://github.com/CachyOS/chwd/blob/master/profiles/pci/handhelds/profiles.toml) and the kernel.
### Steam Deck
Valve's powerbuttond is used to handle power button events\
Steam is used for controller support.
### ROG Ally
Handheld Daemon (HHD) is used by default to provide power button handling and controller support.\
Rogue enemy is an alternative that provides power profile switching and controller support.
### Lenovo Legion
Handheld Daemon (HHD) is used by default to provide power button handling and controller support.


## Desktop Support

it is generally planned to enhance the support further also for desktops.
This generally already works, but swichting the gamesession on Desktops could show problems.


## Additonal Information

### How can I disable scx_lavd and use the BORE/EEVDF Scheduler?

This can be simply done with following:
```
sudo systemctl disable scx.service
sudo systemctl mask scx.service
```
### How can I change the default desktop scaling?
For unofficially support devices the scaling is provided by KDE.\
For officially supported devices (deck, ally, legion go, etc) the scaling is provided by a custom deckscale script.\
The values used by this script can be configured using the configuration file located at ~/.config/deckscale\
If this file does not exist for you, create it and add the contents from [this file.](https://github.com/CachyOS/CachyOS-Handheld/blob/main/etc/skel/.config/deckscale)

## Credit to:
- ChimeraOS
- Ripplingsnake
- Manjaro (Phillip Müller for the base deckify package)

## Maintainers
- Pogogo007 (Nekoh)
- ptr1337
