angular.module('ekg', []).
  config(function($routeProvider) {
    $routeProvider.
      when('/', {controller:ListCtrl, templateUrl:'templates/list.html'}).
      when('/organizations/:organization', {controller:OrganCtrl, templateUrl:'templates/organization.html'}).
      otherwise({redirectTo:'/'});
  });

function ListCtrl ($scope, $http) {
	$scope.organizations = [];
	$scope.organizations.push({name:'Remotex', id:1});
}

function OrganCtrl ($scope) {
	$scope.name = "RemoteX";
	$scope.dangerhearts = [];
	$scope.warninghearts = [];
	$scope.newhearts = [];
}
