#!/bin/bash
# Run this script from the root of your target project (e.g., your Django app)

# Set the path to your central standards repository
VAULT_DIR=".wolfremium-agents"
TARGET_DIR=".agents"

echo "Bootstrapping Antigravity workspace from $VAULT_DIR..."

# 1. Create the standard Antigravity directories expected by the IDE
mkdir -p "$TARGET_DIR/rules" "$TARGET_DIR/skills"

# 2. Iterate through your vertical slices and symlink them
for SLICE in "$VAULT_DIR"/*; do
    if [ -d "$SLICE" ]; then
        SLICE_NAME=$(basename "$SLICE")
        echo "Injecting vertical slice: $SLICE_NAME"

        # Symlink the domain-specific rules into the active workspace
        if [ -d "$SLICE/rules" ]; then
            ln -sf "$SLICE/rules/"* "$TARGET_DIR/rules/"
        fi

        # Symlink the domain-specific skills into the active workspace
        if [ -d "$SLICE/skills" ]; then
            ln -sf "$SLICE/skills/"* "$TARGET_DIR/skills/"
        fi
    fi
done

# 3. Ensure the injected config is ignored by the project's Git repository
if ! grep -q "^.agents" .gitignore; then
    echo ".agents/" >> .gitignore
    echo "Added .agents/ to .gitignore"
fi