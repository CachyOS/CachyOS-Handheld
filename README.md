# Cachyos-Handheld-Edition

Handheld Edition of CachyOS

This will include our own calamares, adjusted desktop and scripts for proper installation on handhelds.
We will provide only the online installation, so an internet connection will be mandatory.

Currently it is not planned to support more bootloaders, but if there is any interest we can simply add them as in our default ISOs.
There will be support for 4 different filesystems:

- xfs
- ext4
- btrfs (default)
- zfs

There is also automatic snapshotting with btrfs and limine to make it easy for users to rollback if they run into issues after updating.

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
- CachyOS handheld Kernel
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
steam-powerbuttond-git is used to handle power button events.\
InputPlumber is used for controller support.\
Rogue enemy is an alternative that provides power profile switching and controller support.
### Lenovo Legion
Handheld Daemon (HHD) is used by default to provide power button handling and controller support.

## Non Officially supported hardware.
On not tested/supported hardware, you may face issues such as wrong screen orientation, missing sound, etc.
HHD is not enabled automatically on unknown hardware, as such it must be enabled for specific controllers to work.

## Desktop Support

it is generally planned to enhance the support further also for desktops.
This generally already works, but swichting the gamesession on Desktops could show problems.

## Additonal Information

### How can I update without leaving Gaming Mode?

**Update CachyOS** is added to the Non-Steam games library automatically.
To add it again manually, run:

```
steamos-add-to-steam /usr/share/applications/cachyos-handheld-update.desktop
```

To disable automatic setup for every user, run
`sudo systemctl --global disable cachyos-handheld-updater-setup.path`.
That change takes effect at the next user-session start.
For just your account, run
`systemctl --user mask --now cachyos-handheld-updater-setup.path cachyos-handheld-updater-setup.service`.

Then launch **Update CachyOS** from Steam's Library in Gaming Mode. It opens a
full-screen terminal, asks for your account password and confirms a full
`pacman -Syu` upgrade. Steam + X opens the on-screen keyboard.

### How can I permanently boot to Desktop Mode?

The default handheld behavior starts the Gamescope session on every fresh boot.
To make the system remember the last selected session instead, run:
```
steamos-session-select persistent
```

After enabling persistent mode, switching to Desktop Mode will keep future boots
on the desktop session instead of forcing Gamescope again.

To restore the default handheld behavior, run:
```
steamos-session-select oneshot
```

With oneshot mode enabled, every fresh boot starts in the Gamescope session.

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
- Bazzite

## Maintainers
- Pogogo007 (Nekoh)
- ptr1337
