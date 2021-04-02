CONTAINER_ROOT=$1
NEXTCLOUD_INSTANCES=$2

function enable_plugin() {
    # $1: Container name.
    # $2: Plugin to disable.
    echo "Disabling: user_ldap"
    docker exec -u www-data -it $1 php occ app:enable user_ldap
}

for i in $(seq 1 $NEXTCLOUD_INSTANCES)
do
    enable_plugin $CONTAINER_ROOT$i"_1"
    echo "--------------------------------------"
done
