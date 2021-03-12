$CONTAINER_ROOT = $args[0]
$NEXTCLOUD_INSTANCES = $args[1]

$PLUGINS = "accessibility","dashboard","accessibility","firstrunwizard","nextcloud_announcements","photos","weather_status","user_status","survey_client","support","recommendations","updatenotification"

function DisablePlugin {
    param (
        [string] $ContainerName,
        [string] $Plugin
    )
    
    Write-Host -ForegroundColor red "Container: $ContainerName"
    Write-Host -ForegroundColor blue "Disabling: $Plugin"
    docker exec -u www-data -it $ContainerName php occ app:disable $Plugin
}

for ( $i = 1; $i -le $NEXTCLOUD_INSTANCES; $i++ ) {
    for ( $j = 0; $j -lt $PLUGINS.count; $j++ ) {
        DisablePlugin -ContainerName $CONTAINER_ROOT$i"_1" -Plugin $PLUGINS[$j]
        Write-Host -ForegroundColor green "--------------------------------------"
    }
}
