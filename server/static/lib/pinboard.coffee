module = angular.module "dd4epinboard.pinboard", ["dd4epinboard.login", "dd4epinboard.dialog"]

module.factory "pinboardservice", ($http, $rootScope, loginservice) ->
    class PinboardService
        constructor: ->
            @pinboards = {}
            @entryTypeTranslations = {}

        save: (id, name, description, isPublic) =>
            p = $http.put "/pinboards/#{id}",
                operation: "update",
                pinboard:
                    name: name
                    description: description
                    public: isPublic
            return p.then @_updateFromResults

        saveNew: (name, description, isPublic, entries) =>
            p = $http.post "/pinboards/",
                name: name
                description: description
                public: isPublic
            return p.then @_updateFromResults

        update: (id, properties) =>
            p = @load(id)
            p = p.then (pinboard) =>
                @save(
                    id,
                    properties.name ? pinboard.name,
                    properties.description ? pinboard.description,
                    properties.isPublic ? pinboard.public,
                )

        _updateFromResults: (results) =>
            pinboard = results.data?.pinboard
            @_updatePinboardCache(pinboard)
            return pinboard

        _updatePinboardCache: (updatedPinboard) =>
            @pinboards[updatedPinboard.id] = updatedPinboard

        addEntry: (pinboardId, entryType, entryId) =>
            p = $http.put "/pinboards/#{pinboardId}",
                operation: "add_entry"
                entry:
                    entry_type: entryType
                    id: entryId
            return p.then @_updateFromResults

        removeEntry: (pinboardId, entryType, entryId) =>
            p = $http.put "/pinboards/#{pinboardId}",
                operation: "remove_entry"
                entry:
                    entry_type: entryType
                    id: entryId
            return p.then @_updateFromResults

        removePinboard: (pinboardId) =>
            p = $http.delete "/pinboards/#{pinboardId}"
            return p.then @loadAll

        load: (pinboardId) =>
            p = $http.get "/pinboards/#{pinboardId}"
            return p.then (results) =>
                pinboard = results.data?.pinboard
                @_updatePinboardCache(pinboard)

        loadAll: =>
            p = $http.get "/pinboards/"
            return p.then (results) =>
                @pinboards = results.data?.pinboards
                return @pinboards

    return new PinboardService()

module.config (dialogserviceProvider) ->
    dialogserviceProvider.addDialog "pinboardConfirmRemove",
        templateUrl: "/partials/pinboard_remove_confimation_dialog"
        buttons: [
            {
                text: "Yes"
                click: () -> true
            }
            {
                text: "No"
                click: () -> false
            }
        ]

module.controller "PinboardController", ($scope, $rootScope, $routeParams, $location, pinboardservice, loginservice, dialogservice) ->
    # ====================
    # default variables
    # ====================
    $scope.editMode = $routeParams.pinboardId == "new"
    $scope.pinboard = {}

    # ====================
    # methods
    # ====================
    $scope.isNew = ->
        return $routeParams.pinboardId == "new"

    $scope.getMode = ->
        if $scope.editMode
            "edit"
        else
            "view"

    $scope.edit = ->
        $scope.editMode = true

    $scope.save = ->
        if $scope.isNew()
            p = pinboardservice.saveNew(
                $scope.pinboard.name,
                $scope.pinboard.description,
                $scope.pinboard.public,
            )
            p.then (pinboard) ->
                $location.path("/pinboard/#{pinboard.id}")
        else
            p = pinboardservice.save(
                $scope.pinboard.id,
                $scope.pinboard.name,
                $scope.pinboard.description,
                $scope.pinboard.public,
            )
            p.then ->
                $scope.editMode = false

    $scope.load = () ->
        p = pinboardservice.load($routeParams.pinboardId)
        p.then (pinboard) ->
            $scope.pinboard = pinboard

    $scope.remove = () ->
        p = dialogservice.showConfirmation("pinboardConfirmRemove")
        p = p.then () ->
            pinboardservice.removePinboard($scope.pinboard.id)
        p.then ->
            $location.path("/")

    $scope.removeEntryFromPinboard = (pinboard, entry) ->
        p = pinboardservice.removeEntry(pinboard.id, entry.entry_type, entry.id)
        p.then (pinboard) ->
            $scope.pinboard = pinboard

    $scope.translateEntryType = (entryType) ->
        if entryType of pinboardservice.entryTypeTranslations
            pinboardservice.entryTypeTranslations[entryType]
        else
            if entryType?
                entryType.capitalize()
            else
                "None"
        
    # ====================
    # events
    # ====================
    $rootScope.$on "LoginSuccessful", ->
        if not $scope.isNew()
            $scope.load()

    # ====================
    # init
    # ====================
    if not $scope.isNew() and loginservice.isLoggedIn()
        $scope.load()
