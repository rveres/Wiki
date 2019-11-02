$(document).ready(function () {
    $('#redirbut2').click(function () {
        window.location.href = "/login";
    });

    $('input[type="text"], input[type="password"]').focus(function () {
        $('#' + $(this).next('label').text().toLowerCase() + 'Error').text('');
    }).blur(function () {
        var field = $(this).next('label').text().toLowerCase();
        if ($(this).val().length < 5) {
            if (field == 'verify') {
                if ($('#password').val() !== $('#verify').val()) {
                    $('#verifyError').text('Your passwords don\'t match');
                    return;
                }
                return;
            }
            $('#' + field + 'Error').text('That ' + field + ' is not long enough');
            $('#submitbut').attr("disabled", "disabled");
        }
        else if ($('#username').val().length >= 5 && $('#password').val().length >= 5 && $('#verify').val().length >= 5) {
            $('#submitbut').attr("disabled", false);
        }
    });

    $('#signupform').submit(function () {
        if ($('#password').val() !== $('#verify').val()) {
            $('#verifyError').text('Your passwords didn\'t match');
            return false;
        }
    });
});