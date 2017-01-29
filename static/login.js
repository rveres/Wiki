$(document).ready(function() {
    $('#loginform').submit(function() {
        if ($('#username').val() == '' && $('#password').val() == '') {
            $('#error').text('Invalid username and password');
            return false;
        }
        else if ($('#username').val() == '') {
            $('#error').text('Invalid username');
            return false;
        }
        else if ($('#password').val() == '') {
            $('#error').text('Invalid password');
            return false;
        }
        else {
            return true;
        }
    });

    $('#username').focus(function () {
        $('#usrError').text('');
    }).blur(function () {
        if ($(this).val().length < 5) {
            $('#pswError').text('');
            $('#usrError').text('That ' + $(this).next('label').text().toLowerCase() + ' is not long enough');
        }
        else if ($('#username').val().length >= 5 && $('#password').val().length >= 5) {
                $('#submitbut').attr("disabled", false);
        }
    });

    $('#password').focus(function () {
        $('#pswError').text('');
    }).blur(function () {
        if ($(this).val().length < 5) {
            $('#usrError').text('');
            $('#pswError').text('That ' + $(this).next('label').text().toLowerCase() + ' is not long enough');
        }
        else if ($('#username').val().length >= 5 && $('#password').val().length >= 5) {
                $('#submitbut').attr("disabled", false);
        }
    });

    $('#redirbut').click(function () {
        window.location.href = "/signup";
    });

});