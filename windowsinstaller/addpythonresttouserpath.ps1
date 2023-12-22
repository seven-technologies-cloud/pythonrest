# Specify the desired entry to add
$desired_entry = 'C:\Program Files\PythonREST'

# Get the current user PATH
$old_path = [Environment]::GetEnvironmentVariable('PATH', 'User')

$old_path_entry_list = ($old_path).split(";")
$new_path_entry_list = New-Object System.Collections.ArrayList

foreach($old_path_entry in $old_path_entry_list) {
    if($old_path_entry -eq $desired_entry){
        # ignore old entry
    }else{
        [void]$new_path_entry_list.Add($old_path_entry)
    }
}

# Add the desired entry to the user PATH
[void]$new_path_entry_list.Add($desired_entry)

$new_path = $new_path_entry_list -Join ";"

# Set the updated user PATH
[Environment]::SetEnvironmentVariable('PATH', $new_path, 'User')
