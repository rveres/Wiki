$(function () {
    var originalText = $('#editContent').val();
    var urlEdit = window.location.pathname;
    var correctUrl = urlEdit.replace('_edit/', '');

    $('#editForm').submit(function (event) {
        if ($('#editContent').val() == originalText) {
            event.preventDefault();
            window.location.replace(correctUrl);
        }
    });
});