angular.module('ekg', []).
config(function($locationProvider, $routeProvider) {
    $locationProvider.html5Mode(true);
    $routeProvider.
    when('/app/', {controller:ListCtrl, templateUrl:'/app/templates/list.html'}).
    when('/app/organizations/:organization/config', {controller:DetailsCtrl, templateUrl:'/app/templates/config.html'}).
    when('/app/organizations/:organization', {controller:OrganCtrl, templateUrl:'/app/templates/organization.html'}).
    when('/app/organizations/:organization/hearts', {controller:HeartListCtrl, templateUrl:'/app/templates/heartlist.html'}).
    when('/app/organizations/:organization/hearts/:heart', {controller:HeartCtrl, templateUrl:'/app/templates/heart.html'}).
    when('/app/invitations/:invite', {controller:InviteCtrl, templateUrl:'/app/templates/invite.html'}).
    otherwise({redirectTo:'/app/'});


});



var seticon = function(alert) {
    var element = document.getElementById("favicon");
    if(element){
        element.parentNode.removeChild(element);
    }
    var link = document.createElement('link');
    link.id = 'favicon';
    link.type = 'image/x-icon';
    link.rel = 'shortcut icon';
    link.href = alert ? '/app/img/favicon-red.ico' : '/app/img/favicon.ico';

    document.getElementsByTagName('head')[0].appendChild(link);
};




function HeartListCtrl ($scope, $http, $routeParams) {
    $http.get("/api/organizations/"+$routeParams.organization+'/hearts').success(function(result) {
        $scope.title = result.title;
        $scope.hearts = result.hearts;
    });
    $scope.organization = $routeParams.organization;
}

function InviteCtrl ($scope, $http, $routeParams, $location) {
    $http.get("/api/invitations/"+$routeParams.invite).success(function(result) {
        $scope.title = result.title;
    });

    $scope.accept = function() {
        $http.get("/api/invitations/"+$routeParams.invite+"/accept").success(function() {
            $location.path('/app/');
        });
    };

    $scope.decline = function() {
        $http.get("/api/invitations/"+$routeParams.invite+"/decline").success(function() {
            $location.path('/app/');
        });
    };
}
function ListCtrl ($scope, $http) {
    $scope.organizations = [];
    $http.get("/api/me/organizations").success(function(result) {
        $scope.organizations = result;
    });

    $scope.create = function  () {
        $http.post("/api/me/organizations", {title:$scope.title}).success(function(result) {
            $scope.organizations.push(result);
        });
        $scope.title = '';
    };
}

function DetailsCtrl ($scope, $http, $routeParams) {
    $scope.organization = $routeParams.organization;
    $http.get("/api/organizations/"+$routeParams.organization).success(function(result) {
        $scope.title = result.title;
        $scope.users = result.users;
        $scope.alert_email = result.alert_email;
    });
    $scope.send = function() {
        $scope.sending = true;
        $http.post('/api/invitations/', {organization: $routeParams.organization, email: $scope.email}).success(function() {
            $scope.sent = true;
            $scope.sending = false;
        });
    };
    $scope.save = function() {
        $scope.saving = true;
        $scope.saved = false;
        $http.put("/api/organizations/"+$routeParams.organization, {title:$scope.title, alert_email:$scope.alert_email}).success(function(result) {
            $scope.saved = true;
            $scope.saving = false;
            $scope.error = false;
        }).error(function() {
            $scope.error = true;
        });
    };
}

function OrganCtrl ($scope, $http, $routeParams) {

    function recieved_message (message) {
        console.log(message);
        $scope.$apply(function  () {

            if(message.flatline == "resuscitated"){
                $scope.flatlines = $scope.flatlines.filter(function(f) {
                    return f.heart != message.heart;
                });
            } else {
                $scope.flatlines.push({heart:message.heart, title: message.heart, start: message.start, how_long: moment.utc(message.start).fromNow()});
            }
            seticon($scope.flatlines.length);
        });
    }

    var pubnub = PUBNUB.init({ subscribe_key : 'sub-c-c8c9e356-df06-11e2-95e6-02ee2ddab7fe',  ssl  : true });

    pubnub.subscribe({
        channel : "remotex-alerts",
        message : recieved_message
    });


    $scope.organization = $routeParams.organization;
    $http.get("/api/organizations/"+$routeParams.organization).success(function(result) {
        $scope.title = result.title;
        $scope.flatlines = result.flatlines.map(function(f) {
            f.how_long = moment.utc(f.start).fromNow();
            return f;
        });
        $scope.availablility = result.availablility;
        $scope.newhearts = result.newhearts;
        seticon($scope.flatlines.length);
    });
    $scope.flatlines = [];
    $scope.newhearts = [];

    setInterval( function  () {
        $scope.$apply(function  () {
           for (var i = 0; i < $scope.flatlines.length; i++) {
               $scope.flatlines[i].how_long = moment.utc($scope.flatlines[i].start).fromNow();
           }});
    }, 10000);
}

function HeartCtrl ($scope, $http, $routeParams) {

    $scope.updateScheduleInfo = function  () {
        var pulse_moment = moment.utc($scope.last_pulse);
        $scope.last_pulse_text = pulse_moment.fromNow();
        try{
            var schedule = later.parse.cron($scope.cron);
            $scope.cron_guess = moment.utc(later.schedule(schedule).next(1, pulse_moment.toDate())).fromNow();
            $scope.cron_schedule_text = getPrettyCron(schedule.schedules[0]);
            $scope.valid = true;
        } catch(e){
            $scope.valid = false;
        }
        $scope.threshold_text = moment.utc().add('seconds', $scope.threshold).fromNow();
    };

    $http.get("/api/organizations/"+$routeParams.organization+"/hearts/"+$routeParams.heart).success(function(result) {
        $scope.threshold = result.threshold;
        $scope.title = result.title;
        $scope.cron = result.cron;
        $scope.last_pulse = result.last_pulse;
        $scope.time_zone = result.time_zone;
        $scope.updateScheduleInfo();
        $scope.flatlines = result.flatlines.map(function(f) {
            f.duration = f.end != 'None' ? moment(f.end).from(moment(f.start), true) : 'On going';
            f.start = moment.utc(f.start).local().format('YYYY-MM-DD HH:mm');
            if(f.end != 'None'){
                f.end = moment.utc(f.end).local().format('YYYY-MM-DD HH:mm');
            }
            return f;
        });
        $scope.error = false;
    });

    $scope.save = function() {
        $scope.saving = true;
        $scope.saved = false;
        $http.put("/api/organizations/"+$routeParams.organization+"/hearts/"+$routeParams.heart, {title:$scope.title, threshold:$scope.threshold, cron: $scope.cron, time_zone: $scope.time_zone}).success(function(result) {
            $scope.saved = true;
            $scope.saving = false;
            $scope.error = false;
        }).error(function() {
            $scope.error = true;
        });
    };
    $scope.delete = function() {
        $scope.saving = true;
        $scope.saved = false;
        $http.delete("/api/organizations/"+$routeParams.organization+"/hearts/"+$routeParams.heart).success(function(result) {
            $scope.saved = true;
            $scope.saving = false;
            $scope.error = false;
            window.location.pathname = "/app/organizations/"+$routeParams.organization;
        }).error(function() {
            $scope.error = true;
        });
    };
}
