$(document).ready(function () {
    $('#redirbut2').click(function () {
        window.location.href = "/login";
    });

    $('#verify').keyup(function () {
        if ($('#password').val() !== $(this).val()) {
            $('#verifyError').text('Your passwords don\'t match');
            $('#submitbut').attr("disabled", "disabled");
        }
        else if ($('#password').val() == $(this).val()) {
            $('#verifyError').text('');
        }
    });

    $('input[type="text"], input[type="password"]').focus(function () {
        $('#' + $(this).next('label').text().toLowerCase() + 'Error').text('');
    }).blur(function () {
        var field = $(this).next('label').text().toLowerCase();
        if (field == 'verify') {
            if ($('#password').val() !== $('#verify').val()) {
                $('#verifyError').text('Your passwords don\'t match');
                return;
            }
            else {
               $('#verifyError').text('');
               $('#submitbut').attr("disabled", false);
            }
        }
        else if ($(this).val().length < 5) {
            if (field == 'verify') {
                $('#' + field + 'Error').text('That\'s not long enough');
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