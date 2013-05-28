angular.module('ekg', []).
config(function($locationProvider, $routeProvider) {
	$locationProvider.html5Mode(true);
	$routeProvider.
	when('/app/', {controller:ListCtrl, templateUrl:'/app/templates/list.html'}).
	when('/app/organizations/:organization/config', {controller:DetailsCtrl, templateUrl:'/app/templates/config.html'}).
	when('/app/organizations/:organization', {controller:OrganCtrl, templateUrl:'/app/templates/organization.html'}).
	when('/app/organizations/:organization/:heart', {controller:HeartCtrl, templateUrl:'/app/templates/heart.html'}).
	when('/app/invitations/:invite', {controller:InviteCtrl, templateUrl:'/app/templates/invite.html'}).
	otherwise({redirectTo:'/app/'});
});

function InviteCtrl ($scope, $http, $routeParams) {
	$http.get("/api/invitations/"+$routeParams.invite).success(function(result) {
		$scope.title = result.title;
	});

	$scope.accept = function() {
		$http.get("/api/invitations/"+routeParams.invite+"/accept").success(function() {
			$scope.accepted = true;
			$scope.answered = true;
		});
	};

	$scope.decline = function() {
		$http.get("/api/invitations/"+routeParams.invite+"/decline").success(function() {
			$scope.accepted = false;
			$scope.answered = true;
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

	$http.get("/api/organizations/"+$routeParams.organization+"/hearts/"+$routeParams.heart).success(function(result) {
		$scope.threshold = result.threshold;
		$scope.title = result.title;
		$scope.last_pulse = result.last_pulse;
		$scope.last_pulse_text = moment.utc(result.last_pulse).fromNow();
	});

	$scope.save = function() {
		$scope.saving = true;
		$scope.saved = false;
		$http.put("/api/organizations/"+$routeParams.organization+"/hearts/"+$routeParams.heart, {title:$scope.title, threshold:$scope.threshold}).success(function(result) {
			$scope.saved = true;
			$scope.saving = false;
		});
	};
}
