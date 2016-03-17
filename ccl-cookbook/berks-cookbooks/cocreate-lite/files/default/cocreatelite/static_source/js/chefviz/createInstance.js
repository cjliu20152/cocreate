angular.module('chefInstanceCreate', [])
  .controller('chefInstanceController', function($scope, $http) {

    $scope.instance = {
      name: '',
      ami: '',
      type: '',
      sshKey: '',
      recipe: '',
      vpc: '',
      subnet: '',
      secGroups: [],
        csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]')[0].value
    };

    $scope.vpcChange = function() {
      $scope.getSecurityGroupsByVPC($scope.instance.vpc);
      $scope.getSubnetsByVPC($scope.instance.vpc);
    };

    $scope.recipeChange = function() {
      //Preload the defaults for this recipe
      util.getNodeRESTData('/aws/applicationConfig/' + $scope.instance.recipe, function(data) {
        if(data != 'No config found') {
          $scope.instance.ami = data.ami;
          $scope.instance.vpc = data.vpc;
          $scope.getSubnetsByVPC(data.vpc);
          $scope.getSecurityGroupsByVPC(data.vpc);
          $scope.instance.subnet = data.subnet;
          $scope.instance.type = data.instanceType;
          $scope.instance.recipe = data.recipe;
          $scope.instance.secGroups = data.secGroups;
        }
      });
    };

    $scope.recipes = {};
    $scope.securityGroups = {};
    $scope.keyPairs = {};
    $scope.amis = {};
    $scope.instanceTypes = {};
    $scope.vpcs = {};
    $scope.subnets = {};

    $scope.getAMIs = function() {
      util.getNodeRESTData('/aws/amis/chef', function(data) {
        $scope.amis = data.Images;
      });
    };
    $scope.getAMIs();

    $scope.getInstanceTypes = function() {
      util.getNodeRESTData('/aws/instanceTypes', function(data) {
        $scope.instanceTypes = data.InstanceTypes;
      });      
    };
    $scope.getInstanceTypes();

    $scope.getInstanceVPCs = function() {
      util.getNodeRESTData('/aws/vpcs', function(data) {
        $.each(data.Vpcs, function(index, item) {
          $.each(item.Tags, function(tagIndex, tagItem) {
            if (tagItem.Key == "Name") {
              item.VpcName = tagItem.Value;
            }
          });
        });
        $scope.vpcs = data.Vpcs;
      });
    }
    $scope.getInstanceVPCs();

    $scope.getRecipes = function() {
      //Get the implementation cookbooks only
      util.getNodeRESTData('/chef/cookbooks/impl', function(data) {
        $scope.recipes = data.cookbooks;
      });
    };
    $scope.getRecipes();


    $scope.getInstanceVPCs();


    $scope.getSubnetsByVPC = function(vpc) {
      util.getNodeRESTData('/aws/subnets/vpc/'+ vpc, function(data) {
        $scope.subnets = data.Subnets;
      });
    }



    $scope.getSecurityGroupsByVPC = function(vpc) {
      util.getNodeRESTData('/aws/securityGroups/vpc/' + vpc, function(data) {
        $scope.securityGroups = data.SecurityGroups;
        $.each($scope.securityGroups, function(index, item) {
          //If this sec group item is set as the "default" for this recipe, select it
          if ($.inArray(item.GroupId, $scope.instance.secGroups) > -1) {
            item.active = true;
          }
        })
      });
    };

    $scope.secGroupClicked = function(secGroupId) {
      if ($('#' + secGroupId).hasClass('active')) {
        $('#' + secGroupId).removeClass('active');
      }
      else {
        $('#' + secGroupId).addClass('active');
      }
    };

    $scope.getKeyPairs = function() {
      util.getNodeRESTData('/aws/keypairs', function(data) {
        $scope.keyPairs = data.KeyPairs;
      });
    };
    $scope.getKeyPairs();

    $scope.createInstance = function() {
      //Get the actively selected security groups after clearing the old ones
      $scope.instance.secGroups = [];
      $.each($('#securityGroups').children('.active'), function(index, item) {
        $scope.instance.secGroups.push(item.id);
      });

      if (!$scope.fieldsFilled()) {
        $('#invalidFieldWarn').removeClass('collapse');
          setTimeout(function() {$('#invalidFieldWarn').addClass('collapse')}, 5000);
      }
      else {
        //Send it off
        
        $.ajax({
          type: "POST",
          //url: util.restURL + "/create",
            url: "/sandbox/request/aws",
          data: $scope.instance,
          success: function(data) {
            console.log($scope.instance);
            console.log(data);
            //var status_page = "/sandbox/status_aws?instanceName=" + $scope.instance.name;
            var status_page = "/sandbox/status/aws/" + $scope.instance.name;
            window.location.replace(status_page);
          },
          error: function(data) {
            console.error(data);
          },
          dataType: "JSON"
        });
      }
    };

    $scope.fieldsFilled = function() {
      return $scope.instance.name != '' && $scope.instance.ami != '' 
      && $scope.instance.type != '' && $scope.instance.sshKey != '' 
      && $scope.instance.recipe != '' && $scope.instance.vpc != '' && $scope.instance.subnet != '' && $scope.instance.secGroups.length > 0
    }
    $scope.fieldFilled = function(fieldName) {
      switch (fieldName) {
        case 'name':
        case 'ami':
        case 'type':
        case 'sshKey':
        case 'recipe':
        case 'vpc':
        case 'subnet':
          return (eval("$scope.instance." + fieldName)) != '';
          break;
        case 'secGroups': 
          return $('#securityGroups').children('.active').length > 0;
          break;
      }
    }
  });
