var statesMap = { 
    'running': 'Running',
    'stopped': 'Stopped',
    'pending': 'Creation in Progress',
    'stopping': 'Stopping',
    'shutting-down': 'Shutting Down',
    'rebooting': 'Rebooting',
    'terminated': 'Terminated (Deleted)'
};

var util = {
    restURL: "http://nga-eaw-node-1734575316.us-gov-west-1.elb.amazonaws.com",
    djangoURL: "",
    
   /* getNodeRESTData: function(service, success, error) {
        angular.element('html')
               .injector()
               .get('$http')
               .get(util.restURL + service)
               .success(
                   function(data, status, headers, config) {
                       success(data);
                   }
               )
               .error(
                   function(data, status, headers, config) {
                       error(data);
                   }
               );
    },*/
    getNodeRESTDataFromDjango: function(service, success, error) {
        angular.element('html')
               .injector()
               .get('$http')
               .get(util.djangoURL + service)
               .success(
                   function(data, status, headers, config) {
                       success(data);
                   }
               )
               .error(
                   function(data, status, headers, config) {
                       error(data);
                   }
               );
    },

    getURLParam: function(name) {
        var results = new RegExp('[\?&]' + name + '=([^&#]*)').exec(window.location.href);
        if (results==null){
            return null;
        }
        else{
            return results[1] || 0;
        }
    },
    
    /*
        Return a value that looks like:
        {
            status: <string>,
            display: <friendly string>,
            precent: <integer>
        }
    
        util.getInstanceStatus("foo",
            function (status) {
                updatePercentComplete("foo", status.percent);
            }
        )
    */
    getInstanceStatus: function(instanceName, success, error) {
        
        // we need to chain calls together, first to /aws/instance/<instanceName> and /aws/instance/name/<instanceName>
        // to see if this even exists, 
        // and then to /chef/node/<instanceName> to get the progress and status
        
        util.getNodeRESTData("/aws/instance/" + instanceName,
        
            // results from /aws/instance
            function (data) {
                if (data.Reservations != null && data.Reservations.length > 0 && datadata.Reservations[0].Instances != null) {
                      // we have what we need -> $scope.updateFieldData(data);
                      // send to success
                      util._getProgressFromInstanceData(instanceName, data, success, error);                      
                }
                else {
                    // check with /aws/instance/name/<instanceName> (why doesn't this happen in the backend?)
                    util.getNodeRESTData("/aws/instance/name/" + instanceName,
                    
                        // results from /aws/instance/name
                        function (data) {
                            if (data.Reservations != null && data.Reservations.length > 0 && data.Reservations[0].Instances != null) {
                                // we have what we need -> $scope.updateFieldData(data)
                                // send to success
                                util._getProgressFromInstanceData(instanceName, data, success, error);
                            }                            
                        },
                        
                        // error from /aws/instance/name
                        function (data) {
                            // send to error
                            error(data);
                        }
                    
                    )
                }
            },
            
            // error from /aws/instance
            function (data) {
                // send an error response/unknown 0%
                // send to error
                error(data);
            }
        );
    },
    
    _getProgressFromInstanceData: function (instanceName, instanceData, success, error) {
        
        var instanceFound = false;
        var instanceStatus = {
            status: "",
            display: "",
            precent: 0
        };
        
        $.each(instanceData.Reservations[0].Instances[0].Tags,
            function (index, item) {
                if (item.Key == "Name") {
                    instanceFound = true;
                    instanceStatus.status = data.Reservations[0].Instances[0].State.Name;
                    instanceStatus.display = statesMap[instanceStatus.status];
                }
            }
        )
        
        if (instanceFound) {
            // build out the run list call
            util.getNodeRESTData("/chef/node/" + instanceName,
            
                // results from /chef/node/<instanceName>
                function (data) {
                    
                    if (data.automatic != null && data.automatic.recipes != null) {
                        instanceStatus.percent = 100;
                    }
                    else if (instanceStatus.status == 'pending') {
                        instanceStatus.percent = 0;
                    }
                    else if (instanceStatus.status == 'running') {
                        instanceStatus.percent = 50;
                    }
                    else {
                        instanceStatus.percent = 0;
                    }
                    
                    success(instanceStatus);
                
                },
                
                // error from /chef/node/<instanceName>
                function (data) {
                    error(data);
                }
            );

            
        }
        else {
            error(instanceData);
        }
    }
} 
