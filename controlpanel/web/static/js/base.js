$.fn.doubleClick = function (onDoubleClick) {
    if (typeof onDoubleClick !== 'function') return this;
    this.click(function (e) {
        if (e.detail == 2) {
            onDoubleClick.call(this, e);
        }
    });
    return this;
}

$.fn.visible = function() {
    return this.css('visibility', 'visible');
};

$.fn.invisible = function() {
    return this.css('visibility', 'hidden');
};

function ordinal(n){
    let s=["th","st","nd","rd"],
    v=n%100;
    return n+(s[(v-20)%10]||s[v]||s[0]);
}

function getLastMomentOfToday(){
    let date = new Date();
    date.setHours(23, 59, 59, 999);
    return date;
}

function daysBetween(date1, date2) {

    const ONE_DAY = 1000 * 60 * 60 * 24;

    date1_clone = new Date(date1);
    date1_clone.setHours(0,0,0,0);

    date2_clone = new Date(date2);
    date2_clone.setHours(0,0,0,0);

    const differenceMs = Math.abs(date1_clone - date2_clone);

    // Convert back to days and return
    return Math.round(differenceMs / ONE_DAY);
}


function removeTags(text){
    return text.replaceAll(/<\/?[^<>\/\\]+\/?>/g, '');
}


/* Markdown parsing functions */

function parseAsterisks(text){
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