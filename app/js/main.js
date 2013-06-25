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
    });
    $scope.send = function() {
        $scope.sending = true;
        $http.post('/api/invitations/', {organization: $routeParams.organization, email: $scope.email}).success(function() {
            $scope.sent = true;
            $scope.sending = false;
        });
    };
}

function OrganCtrl ($scope, $http, $routeParams) {
    $scope.organization = $routeParams.organization;
    $http.get("/api/organizations/"+$routeParams.organization).success(function(result) {
        $scope.title = result.title;
        $scope.flatlines = result.flatlines.map(function(f) {
            f.how_long = moment.utc(f.start).fromNow();
            return f;
        });
        $scope.newhearts = result.newhearts;
    });
    $scope.flatlines = [];
    $scope.newhearts = [];
}

function HeartCtrl ($scope, $http, $routeParams) {

    $scope.updateScheduleInfo = function  () {
        $scope.last_pulse_text = moment.utc($scope.last_pulse).fromNow();
        try{
            var schedule = later.parse.cron($scope.cron);
            $scope.cron_guess = moment.utc(later.schedule(schedule).next(1, $scope.last_pulse)).fromNow();
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
        $scope.updateScheduleInfo();
        $scope.flatlines = result.flatlines.map(function(f) {
            f.duration = f.end != 'None' ? moment(f.end).from(moment(f.start), true) : 'On going';
            return f;
        });
        $scope.error = false;
    });

    $scope.save = function() {
        $scope.saving = true;
        $scope.saved = false;
        $http.put("/api/organizations/"+$routeParams.organization+"/hearts/"+$routeParams.heart, {title:$scope.title, threshold:$scope.threshold, cron: $scope.cron}).success(function(result) {
            $scope.saved = true;
            $scope.saving = false;
            $scope.error = false;
        }).error(function() {
            $scope.error = true;
        });
    };
}
