#!/bin/bash

# Function to change power settings
change_power_setting() {
    setting=$1
    powerd --configure $setting
}

# Function to create GUI with radio buttons
create_gui() {
    echo "Choose a power setting:"
    PS3="Enter your choice: "
    options=("Low Power" "Balanced" "High Performance" "Quit")
    select opt in "${options[@]}"
    do
        case $opt in
            "Low Power")
                change_power_setting "low"
                ;;
            "Balanced")
                change_power_setting "balanced"
                ;;
            "High Performance")
                change_power_setting "high"
                ;;
            "Quit")
                break
                ;;
            *) echo "Invalid option";;
        esac
    done
}

# Main function
main() {
    create_gui
}

# Call main function
main
