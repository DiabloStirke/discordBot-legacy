$.fn.doubleClick = function (onDoubleClick) {
    if (typeof onDoubleClick !== 'function') return this;
    this.click(function (e) {
        if (e.detail == 2) {
            onDoubleClick.call(this, e);
        }
    });
    return this;
}

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