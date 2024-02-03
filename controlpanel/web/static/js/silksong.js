
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
        msg = `There were silksong news on ${formatted_date}! `;
    }
    return msg;
}

$(function() {


   { // Scope for variables. 
        let char_limit = 1750;
        
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

            if ($(this).text().length >= char_limit) {
                $(this).addClass('content-editable-error');
                $(this).siblings('.content-editable-error-label').show();
                const trimmed_text = $(this).text().substring(0, char_limit);
                $(this).text(trimmed_text);
            }

        });
        
        // Prevent typing more than "char_limit" characters
        $(document).on('keydown', 'p[contenteditable]', function(e) {
            allowed_keys = [8, 16, 17, 37, 38, 39, 40, 46];
            if ($(this).text().length >= char_limit && !allowed_keys.includes(e.keyCode)) {
                e.preventDefault();
                $(this).addClass('content-editable-error');
                $(this).siblings('.content-editable-error-label').show();
            }
            else if (e.keyCode === 8 || e.keyCode === 46) {
                $(this).removeClass('content-editable-error');
                $(this).siblings('.content-editable-error-label').hide();

            }
        });

        $(document).on('input', 'p[contenteditable]', function(e) {
            if ($(this).text().length > char_limit) {
                $(this).addClass('content-editable-error');
                $(this).siblings('.content-editable-error-label').show();
                const trimmed_text = $(this).text().substring(0, char_limit);
                $(this).text(trimmed_text);
            } else {
                $(this).removeClass('content-editable-error');
                $(this).siblings('.content-editable-error-label').hide();
            }
        });

    }
    // Preview button click handler
    $(".dc-embed-preview-btn").on('click', function(e) {
        const preview_btn_id = "#" + this.id;
        const embed_id = "#" + this.id.replace(/-preview-btn$/, '');
        const edit_btn_id = embed_id + '-edit-btn';
        const date_btn_id = embed_id + '-date-btn';

        if ($(embed_id).prop('contenteditable') === "false") {
            return;
        }

        let html = $(embed_id).html()
        // html holds, well, the html. The first time it's called, it holds the text stored in the database.
        // database stores the text with \n as line breaks, but html uses <br> as line breaks.
        // So, we need to replace \n with <br> to display the text correctly.
        html = html.replaceAll('\r\n', '\n').replaceAll('\r', '\n').replaceAll('\n', '<br>');
        // However, original_data holds the text as it is stored in the database, so we need to replace <br> with \n
        // Seems kinda redundant, but it's necessary. Although there might be a better way to do this.
        let original_data = html.replace(/<br>$/, '').replaceAll(/<br>/g, '\n');
        original_data = removeTags(original_data);
        
        html = compileMarkdown(html);
        html = $(embed_id).attr('before-text') + html;
        
        $(embed_id).prop('contenteditable', false).attr('data-original', original_data);
        $(embed_id).html(html);
        $(edit_btn_id).show()
        $(preview_btn_id).hide();
        $(date_btn_id).invisible();
    });

    // Edit button click handler
    $(".dc-embed-edit-btn").on('click', function(e) {
        const edit_btn_id = "#" + this.id;
        const embed_id = "#" + this.id.replace(/-edit-btn$/, '');
        const preview_btn_id = embed_id + '-preview-btn';
        const date_btn_id = embed_id  + '-date-btn';

        let original_data = $(embed_id).attr('data-original');
        original_data = removeTags(original_data);
        const html = original_data.replaceAll(/\n/g, '<br>');

        $(embed_id).html(html).prop('contenteditable', true);
        $(preview_btn_id).show();
        $(edit_btn_id).hide();
        $(date_btn_id).visible();
    });

    $(".dc-embed-edit-mode-btn").on('click', function(e) {
        const embed_id = "#" + this.id.replace(/-edit-mode-btn$/, '');
        const edit_btn_id = embed_id + '-edit-btn';
        $(edit_btn_id).parents('.dc-btn-container').show();
        $(this).parents('.dc-embed-drawer').remove(); // yup, one-way edit mode (you can't go back to preview mode)
        $(edit_btn_id).trigger('click');
        $(embed_id).trigger('focus');
        // A lot of things going on just to set the cursor at the end of the text
        const range = document.createRange();
        const sel = window.getSelection();
        const embed = $(embed_id)[0];
        range.setStart(embed, embed.childNodes.length);
        range.collapse(true);
        sel.removeAllRanges();
        sel.addRange(range);
    });

    // Save button click handler
    $(".dc-embed-save-btn").on('click', function(e) {
        const embed_id = "#" + this.id.replace(/-save-btn$/, '');
        const preview_btn_id = embed_id + '-preview-btn';
        if ($(preview_btn_id).is(':visible')) {
            $(preview_btn_id).trigger('click');
        }
        let message = $(embed_id).attr('data-original');
        const date = $(embed_id).attr('data-date') || new Date().toISOString();
        const id = $(this).attr('data-news-id');
        message = message.replaceAll('"', "'");

        let action = "/silksong"
        if (id != 'new') {
            action += "/" + id + "/edit";
        }
        // Dirty hack to send the data to the server with a POST request and redirect
        // by creating a form and submitting it
        const form = $('<form action="'+ action +'" method="POST">' +
            '<input type="hidden" name="message" value="' + message + '" />' +
            '<input type="hidden" name="date" value="' + date  + '" />' +
            '</form>'
        );
        $('body').append(form);
        form.trigger('submit');
    });

    // Attach date picker to date button
    $('.dc-embed-date-btn').each( function(){
        const picker = new tempusDominus.TempusDominus(this, {
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
        })

        const embed_id = "#" + this.id.replace(/-date-btn$/, '');

        this.addEventListener(tempusDominus.Namespace.events.change, function(e) {
            $(embed_id).attr('before-text', formatNewsDateMessage(e.detail.date));
            $(embed_id).attr('data-date', e.detail.date.toISOString());
        });

        let date = $(embed_id).attr('data-date');
        if (date) {
           // date = new Date(date);
            //$(embed_id).attr('before-text', formatNewsDateMessage(date));
            picker.dates.setValue(new tempusDominus.DateTime(date));
        }
    });

    $('p.dc-news-body').not('#dc-embed-new').each(function(){
        $('#'+this.id+'-preview-btn').trigger('click');
        $('#'+this.id+'-preview-btn').hide();
        $('#'+this.id).parents('.news-item').show();
    });

    $('.dc-avatar').one('error', function(){
        $(this).attr('src', '/rick-astley.png')
    });
});