function parseAsterisks(text){
    //"".replace(new RegExp("<br>$"), "").replaceAll("<br>", "\n");
    //let res = text.replaceAll(/\*\*\*((?:[^*\\]|\\\*)+)\*\*\*/g, "<b><i>$1</i></b>");
    const asterisk_code = '!::0x2A';
    let encoded = text.replaceAll(/\\\*/g, asterisk_code);
    let res = encoded.replaceAll(/\*\*\*((?:(?!\*\*\*).)+)\*\*\*/g, "<b><i>$1</i></b>");
    res = res.replaceAll(/\*\*((?:(?!\*\*).)+)\*\*/g, "<b>$1</b>");
    res = res.replaceAll(/\*([^*]+)\*/g, "<i>$1</i>");
    res = res.replaceAll(asterisk_code, "*");
    return res;
}

function parseTildes(text){
    const tilde_code = '!::0x7E';
    let encoded = text.replaceAll(/\\~/g, tilde_code);
    let res = encoded.replaceAll(/~~((?:(?!~~).)+)~~/g, "<del>$1</del>");
    res = res.replaceAll(tilde_code, "~");
    return res;
}

function extractAndEncodeUrls(text){
    const url_code = '!::0xURL';
    let url_regex = /https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&\/\/=]*)/g
    let url_arr = text.match(url_regex);
    url_arr = (url_arr === undefined || url_arr === null) ? [] : url_arr;
    let encoded = text.replaceAll(url_regex, url_code);
    return {url_array: url_arr, url_encoded: encoded};

}

function decodeUrls(url_arr, text){
    const url_code = '!::0xURL';
    let res = text;
    for (let i = 0; i < url_arr.length; i++){
        let anchor = '<a href="' + url_arr[i] + '">' + url_arr[i] + '</a>';
        res = res.replace(url_code, anchor);
    }
    return res;
}

function compileMarkdown(text){
    let {url_array, url_encoded} = extractAndEncodeUrls(text); 
    let res = parseAsterisks(url_encoded);
    res = parseTildes(res);
    res = decodeUrls(url_array, res);
    return res;
}

function removeTags(text){
    return text.replaceAll(/<\/?[^<>\/\\]+\/?>/g, '');

}

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

    $(".dc-embed-preview-btn").click(function(e) {
        const preview_btn_id = "#" + this.id;
        const embed_id = "#" + this.id.replace(/-preview-btn$/, '');
        const edit_btn_id = embed_id + '-edit-btn';
        const date_btn_id = embed_id + '-date-btn';

        let html = $(embed_id).html()
        let original_data = html.replace(/<br>^/, '').replaceAll(/<br>/g, '\n');
        original_data = removeTags(original_data);
        $(embed_id).prop('contenteditable', false).attr('data-original', original_data);

        html = compileMarkdown(html);
        html = $(embed_id).attr('before-text') + html;
        
        $(embed_id).html(html);
        $(edit_btn_id).prop('disabled', false);
        $(preview_btn_id).prop('disabled', true);
        $(date_btn_id).invisible();
    });
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

    $("p[contenteditable]").doubleClick(function(e) {
        if (this.isContentEditable) return;
        
        $("#" + this.id + "-edit-btn").click();
    });

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
                clock: false
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

    $('.dc-embed-date-btn').on(tempusDominus.Namespace.events.change, function(e) {
        const embed_id = "#" + this.id.replace(/-date-btn$/, '');
        $(embed_id).attr('before-text', formatNewsDateMessage(e.date));
    });
});