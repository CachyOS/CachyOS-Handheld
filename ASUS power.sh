
#!/bin/bash

# Display a dialog with radio buttons
choice=$(zenity --list --title="Power Preferences" --text="Choose a power profile:" \
        --radiolist --column="Select" --column="Profile" \
        TRUE "Performance" \
        FALSE "Balanced" \
        FALSE "Power Save")

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
        echo "Setting power profile to Power Save."
        # Set the power saver profile
        powerprofilesctl set power-saver
        ;;
    *)
        echo "No profile selected."
        ;;
esac
