var states = { 
  'running': 'Running',
  'stopped': 'Stopped',
  'pending': 'Creation in Progress',
  'stopping': 'Stopping',
  'shutting-down': 'Shutting Down',
  'rebooting': 'Rebooting',
  'terminated': 'Terminated (Deleted)'
};

var updateProgressBar = function(value) {
  if ($('#instanceProgress').attr('aria-valuenow') != value + '') {
    if (value == 100) {
      $('#instanceProgress').addClass('progress-bar-success');
    }
    else {
      $('#instanceProgress').removeClass('progress-bar-success');
    }
    $('#instanceProgress').css('width', value + '%').attr('aria-valuenow', value);   
  }
};

var displayID = '';

angular.module('chefViz', [])
  .controller('chefVizController', function($scope, $http) {

    $scope.instanceFound = false;

    $scope.instance = {
      name: '',
      status: '',
      friendlyStatus: '',
      creation_time: '',
      ami: '',
      operating_system: 'Pending Chef Report',
      ip_address: '',
      keyname: '',
      uptime: 'Pending Chef Report',
      deployPercent: 0
    };

    $scope.showError = function() {
      return $scope.instance.status == 'terminated' || $scope.instance.status == 'stopped';
    };
    $scope.showProgress = function() {
      return $scope.instance.uptime == 'Pending Chef Report' && ($scope.instance.status != 'terminated' || $scope.instance.status != 'stopped');
    };
    $scope.showSuccess = function() {
      return $scope.instance.uptime != 'Pending Chef Report' && ($scope.instance.status == 'terminated' || $scope.instance.status == 'running');
    }

    //Fire off a timer to refersh the data automatically in the background
    setInterval(function() {
      if ($scope.instanceFound) {
        $scope.searchAMI();
      }
    }, 3000);

    $scope.instanceID;
    $scope.chef_runlist = [];

    $scope.reset = function() {

      //Clean up any old runs
      $('#instanceProgress').css('width', '0%').attr('aria-valuenow', 0);    
      $('#instanceProgress').removeClass('progress-bar-success');
      $scope.instance = {
        name: '',
        status: '',
        friendlyStatus: '',
        creation_time: '',
        ami: '',
        operating_system: 'Pending Chef Report',
        ip_address: '',
        uptime: 'Pending Chef Report',
        deployPercent: 0
      };
    };


    $scope.searchAMI = function() {
      if (displayID != $scope.instanceID) {
        $scope.reset();
        $scope.instanceFound = false;
        displayID = $scope.instanceID;
      }

      util.getNodeRESTData("/aws/instance/" + $scope.instanceID, function(data) {
        //Iterate the tags and try to find the instance Name (the node name in Chef)

        if (data.Reservations != null && data.Reservations.length > 0 && datadata.Reservations[0].Instances != null) {
          $scope.updateFieldData(data);
        }
        else {
          //Try searching by instance name
          util.getNodeRESTData("/aws/instance/name/" + $scope.instanceID, function(data) {
            if (data.Reservations != null && data.Reservations.length > 0 && data.Reservations[0].Instances != null) {
              $scope.updateFieldData(data);
            }
            else {
              //Make the warning alert visible
              $('#noInstanceIDWarn').removeClass('collapse')
              setTimeout(function() {$('#noInstanceIDWarn').addClass('collapse')}, 5000);
            }
          });
        }
      });
    }

    //See if we were redirected an instance to monitor
    var redir = util.getURLParam('instanceName');
    if (redir) {
      $scope.instanceID = redir;
      console.log(displayID);
      $scope.searchAMI();
    }
    
    // see if we have an injected instanceName
    if (window.cocreate && window.cocreate.instanceName) {
        $scope.instanceID = window.cocreate.instanceName;
        console.log(displayID);
        $scope.searchAMI();
        $("#headerInfoContainer").hide();
    }

    $scope.getRunList = function() {

      util.getNodeRESTData("/chef/node/" + $scope.instance.name, function(data) {

        if (data.automatic != null && data.automatic.recipes != null) {
          $scope.chef_runlist = data.automatic.recipes;

          $scope.instance.operating_system = data.automatic.os + ' ' + data.automatic.platform + ' ' + data.automatic.platform_version;
          $scope.instance.ip_address = data.automatic.ipaddress;
          $scope.instance.uptime = data.automatic.uptime;

          updateProgressBar(100);
        }
        else {
          if ($scope.instance.status == "pending") {
            $scope.chef_runlist = ["Chef recipes will run when instance is created"];
            updateProgressBar(0);
          }
          else if ($scope.instance.status == "running") {
            $scope.chef_runlist = ["Chef recipes are currently provisioning the instance"];
            updateProgressBar(50);  
          }
          else {
            $scope.chef_runlist = ["No Recipes Found"];
            updateProgressBar(0);
          }
        }
        $('#instanceResult').css('visibility', 'visible');
      }, function(data) {
      // log error
      $scope.chef_runlist = ["No Recipes Found"];
      $('#instanceResult').css('visibility', 'visible');

      });
    };

    $scope.updateFieldData = function(data) {
      var tags = data.Reservations[0].Instances[0].Tags;
      $.each(tags, function(index, item) {
        if (item.Key == "Name") {
          $scope.instanceFound = true;

          $scope.instance.name = item.Value;
          $scope.instance.status = data.Reservations[0].Instances[0].State.Name;
          $scope.instance.friendlyStatus = states[$scope.instance.status];
          $scope.instance.creation_time = data.Reservations[0].Instances[0].LaunchTime;
          $scope.instance.ami = data.Reservations[0].Instances[0].ImageId + ' ' + 
            data.Reservations[0].Instances[0].Architecture;

          $scope.instance.ip_address = data.Reservations[0].Instances[0].PrivateIpAddress;
          $scope.instance.keyname = data.Reservations[0].Instances[0].KeyName;
          $scope.getRunList();
        }
      });

      if (!$scope.instanceFound) {
        //Make the warning alert visible
        $('#noInstanceIDWarn').removeClass('collapse')
        setTimeout(function() {$('#noInstanceIDWarn').addClass('collapse')}, 5000);
      }
    }
  });
