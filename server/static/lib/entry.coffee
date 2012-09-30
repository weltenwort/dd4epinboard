module = angular.module "dd4epinboard.entry", []

module.controller "EntryController", ($scope, $routeParams, pinboardservice) ->
    # ====================
    # methods
    # ====================
    $scope.getEntryType = ->
        $routeParams.entryType

    $scope.getEntryId = ->
        $routeParams.entryId.toNumber()

    $scope.isEntryInPinboard = (pinboard) ->
        pinboard?.entries.any
            id: $scope.getEntryId()
            entry_type: $scope.getEntryType()

    $scope.addEntryToPinboard = (pinboard) ->
        pinboardservice.addEntry(pinboard.id, $scope.getEntryType(), $scope.getEntryId())

    $scope.removeEntryFromPinboard = (pinboard) ->
        pinboardservice.removeEntry(pinboard.id, $scope.getEntryType(), $scope.getEntryId())
