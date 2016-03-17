angular.module('chefInstanceCreate', [])
  .controller('chefInstanceController', function($scope, $http, $location) {

    $scope.instance = {
      name: '',
      type: '',
        repository: '',
      sshKey: '',
      recipe: '',
      csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]')[0].value
    };

    // get our playground
    $scope.playground_id = $location.path().split("/")[2];
    
    console.log("Playground_id: " + $scope.playground_id);
  
    $scope.recipeChange = function() {
      //Preload the defaults for this recipe
      util.getNodeRESTDataFromDjango('/api/isee/application/' + $scope.instance.recipe + "/config", function(data) {
        if(data != 'No config found') {
          $scope.instance.type = data.instanceType;
          $scope.instance.recipe = data.recipe;
        }
      });
    };

    $scope.repositories = {};
    $scope.recipes = {};
    $scope.keyPairs = {};
    $scope.instanceTypes = {};
  
    $scope.getRepositories = function() {
        util.getNodeRESTDataFromDjango('/api/git/repositories', function (data) {
            $scope.repositories = data.Repositories;
        });
    };
    $scope.getRepositories();
  
    $scope.getInstanceTypes = function() {
      util.getNodeRESTDataFromDjango('/api/isee/instanceTypes', function(data) {
        $scope.instanceTypes = data.InstanceTypes;
      });      
    };
    $scope.getInstanceTypes();

  
    $scope.getRecipes = function() {
      //Get the implementation cookbooks only
      util.getNodeRESTDataFromDjango('/api/chef/cookbooks', function(data) {
        $scope.recipes = data.cookbooks;
      });
    };
    $scope.getRecipes();


    $scope.getKeyPairs = function() {
      util.getNodeRESTDataFromDjango('/api/ssh/keys', function(data) {
        $scope.keyPairs = data.KeyPairs;
      });
    };
    $scope.getKeyPairs();

    $scope.createInstance = function() {

      if (!$scope.fieldsFilled()) {
        $('#invalidFieldWarn').removeClass('collapse');
          setTimeout(function() {$('#invalidFieldWarn').addClass('collapse')}, 5000);
      }
      else {
        //Send it off
        
        $.ajax({
          type: "POST",
          //url: util.restURL + "/create",
            url: "/playground/" + $scope.playground_id + "/sandbox/add",
    //        url: "/sandbox/request/aws",
          data: $scope.instance,
          success: function(data) {
            console.log($scope.instance);
            console.log(data);
            //var status_page = "/sandbox/status_aws?instanceName=" + $scope.instance.name;
            var status_page = "/playground/" + $scope.playground_id;
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
      return $scope.instance.name != '' 
                && $scope.instance.type != '' 
                && $scope.instance.sshKey != '' 
                && $scope.instance.recipe != '';
    }
    
    $scope.fieldFilled = function(fieldName) {
      switch (fieldName) {
        case 'name':
        case 'repository':
        case 'type':
        case 'sshKey':
        case 'recipe':
          return (eval("$scope.instance." + fieldName)) != '';
          break;
      }
    }
  })
  .config(function($locationProvider) {
    $locationProvider.html5Mode(true).hashPrefix('!');
  });
