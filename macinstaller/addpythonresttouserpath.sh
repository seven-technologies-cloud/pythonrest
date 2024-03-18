desired_entry='/usr/bin/python-rest'
bash_profile="$HOME/.bash_profile"
zshrc="$HOME/.zshrc"

if [ -n "$BASH_VERSION" ]; then
    profile_file="$bash_profile"
elif [ -n "$ZSH_VERSION" ]; then
    profile_file="$zshrc"
else
    echo "Unsupported shell. Please use Bash or Zsh."
    exit 1
fi

old_path=$PATH
IFS=':' read -r -a old_path_entry_list <<< "$old_path"
new_path_entry_list=()

for old_path_entry in "${old_path_entry_list[@]}"; do
    if [ "$old_path_entry" == "$desired_entry" ]; then
        continue
    else
        new_path_entry_list+=("$old_path_entry")
    fi
done

new_path_entry_list+=("$desired_entry")
new_path=$(IFS=:; echo "${new_path_entry_list[*]}")
export PATH="$new_path"

echo 'export PATH="$new_path"' >> "$profile_file"

source "$profile_file"
