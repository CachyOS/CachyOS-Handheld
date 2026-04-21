# Cachyos-Handheld-Edition

Handheld Edition of CachyOS

This will include our own calamares, adjusted desktop and scripts for proper installation on handhelds.
We will provide only the online installation, so an internet connection will be mandatory.

Currently it is not planned to support more bootloaders, but if there is any interest we can simply add them as in our default ISOs. For now we will default to systemd-boot.
There will be support for 5 different filesystems:

- xfs
- ext4
- btrfs (default)
- zfs
- bcachefs

There will also be automatic snapshotting implemented, to make it easy for users to rollback if they run into issues.
Bcachefs could be generally a good idea for handhelds, but it is not fully ready yet and we don't suggest it for now.

## Features
- `scx_lavd` used as default scheduler - LAVD is a latency sensitive scheduler, which is intended to be used for handhelds and gaming
- Steam Deck-like experience
- Gamescope Session properly implemented
- Kernel patched to support Steam Deck OLED and Rog Ally respectively
- Steam Deck OLED Firmware included as default
- HDR correctly implemented via kernel patches
- All dependencies and packages bundled for proper gaming experience (cachyos-gaming-meta)
- Support for Winesync/Fastsync/NTSync
- BBRv3 used as default
- OpenRGB patches included
- Screensharing for Discord (via xwaylandvideobridge)
- CachyOS kernel
- CachyOS repository (all packages compiled with avx2/avx512 including auto detection for cpu support)
- Orientation patches for several handheld devices
- Fixes and improvements for VRR on AMD

## Planned
- Provide better Steam Deck-like experience to SteamOS
- Provide Steam Deck themes
- Enhance hardware support

## Device specific / Officially supported devices
Device specific customizations are mainly provided by chwd [profiles](https://github.com/CachyOS/chwd/blob/master/profiles/pci/handhelds/profiles.toml) and kernel.
### Steam Deck
Valve's powerbuttond is used to handle power button events.\
Steam is used for controller support.
### ROG Ally
[steam-powerbuttond-git](https://gitlab.steamos.cloud/holo/powerbuttond) is used to handle power button events.\
InputPlumber is used for controller support.\
Rogue enemy is an alternative that provides power profile switching and controller support.
### Lenovo Legion
Handheld Daemon (HHD) is used by default to provide power button handling and controller support.

## Non Officially supported hardware.
On untested/unsupported hardware, you may face issues such as wrong screen orientation, missing sound, etc...
HHD is not enabled automatically on unknown hardware, as such it must be enabled for specific controllers to work.

## Desktop Support

It is generally planned to enhance desktop support.
This generally already works, but switching the gamesession on desktops could show problems.

## Additonal Information

### How can I disable `scx_lavd` and use the BORE/EEVDF scheduler?

This can be simply done with following:
```
sudo systemctl disable scx.service
sudo systemctl mask scx.service
```

## Credit to:
- [ChimeraOS](https://chimeraos.org/)
- [Ripplingsnake](https://github.com/ripplingsnake)
- [Manjaro](https://manjaro.org) ([Phillip Müller](https://sourceforge.net/u/philmmanjaro/profile) for the base deckify package)
- [Bazzite](https://bazzite.gg/)

## Maintainers
- [Pogogo007 (Nekoh)](https://github.com/Pogogo007)
- [ptr1337 (Peter Jung)](https://github.com/ptr1337)
