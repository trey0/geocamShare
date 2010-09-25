// __BEGIN_LICENSE__
// Copyright (C) 2008-2010 United States Government as represented by
// the Administrator of the National Aeronautics and Space Administration.
// All Rights Reserved.
// __END_LICENSE__

$extend(geocamShare.core,
{
    ajaxFormSuccessFnG: null,

    ajaxFormSubmitHandler: function (formData, jqForm, options) {
        // clear old errors
        var fields = jqForm.serializeArray();
        $.each(fields,
               function (i, nameVal) {
                   $('#' + nameVal.name + '_error').html('');
               });

        // notify user save is in progress
        $('#ajaxFormEditStatus').html('<div class="pendingStatus">'
			              + geocamShare.core.getLoadingIcon()
                                      + '<span style="vertical-align: middle;">Saving your changes.</span>'
			              + '</div>');
    },

    ajaxFormResponseHandler: function (responseJson, statusText, xhr) {
        if (responseJson.error == null) {
            $('#ajaxFormEditStatus').html('<div class="successStatus">'
                                          + 'Your changes were saved.'
                                          + '</div>');
            if (geocamShare.core.ajaxFormSuccessFnG != undefined) {
                geocamShare.core.ajaxFormSuccessFnG(responseJson[1]);
            }
        } else {
            $('#ajaxFormEditStatus').html('<div class="errorStatus">Please correct the errors below.</div>');
            $.each(responseJson.error.data,
                   function (name, errors) {
                       $('#' + name + '_error').html('<div class="formError">' + errors.join('<br/>') + '</div>');
                   });
        }
    },

    ajaxFormErrorHandler: function (xhr, ajaxOptions, thrownError) {
        $('#ajaxFormEditStatus').html('<div class="errorStatus">Could not save changes: '
                                      + xhr.status + ' ' + xhr.statusText + '</div>');
    },

    ajaxFormInit: function (domId, successFn) {
        // gross
        geocamShare.core.ajaxFormSuccessFnG = successFn;

        $('#' + domId).ajaxForm({
            beforeSubmit: geocamShare.core.ajaxFormSubmitHandler,
            success: geocamShare.core.ajaxFormResponseHandler,
            error: geocamShare.core.ajaxFormErrorHandler,
            dataType: 'json',
            data: { 'ajax': 1 }
        });
    }

});
