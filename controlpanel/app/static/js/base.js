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