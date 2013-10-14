 
function pingCtrlPc($scope, $http, $timeout) {
	$scope.statut = '--';
	$scope.ip = '--';
	$scope.getJson = function() {
		$http({method: 'GET', url: 'json/pc'}).
		success(function(data, status) {
			$scope.status = status;
			$scope.data = data;
		}).
		error(function(data, status) {
			$scope.status = '??';
		});
		$timeout($scope.getJson, 120000);
	};
}
