module = angular.module "dd4epinboard.search", []

module.factory "searchservice", ($http, $rootScope) ->
    wrapLike = (value) ->
        if value
            "%#{value}%"
        else
            null

    nullVal = (data) -> data.val? and data.val != ""

    class SearchService
        constructor: ->
            @objects = []
            @page = 1
            @totalPages = 0
            @filterOptions = {}

        performSearch: (query) =>
            query.page ?= 1

            p = $http.post "/entry/#{query.type}",
                query: angular.toJson(query.query)
                page: query.page
            return p

        searchFeat: (name, tier, page=1) =>
            @performSearch
                type: "feat"
                page: page
                query:
                    filters: [
                        {name: "name", op: "like", val: wrapLike(name)}
                        {name: "tier", op: "eq", val: tier}
                    ].filter(nullVal)

        searchDeity: (name, alignment, page=1) =>
            @performSearch
                type: "deity"
                page: page
                query:
                    filters: [
                        {name: "name", op: "like", val: wrapLike(name)}
                        {name: "alignment", op: "eq", val: alignment}
                    ].filter(nullVal)

        searchClass: (name, role, powersource, page=1) =>
            @performSearch
                type: "class"
                page: page
                query:
                    filters: [
                        {name: "name", op: "like", val: wrapLike(name)}
                        {name: "role", op: "eq", val: role}
                        {name: "powersource", op: "eq", val: powersource}
                    ].filter(nullVal)

        searchMonster: (name, level, grouprole, page=1) =>
            @performSearch
                type: "monster"
                page: page
                query:
                    filters: [
                        {name: "name", op: "like", val: wrapLike(name)}
                        {name: "level", op: "eq", val: level}
                        {name: "grouprole", op: "eq", val: grouprole}
                    ].filter(nullVal)

        searchPower: (name, classname, min_level, max_level, actiontype, usagetype, page=1) =>
            @performSearch
                type: "power"
                page: page
                query:
                    filters: [
                        {name: "name", op: "like", val: wrapLike(name)}
                        {name: "classname", op: "eq", val: classname}
                        {name: "level", op: "geq", val: min_level}
                        {name: "level", op: "leq", val: max_level}
                        {name: "actiontype", op: "eq", val: actiontype}
                        {name: "usagetype", op: "eq", val: usagetype}
                    ].filter(nullVal)

        searchItem: (name, min_cost, max_cost, min_level, max_level, category, page=1) =>
            category_filter = if not category? then [] else [
                {name: "magical", op: "eq", val: category.split("|")[0] == "Magical"}
                {name: "category", op: "eq", val: category.split("|")[1]}
            ]
            @performSearch
                type: "item"
                page: page
                query:
                    filters: [
                        {name: "name", op: "like", val: wrapLike(name)}
                        {name: "cost", op: "geq", val: min_cost}
                        {name: "cost", op: "leq", val: max_cost}
                        {name: "level", op: "geq", val: min_level}
                        {name: "level", op: "leq", val: max_level}
                    ].include(category_filter).filter(nullVal)

        searchGlossary: (name, category, type, page=1) =>
            @performSearch
                type: "glossary"
                page: page
                query:
                    filters: [
                        {name: "name", op: "like", val: wrapLike(name)}
                        {name: "category", op: "eq", val: category}
                        {name: "glossarytype", op: "eq", val: type}
                    ].filter(nullVal)

        searchRace: (name, page=1) =>
            @performSearch
                type: "race"
                page: page
                query:
                    filters: [
                        {name: "name", op: "like", val: wrapLike(name)}
                    ].filter(nullVal)

        searchRitual: (name, min_cost, max_cost, min_level, max_level, keyskill, page=1) =>
            @performSearch
                type: "ritual"
                page: page
                query:
                    filters: [
                        {name: "name", op: "like", val: wrapLike(name)}
                        {name: "cost", op: "geq", val: min_cost}
                        {name: "cost", op: "leq", val: max_cost}
                        {name: "level", op: "geq", val: min_level}
                        {name: "level", op: "leq", val: max_level}
                        {name: "keyskill", op: "eq", val: keyskill}
                    ].filter(nullVal)

        loadOptions: =>
            p = $http.get("/filter/")
            p.then (results) =>
                Object.merge(@filterOptions, results.data.options, false, true)
            return p


    return new SearchService()

module.controller "SearchController", ($scope, $routeParams, $location, $rootScope, searchservice) ->
    # ====================
    # default variables
    # ====================
    $scope.searchParameters =
        page: 1

    $scope.searchResults =
        objects: []
        page: 1
        totalPages: 0

    $scope.filterOptions = searchservice.filterOptions

    $scope.pageRange = []

    # ====================
    # methods
    # ====================
    $rootScope.updateLocation = ()->
        $location.search("searchParameters", angular.toJson($scope.searchParameters).escapeURL())

    $scope.getSearchEntryType = ->
        $routeParams.searchEntryType

    $scope.getEntries = ->
        $scope.searchResults.objects

    $scope.getTotalPageCount = ->
        $scope.searchResults.totalPages

    $scope.getCurrentPage = ->
        $scope.searchResults.page

    $scope.getPageRange = ->
        $scope.pageRange

    $scope.setCurrentPage = (page) ->
        if Object.isNumber(page)
            if 1 <= page <= $scope.getTotalPageCount() and page != $scope.getCurrentPage()
                $scope.searchParameters.page = page
                $scope.search()

    $scope.search = (newSearch=false)->
        fn = $scope.searches[$routeParams.searchEntryType]
        if Object.isFunction(fn)
            if newSearch
                $scope.searchParameters.page = 1
            $rootScope.$broadcast("SearchStart")
            p = fn()
            p.then (results) ->
                data = results.data
                $scope.searchResults.page = data.page
                $scope.searchResults.totalPages = data.total_pages
                $scope.searchResults.objects = data.objects
                $rootScope.$broadcast("SearchSuccess")

    $scope.searches = 
        feat: ->
            searchservice.searchFeat(
                $scope.searchParameters.term,
                $scope.searchParameters.featTier,
                $scope.searchParameters.page,
            )
        deity: ->
            searchservice.searchDeity(
                $scope.searchParameters.term,
                $scope.searchParameters.deityAlignment
                $scope.searchParameters.page,
            )
        class: ->
            searchservice.searchClass(
                $scope.searchParameters.term,
                $scope.searchParameters.classRole,
                $scope.searchParameters.classPowersource,
                $scope.searchParameters.page,
            )
        monster: ->
            searchservice.searchMonster(
                $scope.searchParameters.term,
                $scope.searchParameters.monsterLevel,
                $scope.searchParameters.monsterGroupRole,
                $scope.searchParameters.page,
            )
        power: ->
            searchservice.searchPower(
                $scope.searchParameters.term,
                $scope.searchParameters.powerClass,
                $scope.searchParameters.powerLevelMinimum,
                $scope.searchParameters.powerLevelMaximum,
                $scope.searchParameters.powerAction,
                $scope.searchParameters.powerUsage,
                $scope.searchParameters.page,
            )
        item: ->
            searchservice.searchItem(
                $scope.searchParameters.term,
                $scope.searchParameters.itemCostMinimum,
                $scope.searchParameters.itemCostMaximum,
                $scope.searchParameters.itemLevelMinimum,
                $scope.searchParameters.itemLevelMaximum,
                $scope.searchParameters.itemCategory,
                $scope.searchParameters.page,
            )
        glossary: ->
            searchservice.searchGlossary(
                $scope.searchParameters.term,
                $scope.searchParameters.glossaryCategory,
                $scope.searchParameters.glossaryType,
                $scope.searchParameters.page,
            )
        race: ->
            searchservice.searchRace(
                $scope.searchParameters.term,
                $scope.searchParameters.page,
            )
        ritual: ->
            searchservice.searchRitual(
                $scope.searchParameters.term,
                $scope.searchParameters.ritualCostMinimum,
                $scope.searchParameters.ritualCostMaximum,
                $scope.searchParameters.ritualLevelMinimum,
                $scope.searchParameters.ritualLevelMaximum,
                $scope.searchParameters.ritualKeyskill,
                $scope.searchParameters.page,
            )

    $scope.loadOptions = ->
        p = searchservice.loadOptions()

    # ==================== 
    # watches
    # ====================
    $scope.$watch (scope) ->
        return [$scope.getCurrentPage(), $scope.getTotalPageCount()]
    , (newValue, oldValue, scope) ->
        [page, totalPages] = newValue

        if totalPages > 9
            pageRange_start = Math.min(Math.max(4, page)-2, totalPages-6)
            pageRange_end = Math.max(Math.min(totalPages-4, page)+2, 7)
            pageRange = [1].concat([pageRange_start..pageRange_end]).concat([totalPages])
            pageRange = pageRange.reduce(((memo, item) ->
                if memo.length > 0
                    if memo.last().label != (item - 1)
                        if memo.last().label == (item - 2)
                            memo.push
                                label: item - 1
                                active: item - 1 == page
                                disabled: false
                        else
                            memo.push
                                label: "..."
                                active: false
                                disabled: true
                memo.push
                    label: item
                    active: item == page
                    disabled: false
                return memo
            ), [])
        else if totalPages == 0
            pageRange = []
        else
            pageRange = ({label: item, active: item == page, disabled: false} for item in [1..totalPages])
        $scope.pageRange = pageRange
    , true
        
    # ====================
    # events
    # ====================
    $rootScope.$on("SearchStart", -> $scope.updateLocation())
    $rootScope.$on("LoginSuccessful", -> $scope.loadOptions())

    # ====================
    # init
    # ====================
    # populate search form model from query string
    locQuery = $location.search()["searchParameters"]
    try
        Object.merge($scope.searchParameters, angular.fromJson(locQuery.unescapeURL()))
        if locQuery? and locQuery.length > 0
            $scope.search()
    catch e
