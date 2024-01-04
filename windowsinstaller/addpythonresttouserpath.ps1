$desired_entry = 'C:\Program Files\PythonREST'
$old_path = [Environment]::GetEnvironmentVariable('PATH', 'User')
$old_path_entry_list = ($old_path).split(";")
$new_path_entry_list = New-Object System.Collections.ArrayList
foreach($old_path_entry in $old_path_entry_list) {
    if($old_path_entry -eq $desired_entry){
    }else{
        [void]$new_path_entry_list.Add($old_path_entry)
    }
}
[void]$new_path_entry_list.Add($desired_entry)
$new_path = $new_path_entry_list -Join ";"
[Environment]::SetEnvironmentVariable('PATH', $new_path, 'User')
