

function func(param){
    //"".replace(new RegExp("<br>$"), "").replaceAll("<br>", "\n");
    //let res = param.replaceAll(/\*\*\*((?:[^*\\]|\\\*)+)\*\*\*/g, "<b><i>$1</i></b>");
    let res = param.replaceAll(/\*\*((?:[^*\\]|\\\*)+)\*\*/g, "<b>$1</b>");
    res = res.replaceAll(/\*((?:[^*\\]|\\\*)+)\*/g, "<i>$1</i>");
    return res;
}

function compileMarkdown(){
    let html = $("#markdown").html();
    html = html.replaceAll("", "\n");
}