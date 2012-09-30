module = angular.module "dd4epinboard.configuration", ["ngCookies", "dd4epinboard.login"]

module.controller "AuthController", ($scope, $log, $rootScope, loginservice) ->
    $scope.session = loginservice.session
    $scope.authMessage = "Authentication required"

    $scope.isAuthenticated = () ->
        loginservice.isLoggedIn()

    $scope.login = (username, password) ->
        p = loginservice.login(username, password)

    $scope.logout = () ->
        p = loginservice.logout()
