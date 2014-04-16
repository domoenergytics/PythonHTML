function teleinfoCtrl($scope, $http, $timeout) {
	$scope.x = 0;

	$scope.draw = function() {
		if (contextCanvas!=null) {
			// -- coordonnees x,y courantes
			$scope.x += 1; // pas de 1 pixel a la fois 
			if ($scope.x > canvas.width) {
				decal = 200;
				var imgData = contextCanvas.getImageData(decal, 0, canvas.width, canvas.height);
				contextCanvas.putImageData(imgData,0,0);
				$scope.x -= decal;
				xo -= decal;
				contextCanvas.fillStyle = "rgb(255,255,200)";
				contextCanvas.fillRect (canvas.width - decal, 0, canvas.width, canvas.height); 
				drawGuides(decal);
			} // fin if x>canvas.width
			y = $scope.data.pa;  // recupere la valeur chiffrÃ©e Ã  partir chaine recue
			y = y/maxVA*(canvas.height-1) // y mappee sur la hauteur canvas
			// -- trace la courbe --                  
			if ($scope.x == 1) {
				yo = y;
			}
			contextCanvas.beginPath(); 
			contextCanvas.moveTo(xo, canvas.height-yo-1);
			contextCanvas.lineTo($scope.x, canvas.height-y-1);               
			contextCanvas.closePath(); 
			contextCanvas.stroke();
			xo = $scope.x;
			yo = y;
		}
	}
	
	$scope.getJson = function() {
		$http({method: 'GET', url: '/teleinfo/json'}).
		success(function(data, status) {
			$scope.status = status;
			$scope.data = data;
			$scope.cumul = eval(data.idxA) + eval(data.idxB) + eval(data.idxC) + eval(data.idxD);
			$scope.draw();
		}).
		error(function(data, status) {
			$scope.status = '??';
		});
		$timeout($scope.getJson, 60200);
	};
}

