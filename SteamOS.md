 CachyOS Installation Guide

## Download CachyOS
You can grab the latest ISO image of CachyOS from the following sources:
```  https://cachyos.org/download/
Install the ISO 
```
## Installation Process
Download the 3 files from Repo
# Steam-Deckify
# Install.sh
# ASUSpower.sh
You must make both the .sh files executable (rightclick file - Permissions - make exacutable
Open Konsole inside download folder type>
#  ./Install.sh
then
#  ./ASUSpower.sh
```

Follow onscreen instructions.

```

During setup select systemd-boot and online installer.

```
## Troubleshooting
- If Wi-Fi in Steam shows as disconnected, turn it off and then back on. It will prompt for the password.
- For additional performance tweaks, explore kernel-level settings on the CachyOS site.

## Recommended kernel 
6.8 or 6.9
Bore or scx_lavd scheduler
tick rate 500
LTO thin 
For inscructions and tweaks visit the cachyOS FAQ

```
## Useful commands and info.
# sudo pacman -Syu     (for system update)

Both inputplumber and asusctl are beta and recive update on regualar basis, its recommended
to check the git hub pages for both and time check the latest updates
# git clone ***HTTPS address***
Both programs to can open there respective folders in Home, open terminal and

# sudo make uninstall  This will remove previous version then 

# make
# sudo make install    This will install latest.

HAPPY GAMING!





