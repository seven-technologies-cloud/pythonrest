desired_entry='/usr/bin/python-rest'
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
echo 'export PATH="$new_path"' >> ~/.bashrc
