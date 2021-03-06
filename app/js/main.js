angular.module('ekg', ['ui.bootstrap']).
config(function($locationProvider, $routeProvider) {
    $locationProvider.html5Mode(true);
    $routeProvider.
    when('/app/', {controller:ListCtrl, templateUrl:'/app/templates/list.html'}).
    when('/app/organizations/:organization/config', {controller:DetailsCtrl, templateUrl:'/app/templates/config.html'}).
    when('/app/organizations/:organization', {controller:OrganCtrl, templateUrl:'/app/templates/organization.html'}).
    when('/app/organizations/:organization/report', {controller:ReportCtrl, templateUrl:'/app/templates/report.html'}).
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
        $scope.organization = result.organization;
        $scope.hearts = result.hearts.map(function(h) {
            h.last_pulse = moment.utc(h.last_pulse).local().format('YYYY-MM-DD HH:mm');
            return h;
        });
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

function ReportCtrl ($scope, $http, $routeParams) {
    $scope.organization = $routeParams.organization;
    $http.get("/api/organizations/"+$routeParams.organization+'/report').success(function(result) {
        $scope.organization = result.organization;
        $scope.availablility = result.availablility;
        $scope.hearts = result.hearts;
        $scope.flatlines = result.flatlines.map(function(f) {
            f.duration = f.end != 'None' ? moment(f.end).from(moment(f.start), true) : 'On going';
            f.start = moment.utc(f.start).local().format('YYYY-MM-DD HH:mm');
            if(f.end != 'None'){
                f.end = moment.utc(f.end).local().format('YYYY-MM-DD HH:mm');
            }
            return f;
        }).sort(function(a,b){return a.start-b.start;});
        $scope.flatcount = $scope.flatlines.length;
    });
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
        $scope.maintenancehearts = result.maintenancehearts;
        $scope.flatlines = result.flatlines.map(function(f) {
            f.how_long = moment.utc(f.start).fromNow();
            return f;
        });
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
        try{
            var next_moment = moment.tz( moment( prettyCron.getNextDate($scope.cron) ).tz('UTC').format('YYYY-MM-DD HH:mm:ss'), $scope.time_zone );
            $scope.cron_guess = $scope.cron == '' ? 'No cron schedule given' : 'Next heartbeat is expected at: ' + next_moment.format( 'YYYY-MM-DD HH:mm Z') + ' (' + next_moment.fromNow() + ')';
            $scope.cron_schedule_text = prettyCron.toString($scope.cron);
            if( new Date($scope.maintenance_day).setHours(0,0,0,0) === new Date().setHours(0,0,0,0) ) {
                $scope.today_is_maintenance_day = moment($scope.maintenance_day).format("[Important! Today,] YYYY-MM-DD[, is maintenance day]");
                $scope.today_is_maintenance_day_note = "By making today a maintenance day will deactivate a flatline that are in progress for this heart!";
            } else {
                $scope.today_is_maintenance_day = "";
                $scope.today_is_maintenance_day_note = "";
            }
            $scope.valid = true;
        } catch(e){
            $scope.valid = false;
        }
        $scope.threshold_text = moment.utc().add('seconds', $scope.threshold).fromNow();
    };

    $scope.load = function() {
        $http.get("/api/organizations/"+$routeParams.organization+"/hearts/"+$routeParams.heart).success(function(result) {
            $scope.threshold = result.threshold;
            $scope.organization = result.organization;
            $scope.title = result.title;
            $scope.cron = result.cron;
            $scope.last_pulse = result.last_pulse;
            $scope.last_closed_by = result.last_closed_by;
            $scope.time_zone = result.time_zone;
            $scope.maintenance_day = result.maintenance_day;
            $scope.flatline_guess_text = result.cron == '' ? 'No cron schedule given' : 
                moment.utc(result.calculated_flatline).tz($scope.time_zone).format(
                    '[If no heartbeat is recorded before] ' + 
                    'YYYY-MM-DD HH:mm Z' + 
                    '[ (' + moment.utc(result.calculated_flatline).tz($scope.time_zone).fromNow() + ')]' +
                    '[, a flatline will be created and alerts will be sent.]');
            $scope.updateScheduleInfo();
            var pulse_moment = moment.utc($scope.last_pulse);
            $scope.last_pulse_text = pulse_moment.fromNow();
            $scope.flatlines = result.flatlines.map(function(f) {
                var start_moment = moment.utc(f.start).local();
                var end = f.end;

                if( end === 'None' ) {
                    f.duration = 'On going';
                    f.end = '-';
                    $scope.flatline_text = '';
                } else {
                    f.duration = moment(f.end).from(moment(f.start), true);
                    f.end = moment.utc(f.end).local().format('YYYY-MM-DD HH:mm Z');
                }

                f.start = start_moment.format('YYYY-MM-DD HH:mm Z');

                return f;
            });
            $scope.error = false;
        });
    };
    $scope.load();

    $scope.save = function() {
        $scope.saving = true;
        $scope.saved = false;
        $http.put("/api/organizations/"+$routeParams.organization+"/hearts/"+$routeParams.heart, {title:$scope.title, threshold:$scope.threshold, cron: $scope.cron, time_zone: $scope.time_zone, maintenance_day: $scope.maintenance_day ? moment($scope.maintenance_day).format("YYYY-MM-DD") : ''}).success(function(result) {
            $scope.saved = true;
            $scope.saving = false;
            $scope.error = false;
            $scope.load();
        }).error(function() {
            $scope.error = true;
        });
    };
    $scope.delete = function() {
        $scope.deleting = true;
        $scope.deleted = false;
        $http.delete("/api/organizations/"+$routeParams.organization+"/hearts/"+$routeParams.heart).success(function(result) {
            $scope.deleted = true;
            $scope.deleting = false;
            $scope.error = false;
            window.location.pathname = "/app/organizations/"+$routeParams.organization;
        }).error(function() {
            $scope.error = true;
        });
    };
}
