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
		$scope.dangerhearts = result.dangerhearts;
		$scope.warninghearts = result.warninghearts;
		$scope.newhearts = result.newhearts;
	});
	$scope.dangerhearts = [];
	$scope.warninghearts = [];
	$scope.newhearts = [];
}

function HeartCtrl ($scope, $http, $routeParams) {
}
