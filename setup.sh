#!/bin/bash
# Run this script from the root of your target project (e.g., your Django app)

# Set the path to your central standards repository
VAULT_DIR=".wolfremium-agents"
TARGET_DIR=".agents"

# 1. Gather all subfolders in $VAULT_DIR
options=()
for SLICE in "$VAULT_DIR"/*; do
    if [ -d "$SLICE" ]; then
        options+=("$(basename "$SLICE")")
    fi
done

if [ ${#options[@]} -eq 0 ]; then
    echo "No folders found in $VAULT_DIR."
    exit 1
fi

echo "Available folders in $VAULT_DIR:"
echo "---------------------------------"
for i in "${!options[@]}"; do
    echo "  $((i+1))) ${options[i]}"
done
echo "---------------------------------"
echo "Enter the numbers of the folders you want to import, separated by spaces (e.g., '1 2')."
echo "Or enter 'a' for all folders, or 'c' to cancel."

while true; do
    read -p "Selection: " input
    # Lowercase the input for comparison
    input_lower=$(echo "$input" | tr '[:upper:]' '[:lower:]')
    
    if [ "$input_lower" = "c" ]; then
        echo "Cancelled."
        exit 0
    elif [ "$input_lower" = "a" ]; then
        SELECTED_SLICES=("${options[@]}")
        break
    fi

    # Try parsing space-separated numbers
    valid=true
    temp_selected=()
    # Read words from input
    for num in $input; do
        if [[ "$num" =~ ^[0-9]+$ ]] && [ "$num" -ge 1 ] && [ "$num" -le "${#options[@]}" ]; then
            temp_selected+=("${options[num-1]}")
        else
            valid=false
            break
        fi
    done

    if [ "$valid" = true ] && [ ${#temp_selected[@]} -gt 0 ]; then
        SELECTED_SLICES=("${temp_selected[@]}")
        break
    fi

    echo "Invalid option. Please enter space-separated numbers corresponding to the folders, 'a', or 'c'."
done

echo "Bootstrapping Antigravity workspace from $VAULT_DIR..."

# 2. Create the standard Antigravity directories expected by the IDE
mkdir -p "$TARGET_DIR/rules" "$TARGET_DIR/skills"

# Clean up broken symlinks inside target rules/skills directories
find "$TARGET_DIR/rules" -maxdepth 1 -type l ! -exec test -e {} \; -delete
find "$TARGET_DIR/skills" -maxdepth 1 -type l ! -exec test -e {} \; -delete

# 3. Iterate through selected slices and symlink them
for SLICE_NAME in "${SELECTED_SLICES[@]}"; do
    SLICE="$VAULT_DIR/$SLICE_NAME"
    if [ -d "$SLICE" ]; then
        echo "Injecting vertical slice: $SLICE_NAME"

        # Symlink the domain-specific rules into the active workspace
        if [ -d "$SLICE/rules" ]; then
            for FILE in "$SLICE/rules"/*; do
                if [ -e "$FILE" ]; then
                    ln -sfn "../../$FILE" "$TARGET_DIR/rules/"
                fi
            done
        fi

        # Symlink the domain-specific skills into the active workspace
        if [ -d "$SLICE/skills" ]; then
            for FILE in "$SLICE/skills"/*; do
                if [ -e "$FILE" ]; then
                    ln -sfn "../../$FILE" "$TARGET_DIR/skills/"
                fi
            done
        fi
    fi
done

# 4. Ensure the injected config is ignored by the project's Git repository
if ! grep -q "^.agents" .gitignore; then
    echo ".agents/" >> .gitignore
    echo "Added .agents/ to .gitignore"
fi

echo "Workspace configuration updated successfully!"