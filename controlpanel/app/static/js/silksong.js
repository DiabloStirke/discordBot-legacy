
function formatDate(date){
    let month = date.toLocaleString('en-UK', { month: 'long' });
    let day = date.getDate();
    let year = date.getFullYear();
    return month + " " + ordinal(day) + " " + year;
}

function formatNewsDateMessage(date){
    let formatted_date = formatDate(date);
    let today = new Date();
    let msg = `Today is ${formatted_date}. There are silksong news today! `;
    if (daysBetween(date, today) === 1){
        msg = `Yesterday was ${formatted_date}. There were silksong news yesterday! `;
    }
    else if (daysBetween(date, today) > 1){
        msg = `The date was ${formatted_date}. There were silksong news on that day! `;
    }
    return msg;
}

$(function() {

    // Paste clipboard data as plain text
    $(document).on('paste', 'p[contenteditable]', function(e) {
        e.preventDefault();
        const clipboardData = e.clipboardData || e.originalEvent.clipboardData || window.clipboardData;
        const text = clipboardData.getData('text/plain');
        const selection = window.getSelection()
        range = selection.getRangeAt(0);
        range.deleteContents();
        range.insertNode(document.createTextNode(text));
        selection.collapseToEnd();
        console.log(text);
    });

    // Preview button click handler
    $(".dc-embed-preview-btn").click(function(e) {
        const preview_btn_id = "#" + this.id;
        const embed_id = "#" + this.id.replace(/-preview-btn$/, '');
        const edit_btn_id = embed_id + '-edit-btn';
        const date_btn_id = embed_id + '-date-btn';

        let html = $(embed_id).html()
        let original_data = html.replace(/<br>$/, '').replaceAll(/<br>/g, '\n');
        original_data = removeTags(original_data);
        
        html = compileMarkdown(html);
        html = $(embed_id).attr('before-text') + html;
        
        $(embed_id).prop('contenteditable', false).attr('data-original', original_data);
        $(embed_id).html(html);
        $(edit_btn_id).prop('disabled', false);
        $(preview_btn_id).prop('disabled', true);
        $(date_btn_id).invisible();
    });

    // Edit button click handler
    $(".dc-embed-edit-btn").click(function(e) {
        const edit_btn_id = "#" + this.id;
        const embed_id = "#" + this.id.replace(/-edit-btn$/, '');
        const preview_btn_id = embed_id + '-preview-btn';
        const date_btn_id = embed_id  + '-date-btn';

        let original_data = $(embed_id).attr('data-original');
        original_data = removeTags(original_data);
        const html = original_data.replaceAll(/\n/g, '<br>');

        $(embed_id).html(html).prop('contenteditable', true);
        $(preview_btn_id).prop('disabled', false);
        $(edit_btn_id).prop('disabled', true);
        $(date_btn_id).visible();
    });

    $(".dc-embed-save-btn").click(function(e) {
        const embed_id = "#" + this.id.replace(/-save-btn$/, '');
        const preview_btn_id = embed_id + '-preview-btn';
        if (!$(preview_btn_id).prop('disabled')) {
            $(preview_btn_id).click();
        }
        const message = $(embed_id).attr('data-original');
        const date = $(embed_id).attr('data-date') || new Date().toISOString();
        // Dirty hack to send the data to the server with a POST request and redirect
        // by creating a form and submitting it
        const form = $('<form action="/silksong" method="POST">' +
            '<input type="hidden" name="message" value="' + message + '" />' +
            '<input type="hidden" name="date" value="' + date  + '" />' +
            '</form>'
        );
        $('body').append(form);
        form.submit();
    });
    // Double click on message handler
    $("p[contenteditable]").doubleClick(function(e) {
        if (this.isContentEditable) return;
        
        $("#" + this.id + "-edit-btn").click();
    });

    // Attach date picker to date button
    $('.dc-embed-date-btn').tempusDominus({
        display: {
            icons: {
                type: 'icons',
                time: 'bi bi-clock',
                date: 'bi bi-calendar-week',
                up: 'bi bi-arrow-up-circle',
                down: 'bi bi-arrow-down-circle',
                previous: 'bi bi-arrow-left-circle',
                next: 'bi bi-arrow-right-circle',
                today: 'bi bi-calendar-check',
                clear: 'bi bi-trash',
                close: 'bi bi-x-circle'
            },
            components: {
                decades: false,
                clock: false,
                hours: false,
                minutes: false,
                seconds: false,
            },
            buttons: {
                today: true,
                close: true
            },
            theme: "dark"
        },
        restrictions: {
            maxDate: getLastMomentOfToday()
        }
    });

    // Date on date change handler
    $('.dc-embed-date-btn').on(tempusDominus.Namespace.events.change, function(e) {
        const embed_id = "#" + this.id.replace(/-date-btn$/, '');
        $(embed_id).attr('before-text', formatNewsDateMessage(e.date));
        $(embed_id).attr('data-date', e.date.toISOString());
    });
});