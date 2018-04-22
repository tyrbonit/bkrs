<template>
    <span v-html="slovo"></span>
</template>
<script>
module.exports = {
    name: 'bkrs-chunk',
    props:{text: String,
           usespace:{type: Boolean, default: false},
           mark:{type: Boolean, default: false}
          },
    data: function(){
        return {
            punctuation: {
                '。':'.', '，':',', '、':',','“':'"',
                '”':'"','‘':"'",'’':"'",'：':":",
                '；':";",'《':"«",'》':"»",'（':"(",
                '）':")",'〈':"&lt;",'〉':"&gt;",'！':"!",'／':"/",
                '？':"?",'【':"[",'】':"]",'［':"[",'＜':"&lt;",'＞':"&gt;",
                '］':"]",'～':"~",'℃':"&#176;C"
            }
        }
    },
    computed: {

  		repl_exp(){
            let a = Object.keys(this.punctuation).join('');
            a = this.escapeRegExp(a);
            return new RegExp('['+a+']','g')
        },
        slovo(){
            return this.escapeHTML(this.text)
              .replace(this.repl_exp, a=>this.punctuation[a])
              +(this.usespace?"&#160;<wbr/>":"");
             }
    },
}
</script>

<style></style>
