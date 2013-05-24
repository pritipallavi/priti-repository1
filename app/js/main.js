angular.module('ekg', []).
  config(function($routeProvider) {
    $routeProvider.
      when('/', {controller:ListCtrl, templateUrl:'templates/list.html'}).
      when('/organizations/:organization', {controller:OrganCtrl, templateUrl:'templates/organization.html'}).
      when('/organizations/:organization/:heart', {controller:HeartCtrl, templateUrl:'templates/heart.html'}).
      otherwise({redirectTo:'/'});
  });

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
