desired_entry='/usr/local/bin/pythonrest'

if [ -n "$BASH_VERSION" ]; then
    profile_file="$HOME/.bash_profile"
elif [ -n "$ZSH_VERSION" ]; then
    profile_file="$HOME/.zshrc"
else
    echo "Unsupported shell. Please use Bash or Zsh."
    exit 1
fi

old_path=$PATH
IFS=':' read -r -a old_path_entry_list <<< "$old_path"
new_path_entry_list=()

for old_path_entry in "${old_path_entry_list[@]}"; do
    if [ "$old_path_entry" != "$desired_entry" ]; then
        new_path_entry_list+=("$old_path_entry")
    fi
done

new_path=$(IFS=:; echo "${new_path_entry_list[*]}")
export PATH="$new_path"

echo 'export PATH="$new_path"' >> "$profile_file"
