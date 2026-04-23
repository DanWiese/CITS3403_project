import $ from 'https://cdn.jsdelivr.net/npm/jquery@latest/+esm';

$(document).ready(function(){
    // Prefill form fields from URL parameters
    const urlParams = new URLSearchParams(window.location.search);

    // Prefill text inputs
    $('#eventName').val(urlParams.get('eventName') || '');
    $('#location').val(urlParams.get('location') || '');
    $('#startDate').val(urlParams.get('startDate') || '');
    $('#startTime').val(urlParams.get('startTime') || '');
    $('#finishDate').val(urlParams.get('finishDate') || '');
    $('#finishTime').val(urlParams.get('finishTime') || '');
    $('#description').val(urlParams.get('description') || '');

    // Prefill checkboxes
    if (urlParams.get('polls') === 'true') {
        $('#pollsCheckbox').prop('checked', true).prop('disabled', true);
    }
    if (urlParams.get('expenses') === 'true') {
        $('#expensesCheckbox').prop('checked', true).prop('disabled', true);
    }
    if (urlParams.get('discussion') === 'true') {
        $('#discussionCheckbox').prop('checked', true).prop('disabled', true);
    }

    // Prefill radio buttons
    const eventType = urlParams.get('eventType');
    if (eventType === 'public') {
        $('input[name="optradio"][value="public"]').prop('checked', true);
    } else {
        $('input[name="optradio"][value="private"]').prop('checked', true);
    }
});

