angular.module('chefInstanceCreate', [])
  .controller('chefInstanceController', function($scope, $http, $location) {

    $scope.instance = {
      name: '',
      repository: '',
      ami: '',
      type: '',
      sshKey: '',
      recipe: '',
      vpc: '',
      subnet: '',
      secGroups: [],
      csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]')[0].value
    };

    // get our playground
    $scope.playground_id = $location.path().split("/")[2];
    
    console.log("Playground_id: " + $scope.playground_id);
    
    $scope.vpcChange = function() {
      $scope.getSecurityGroupsByVPC($scope.instance.vpc);
      $scope.getSubnetsByVPC($scope.instance.vpc);
    };

    $scope.recipeChange = function() {
      //Preload the defaults for this recipe
    };

    $scope.repositories = {};
    $scope.recipes = {};
    $scope.securityGroups = {};
    $scope.keyPairs = {};
    $scope.amis = {};
    $scope.instanceTypes = {};
    $scope.vpcs = {};
    $scope.subnets = {};
    
    $scope.getRepositories = function() {
        util.getNodeRESTDataFromDjango('/api/git/repositories', function (data) {
            $scope.repositories = data.Repositories;
        });
    };

    $scope.getRepositories();
    
    $scope.getAMIs = function() {
      util.getNodeRESTDataFromDjango('/api/aws/amis', function(data) {
        $scope.amis = data.Images;
      });
    };
    
    $scope.getAMIs();

    $scope.getInstanceTypes = function() {
      util.getNodeRESTDataFromDjango('/api/aws/instanceTypes', function(data) {
        $scope.instanceTypes = data.InstanceTypes;
      });      
    };
    
    $scope.getInstanceTypes();

    $scope.getInstanceVPCs = function() {
      util.getNodeRESTDataFromDjango('/api/aws/vpcs', function(data) {
        $.each(data.Vpcs, function(index, item) {
          try {
            $.each(item.Tags, function(tagIndex, tagItem) {
              if (tagItem.Key == "Name") {
                item.VpcName = tagItem.Value;
              }
            });
          } catch(err) {
            console.log("Adding Tags for vpc w/o")
            item.VpcName = 'Name not provided (' + item.VpcId + ')';
          }
        });
        $scope.vpcs = data.Vpcs;
      });
    }
    
    $scope.getInstanceVPCs();

    $scope.getRecipes = function() {
      //Get the implementation cookbooks only
      util.getNodeRESTDataFromDjango('/api/chef/cookbooks', function(data) {
        $scope.recipes = data.recipes;
        console.log($scope.recipes);
      });
    };

    $scope.getRecipes();

    $scope.getInstanceVPCs();

    $scope.getSubnetsByVPC = function(vpc) {
      util.getNodeRESTDataFromDjango('/api/aws/vpc/'+ vpc + "/subnets", function(data) {
        console.log("subnets", data.Subnets);
        $.each(data.Subnets, function(index, item) {
          var attr = $(this).attr('Tags');
          if (!(typeof attr !== typeof undefined && attr !== false)) {
            console.log("Adding Tags for subnet w/o")
            item.Tags = [{'Value': 'Name not provided (' + item.SubnetId + ' in ' + item.AvailabilityZone + ')', 'Key': 'Name'}]
          }
        });
        $scope.subnets = data.Subnets;
      });
    }

    $scope.getSecurityGroupsByVPC = function(vpc) {
      util.getNodeRESTDataFromDjango('/api/aws/vpc/' + vpc + '/secgroups', function(data) {
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
      util.getNodeRESTDataFromDjango('/api/ssh/keys', function(data) {
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
      } else {
          
        $('#createInstanceButton').button('loading');
          
        //Send it off
        console.log($scope.instance.name);

        var endpoint = $('input[name=omnibusEndpoint]')[0].value;
        var options = {authToken: $('input[name=omnibusAuthToken]')[0].value};

        var stack = "";

        var modalLabel = document.getElementById('vagrantModalLabel')
        modalLabel.innerHTML = modalLabel.innerHTML.replace('Provisioning and configuration output for', 'Provisioning and configuration output for "' + $scope.instance.name + '".');

        var div = document.getElementById('vagrantBody');
        var pre = document.getElementById('vagrantPre');
        var updateInterval = 1000;

        (function() {
          // Initialize websocket to back-end
          var transport = SockJS;
          var connection = new Omnibus(transport, endpoint, options);
          var channel = connection.openChannel('vagrants');

          // Handle $scope.instance.name events
          channel.on($scope.instance.name, function (event) {
            stack = stack + "\n" + event.data.payload.text;      
          });
        })();

        function updateVagrantStdout() {
          if (stack != "") {
            $('#vagrantModal').modal('show')  
            pre.innerHTML = pre.innerHTML + stack;
            stack = "";

            // force modal to scroll to bottom to show latest 
            // events.
            div.scrollTop = div.scrollHeight; 
          } 
        }

        var intervalId = setInterval(updateVagrantStdout, updateInterval);

        // Stylize modal aka make it bigger.
        $(".vagrant-modal").on("show.bs.modal", function() {
          var height = $(window).height() - 200;
          $(this).find(".modal-body").css("max-height", height);
        }); 

        $.ajax({
          type: "POST",
          //url: util.restURL + "/create",
          url: "/playground/" + $scope.playground_id + "/sandbox/add",
          //url: "/api/aws/create",
          data: $scope.instance,
          success: function(data) {
            console.log($scope.instance);
            console.log("success calling " + "/playground/" + $scope.playground_id + "/sandbox/add")
            console.log(data);
            //var status_page = "/sandbox/status_aws?instanceName=" + $scope.instance.name;
            var status_page = "/playground/" + $scope.playground_id;
            window.location.replace(status_page);
          },
          error: function(data) {
            console.error("error calling " + "/playground/" + $scope.playground_id + "/sandbox/add")
            console.error(data);
          },
          dataType: "JSON"
        });
      }
    };

    $scope.fieldsFilled = function() {
      return $scope.instance.name != '' && $scope.instance.ami != ''
      && $scope.instance.type != '' && $scope.instance.recipe != ''
      && $scope.instance.vpc != '' && $scope.instance.subnet != ''
      && $scope.instance.secGroups.length > 0
    }

    $scope.fieldFilled = function(fieldName) {
      switch (fieldName) {
        case 'name':
        case 'ami':
        case 'type':
        case 'sshKey':
        case 'recipe':
        case 'vpc':
        case 'repository':
        case 'subnet':
          return (eval("$scope.instance." + fieldName)) != '';
          break;
        case 'secGroups': 
          return $('#securityGroups').children('.active').length > 0;
          break;
      }
    }
  })

  // Ungh. We need the location provider to make this page work, but it hijacks all A tags, which means _no other links_ on the
  // page work. <angry face/>
  .config(function($locationProvider) {
    $locationProvider.html5Mode(true).hashPrefix('!');
  });
