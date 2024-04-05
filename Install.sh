#!/bin/bash

# Function to execute commands with optional prompt
execute_command() {
    command=$1
    prompt=$2
    if [ "$prompt" = true ]; then
        read -p "Execute: $command (y/n)? " choice
        case "$choice" in
            y|Y ) eval $command;;
            * ) echo "Skipping $command";;
        esac
    else
        eval $command
    fi
}



# Bluetooth configuration
configure_bluetooth() {
    execute_command "sudo systemctl enable --now bluetooth" true
}

# install yay
install_additional_packages() {
execute_command "sudo pacman -S yay"
}

# Install additional packages
install_additional_packages() {
    execute_command "yay -S steam gamescope mangohud-git lib32-mangohud-git qt5-tools qt6-tools gamescope-session-steam-git inputplumber-git chimeraos-device-quirks-git" true
}

# InputPlumber setup
inputplumber_setup() {
  
    execute_command "sudo systemctl enable --now inputplumber" true
}

# Steam configuration
configure_steam() {
    echo "Please log in to your Steam account and make the necessary changes."
    echo "Refer to the guide for details."
}

# Steam-Deckify setup
steam_deckify_setup() {
    echo "Please download Steam-Deckify contents and run 'sudo makepkg -si'."
}

# SDDM settings
configure_sddm_settings() {
    echo "Please configure SDDM settings manually."
    echo "Refer to the guide for details."
}

# KDE Wallet warning
kde_wallet_warning() {
    echo "Please change the KDE wallet password to avoid requiring the Wi-Fi password on boot."
    echo "Refer to the guide for details."
}
# Install Asusctl
install_asusctl() {
    execute_command "git clone https://github.com/flukejones/asusctl.git" true
    execute_command "cd asusctl && make build && sudo make install" true
}

#
# Reboot
reboot_system() {
    execute_command "reboot" true
}

# Main function
main() {
    download_iso
    choose_bootloader
    configure_bluetooth
    install_additional_packages
    inputplumber_setup
    configure_steam
    steam_deckify_setup
    configure_sddm_settings
    kde_wallet_warning
    reboot_system
}

# Call main function
main
