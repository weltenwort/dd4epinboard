module = angular.module "dd4epinboard.login", []

module.factory "loginservice", ($http, $q, $rootScope) ->
    class LoginService
        constructor: () ->
            @initDeferred = $q.defer()
            @initialized = @initDeferred.promise
            @session =
                username: null
            @getSession()

        isLoggedIn: () =>
            return @session.username != null

        login: (username, password) =>
            p = $http.post "session",
                username: username
                password: password
            p.then (data) =>
                @updateSession(data.data)
            return p

        logout: () =>
            p = $http.delete "session"
            p.then (data) =>
                @updateSession(data.data)
            return p

        getSession: () =>
            p = $http.get "session"
            p.success @updateSession
            return p
        
        updateSession: (data) =>
            old_username = @session.username
            for key, value of @session
                @session[key] = undefined
            @session.username = data.username
            @initDeferred.resolve(true)

            if @session.username? and old_username != @session.username
                $rootScope.$broadcast("LoginSuccessful")

        isOwnPinboard: (pinboard) =>
            return pinboard.owner_username == @session.username

    new LoginService()

module.controller "AuthController", ($scope, $location, $rootScope, loginservice) ->
    $scope.session = loginservice.session
    $scope.authMessage = "Authentication required"

    $scope.isAuthenticated = () ->
        loginservice.isLoggedIn()

    $scope.login = (username, password) ->
        destination = $location.search().destination || "/"
        p = loginservice.login(username, password)
        
        p.then ->
            $location.url(destination)
        , (data) ->
            switch data.data.reason
                when "invalid_username_or_password"
                    $scope.authMessage = "Invalid username or password, please try again."
                else
                    $scope.authMessage = "An unknown error occurred, please try again."

    $scope.logout = () ->
        p = loginservice.logout()
        p.then ->
            $location.url("/")

    $scope.isOwnPinboard = (pinboard) ->
        return loginservice.isOwnPinboard(pinboard)
