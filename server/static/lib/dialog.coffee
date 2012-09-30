module = angular.module "dd4epinboard.dialog", []

module.provider "dialogservice", () ->
    _dialogs = {}

    @addDialog = (dialogId, options) =>
        _dialogs[dialogId] = options

    @$get = ($templateCache, $q, $rootScope) =>
        class DialogService
            showConfirmation: (dialogId) =>
                options = Object.clone(_dialogs[dialogId], true)
                elem = if options.templateUrl?
                    $($templateCache.get(options.templateUrl))
                else
                    $($templateCache.get(options.templateId))

                closeDeferred = $q.defer()
                options.buttons = options.buttons.map (button) ->
                    oldClick = button.click
                    button.click = () ->
                        $rootScope.$apply () ->
                            result = oldClick.apply(this, arguments)
                            if result
                                closeDeferred.resolve(result)
                            else
                                closeDeferred.reject(result)
                    return button

                elem.dialog(options)

                p = closeDeferred.promise.then (result) ->
                    elem.dialog("close")
                    return result
                , (result) ->
                    elem.dialog("close")
                    return $q.reject(result)
                return p

        return new DialogService()
    return
