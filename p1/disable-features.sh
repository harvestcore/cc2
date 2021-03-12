CONTAINER_ROOT=$1
NEXTCLOUD_INSTANCES=$2

PLUGINS=(accessibility dashboard accessibility firstrunwizard nextcloud_announcements photos weather_status user_status survey_client support recommendations updatenotification)

function disable_plugin() {
    # $1: Container name.
    # $2: Plugin to disable.
    echo "Container: " $1
    echo "Disabling: " $2
    docker exec -u www-data -it $1 php occ app:disable $2
}

for i in $(seq 1 $NEXTCLOUD_INSTANCES)
do
    for j in "${PLUGINS[@]}"
    do
        disable_plugin $CONTAINER_ROOT$i"_1" $j
        echo "--------------------------------------"
    done
done
