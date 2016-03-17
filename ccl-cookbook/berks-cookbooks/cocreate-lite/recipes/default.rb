if node["cocreatelite"]["only_update"] == false

    include_recipe "chef-dk"
    include_recipe "cocreate-lite::vagrant_ccl"
    include_recipe "cocreate-lite::python34"
end

include_recipe "cocreate-lite::cocreate"

if node["cocreatelite"]["only_update"] == false && node["cocreatelite"]["local"] == true
    include_recipe "cocreate-lite::gnome"
end
