$CONTAINER_ROOT = $args[0]
$NEXTCLOUD_INSTANCES = $args[1]

function EnablePlugin {
    param (
        [string] $ContainerName
    )
    
    Write-Host -ForegroundColor red "Container: $ContainerName"
    Write-Host -ForegroundColor blue "Enabling: user_ldap"
    docker exec -u www-data -it $ContainerName php occ app:enable user_ldap
}

for ( $i = 1; $i -le $NEXTCLOUD_INSTANCES; $i++ ) {
    EnablePlugin -ContainerName $CONTAINER_ROOT$i"_1"
    Write-Host -ForegroundColor green "--------------------------------------"
}
