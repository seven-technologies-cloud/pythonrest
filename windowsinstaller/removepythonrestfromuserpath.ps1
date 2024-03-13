$desired_entry = "$env:LOCALAPPDATA\PythonREST"

$old_path = [Environment]::GetEnvironmentVariable('PATH', 'User')

$old_path_entry_list = ($old_path).split(";")
$new_path_entry_list = New-Object System.Collections.ArrayList

foreach($old_path_entry in $old_path_entry_list) {
    if($old_path_entry -ne $desired_entry){
        [void]$new_path_entry_list.Add($old_path_entry)
    }
}

$new_path = $new_path_entry_list -Join ";"
[Environment]::SetEnvironmentVariable('PATH', $new_path, 'User')
