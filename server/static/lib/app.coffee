app = angular.module "dd4epinboard", ["dd4epinboard.login", "dd4epinboard.search", "dd4epinboard.entry", "dd4epinboard.pinboard"]

loggedInPromise = ($q, loginservice) ->
    result = $q.defer()
    loginservice.initialized.then ->
        if loginservice.isLoggedIn()
            result.resolve(true)
        else
            result.reject("notLoggedIn")
    return result.promise

app.config ($interpolateProvider, $routeProvider, dialogserviceProvider) ->
    $interpolateProvider.startSymbol("{+")
    $interpolateProvider.endSymbol("+}")

    $routeProvider.when "/search/:searchEntryType",
        templateUrl: "/partials/search_main"
        controller: "SearchController"
        reloadOnSearch: false
        resolve:
            login: loggedInPromise        
    $routeProvider.when "/pinboard/:pinboardId",
        templateUrl: "/partials/pinboard_main"
        controller: "PinboardController"
        resolve:
            login: loggedInPromise        
    $routeProvider.when "/entry/:entryType/:entryId",
        templateUrl: "/partials/entry_main"
        controller: "EntryController"
        resolve:
            login: loggedInPromise        
    $routeProvider.when "/login",
        templateUrl: "/partials/login"
        controller: "AuthController"
    $routeProvider.otherwise
        redirectTo: "/search/class"

app.controller "MainController", ($scope, $route, $location, loginservice) ->
    $scope.$on "$routeChangeError", (event, d, u, reason) ->
        if reason == "notLoggedIn"
            destinationUrl = $location.url()
            $location.path("/login")
            $location.search
                destination: destinationUrl

    $scope.isOwnPinboard = (pinboard) ->
        return loginservice.isOwnPinboard(pinboard)

app.controller "NavbarController", ($scope, $rootScope, $routeParams, loginservice, pinboardservice) ->
    $scope.getOwnPinboards = ->
        return (pinboard for id, pinboard of pinboardservice.pinboards when loginservice.isOwnPinboard(pinboard))

    $scope.getOtherPinboards = ->
        return (pinboard for id, pinboard of pinboardservice.pinboards when not loginservice.isOwnPinboard(pinboard))

    $scope.isSearchType = (type) ->
        $routeParams?.searchEntryType == type

    # ====================
    # watches
    # ====================
    $rootScope.$on "LoginSuccessful", ->
        pinboardservice.loadAll().then (pinboards) ->
            $scope.pinboards = pinboards

    if loginservice.isLoggedIn()
        pinboardservice.loadAll().then (pinboards) ->
            $scope.pinboards = pinboards

app.filter "pluck", () ->
    (input, predicate) ->
        if input?
            input.map(predicate)
        else
            []

app.filter "unique", () ->
    (input) ->
        if input?
            input.unique()
        else
            []

app.filter "order", () ->
    (input, predicate) ->
        if input?
            input.sortBy(predicate)
        else
            []

app.filter "groupBy", ->
    (input, predicate) ->
        if input?
            input.groupBy(predicate)
        else
            {}
