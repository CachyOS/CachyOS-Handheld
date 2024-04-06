
#!/bin/bash

# Display a dialog with radio buttons
choice=$(zenity --list --title="ASUS Power Control EPP" --text="Choose a power profile:" \
        --radiolist --column="Select" --column="Power Control" \
        TRUE "Performance  >15 Watts" \
        FALSE "Balanced  <15> Watts" \
        FALSE "Low  <10 Watts")

# Handle the user's choice
case "$choice" in
    "Performance")
        echo "Setting power profile to Performance."
        # Set the desired power profile using powerprofilesctl
        powerprofilesctl set performance
        ;;
    "Balanced")
        echo "Setting power profile to Balanced."
        # Set the balanced power profile
        powerprofilesctl set balanced
        ;;
    "Power Save")
        echo "Setting power profile to Low."
        # Set the power saver profile
        powerprofilesctl set power-saver
        ;;
    *)
        echo "No profile selected."
        ;;
esac
