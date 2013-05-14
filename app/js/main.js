angular.module('ekg', []).
  config(function($routeProvider) {
    $routeProvider.
      when('/', {controller:ListCtrl, templateUrl:'templates/list.html'}).
      when('/organizations/:organization', {controller:OrganCtrl, templateUrl:'templates/organization.html'}).
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

function OrganCtrl ($scope) {
	$scope.name = "RemoteX";
	$scope.dangerhearts = [];
	$scope.warninghearts = [];
	$scope.newhearts = [];
}
