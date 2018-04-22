<template>
    <div>
        <div class="check-styles row">
            <div class="col-xs-6">
                <label>Алфавит:</label>
                <input type="checkbox" class="switcher__input" id="latin" value="latin" v-model="alphabets">
                <label class="switcher__label" for="latin">Латиница</label>
                <input type="checkbox" class="switcher__input" id="cyrillic" value="cyrillic" v-model="alphabets">
                <label class="switcher__label" for="cyrillic">Кириллица</label>
                <input type="checkbox" class="switcher__input" id="bopomofo" value="bopomofo" v-model="alphabets">
                <label class="switcher__label" for="bopomofo">Чжуи́нь фуха́о</label>
            </div>
            <div class="col-xs-6">
                <label>Обозначение тона:</label>
                <input type="radio" id="none" value="none" v-model="toneStyle">
                <label for="none">Нет</label>
                <input type="radio" id="tone" value="tone" v-model="toneStyle">
                <label for="tone">Знак</label>
                <input type="radio" id="digit" value="digit" v-model="toneStyle">
                <label for="digit">Цифры</label>
                <input type="checkbox" class="switcher__input" id="color" v-model="color">
                <label for="color" class="switcher__label">Цвет</label>
            </div>
        </div>
        <bkrs-input textarea v-model="text" :markpos="markpos"></bkrs-input>
        <div class="show-area">
            <div class="alfa-style" v-for="alphabet in alphabets">
                <span v-for="(py, i) in styles[alphabet]"
                      v-html="py+' '"
                      @mouseleave="markpos=[]"
                      @mouseenter="updatepos(i)"
                      class="chunk">
                </span>
            </div>
        </div>
        <v-spinner v-model="loading"></v-spinner>
    </div>
</template>

<script>
module.exports = {
    name: 'bkrs-pinyin',
    data(){return {
        markpos:[],
        loading: false,
        alphabets:['latin'],
        toneStyle:'tone',
        color:true,
        text:"",
        pinyin:[],
        positions:[],
        TON_HTML:['', '\u0304', '\u0301','\u030c','\u0300']}
    },
    computed:{
        latin(){
            return this.pinyin.map(
                (word)=>{
                    return _.isArray(word)?word.reduce(
                        (acum, py)=>{
                            var tone=this.tonselect(py);
                            py=((this.toneStyle == 'tone')?py:(this.toneStyle=='digit')?this.tone2style(py, "tone3"):this.tone2style(py, "normal"))
                            if (!this.color) return acum + py;
                            return acum + '<span class="ton'+tone+'">'+py+'</span>'
                        }, ""
                    ):this.escapeHTML(word)}
            )
        },

        cyrillic(){
            return this.pinyin.map(
                (word)=>{
                    return _.isArray(word)?word.reduce(
                        (acum, py)=>{
                            var tone=this.tonselect(py);
                            py=this.tone2style(py, "cyrillic");
                            py=((this.toneStyle=='tone')?this.toner(py):(this.toneStyle=='digit')?py:py.replace(/\d/g,''))
                            if (!this.color) return acum + py;
                            return acum + '<span class="ton'+tone+'">'+py+'</span>'
                        }, ""
                    ):this.escapeHTML(word)}
            )
        },
        bopomofo(){
            return this.pinyin.map(
                (word)=>{
                    return _.isArray(word)?word.reduce(
                        (acum, py)=>{
                            var tone=this.tonselect(py);
                            py=this.tone2style(py, "bopomofo");
                            if (!this.color) return acum + py;
                            return acum + '<span class="ton'+tone+'">'+py+'</span>'
                        }, ""
                    ):this.escapeHTML(word)}
            )
        },
        styles(){
            return {latin:this.latin, cyrillic: this.cyrillic, bopomofo:this.bopomofo}
        },
    },
    watch: {
        text(){this.getpynyin()},
        alphabets(){},
    },
    methods: {

        toner(py){
            return py.replace(/([аеёиоуыэюя])(.*?)(\d?$)/, (m,a,b,c)=>{return a + this.TON_HTML[c||0]+b})
        },

        escapeHTML (s) {
            return String(s)
                .replace(/&/g, '&amp;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;')
                .replace(/"/g, '&quot;')
        },

        tonselect(pin){
            if (/[1āēōīū]/g.test(pin)) return 1;
            if (/[2áéóíúǘḿ]/g.test(pin)) return 2;
            if (/[3ǎěǒǐǔǚň]/g.test(pin)) return 3;
            if (/[4àèòìùǜǹ]/g.test(pin)) return 4;
            return 0
        },

        tone2style(py, style){
            if (!style) return py;

            var PHONETIC_SYMBOL = {
                "ā": "a1",    "á": "a2",    "ǎ": "a3",    "à": "a4",    "ē": "e1",
                "é": "e2",    "ě": "e3",    "è": "e4",    "ō": "o1",    "ó": "o2",
                "ǒ": "o3",    "ò": "o4",    "ī": "i1",    "í": "i2",    "ǐ": "i3",
                "ì": "i4",    "ū": "u1",    "ú": "u2",    "ǔ": "u3",    "ù": "u4",
                "ü": "v",    "ǘ": "v2",    "ǚ": "v3",    "ǜ": "v4",    "ń": "n2",
                "ň": "n3",    "ǹ": "n4",    "ḿ": "m2"};
            var RE_PHONETIC_SYMBOL = new RegExp('[' + _.keysIn(PHONETIC_SYMBOL).join("") + ']', 'g');
            py =py.replace(RE_PHONETIC_SYMBOL, function(m){
                if (style=='normal'){
                    if (_.indexOf(['ḿ', 'ń', 'ň', 'ǹ'], m)>-1){
                        return PHONETIC_SYMBOL[m].replace(/\d/g, '')
                    }
                    else {
                        return PHONETIC_SYMBOL[m].replace(/([aeoiuvnm])([1-4])$/g, '$1')
                    }
                }
                else if (_.indexOf(['tone2', 'tone3', 'cyrillic', 'bopomofo'], style)>-1){
                    return PHONETIC_SYMBOL[m]
                }
                else {
                    return m
                }
            });
            if (_.indexOf(['tone3', 'cyrillic', 'bopomofo'], style)>-1){
                py = py.replace(/^([a-z]+)([1-4])([a-z]*)$/g, '$1$3$2')
            };
            if (style=='cyrillic'){
                var CYRILLIC_REPLACE = [
                    [/ong/g, "ung"],[/([zcs])i/g, "$1U"],[/([xqj])u/g, "$1v"],
                    [/^wu(.?)$/g, "u$1"],[/(.+)r(.?)$/g, "$1R$2"],[/^zh/g, "Cr"],
                    [/^ch/g, "C"],[/^j/g, "qZ"],[/^z/g, "qZ"],[/^x/g, "s"],
                    [/^sh/g, "S"],[/([^CSdst])uo/g, "$1o"],[/^y(.*)$/g, "I$1"],
                    [/Iai/g, "AI"],[/Ia/g, "A"],[/Ie/g, "E"],[/Ii/g, "i"],
                    [/Iou/g, "V"],[/Iu/g, "v"],[/(.v)(\d?)$/g, "$1I$2"],[/Io/g, "O"],
                    /*[/iu/g, "v"],*/[/ie/g, "E"],[/hui/g, "huei"],[/ui/g, "uI"],
                    [/ai/g, "aI"],[/ei/g, "eI"],[/ia/g, "A"],[/(.*[^h])n([^g]?)$/g, "$1nM$2"],
                    [/(.*[^h])ng(.?)$/g, "$1n$2"],[/^v(\d?$)/g, "vI"]
                ];
                var CYRILLIC_TABLE =_.fromPairs(_.zip(
                    'abwgdEOrZiIklmnopRstufhqcCSHTMUevAV'.split(""),
                    'абвгдеёжзийклмнопрстуфхццчшщъьыэюяю'.split("")));
                _.forEach(CYRILLIC_REPLACE, function(value) {
                    py=py.replace(value[0], value[1])
                });
                py=py.split("").map(
                    (c)=>{
                        return _.get(CYRILLIC_TABLE, c, c)}).join("");
            } else if (style=='bopomofo') {
                var BOPOMOFO_REPLACE = [
                    [/^m(\d)$/g, "mu$1"],[/^n(\d)$/g, "N$1"],[/^r5$/g, "er5"],
                    [/iu/g, "iou"],[/ui/g, "uei"],[/ong/g, "ung"],[/^yi?/g, "i"],
                    [/^wu?/g, "u"],[/iu/g, "v"],[/^([jqx])u/g, "$1v"],[/([iuv])n/g, "$1en"],
                    [/^zhi?/g, "Z"],[/^chi?/g, "C"],[/^shi?/g, "S"],[/^([zcsr])i/g, "$1"],
                    [/ai/g, "A"],[/ei/g, "I"],[/ao/g, "O"],[/ou/g, "U"],[/ang/g, "K"],
                    [/eng/g, "G"],[/an/g, "M"],[/en/g, "N"],[/er/g, "R"],[/eh/g, "E"],
                    [/([iv])e/g, "$1E"],[/([^0-4])$/g, "$10"],[/1$/g, ""],
                ];
                var BOPOMOFO_TABLE =_.fromPairs(_.zip(
                    'bpmfdtnlgkhjqxZCSrzcsiuvaoeEAIOUMNKGR2340'.split(""),
                    'ㄅㄆㄇㄈㄉㄊㄋㄌㄍㄎㄏㄐㄑㄒㄓㄔㄕㄖㄗㄘㄙㄧㄨㄩㄚㄛㄜㄝㄞㄟㄠㄡㄢㄣㄤㄥㄦˊˇˋ˙'.split("")));
                _.forEach(BOPOMOFO_REPLACE, function(value) {
                    py=py.replace(value[0], value[1])
                });
                py=py.split("").map((c)=>{return _.get(BOPOMOFO_TABLE, c, c)}).join("");
            }; return py
        },

        tone2style1(py, style, alphabet){
            /*py - пиньин на английском с надстрочными знаками;
            style = ['tone2', 'tone3', 'normal'];
            alphabet = ['cyrillic', 'bopomofo']*/

            if (!style) return py;

            const PHONETIC_SYMBOL = {
                "ā": "a1",    "á": "a2",    "ǎ": "a3",    "à": "a4",    "ē": "e1",
                "é": "e2",    "ě": "e3",    "è": "e4",    "ō": "o1",    "ó": "o2",
                "ǒ": "o3",    "ò": "o4",    "ī": "i1",    "í": "i2",    "ǐ": "i3",
                "ì": "i4",    "ū": "u1",    "ú": "u2",    "ǔ": "u3",    "ù": "u4",
                "ü": "v",    "ǘ": "v2",    "ǚ": "v3",    "ǜ": "v4",    "ń": "n2",
                "ň": "n3",    "ǹ": "n4",    "ḿ": "m2"};

            const RE_PHONETIC_SYMBOL = new RegExp('[' + Object.keys(PHONETIC_SYMBOL).join("") + ']', 'g');

            py = py.replace(RE_PHONETIC_SYMBOL, function(m){
                if (style == 'normal'){
                    if (~['ḿ', 'ń', 'ň', 'ǹ'].indexOf(m)){
                        return PHONETIC_SYMBOL[m].replace(/\d/g, '')
                    } else {
                        return PHONETIC_SYMBOL[m].replace(/([aeoiuvnm])([1-4])$/g, '$1')
                    }
                } else if (~['tone2', 'tone3'].indexOf(style) || ~['cyrillic', 'bopomofo'].indexOf(alphabet)){
                    return PHONETIC_SYMBOL[m]
                } else {
                    return m
                }
            });

            if (~['tone2', 'tone3'].indexOf(style) || ~['cyrillic', 'bopomofo'].indexOf(alphabet)){
                py = py.replace(/^([a-z]+)([1-4])([a-z]*)$/g, '$1$3$2')
            };

            if (alphabet == 'cyrillic'){
                const CYRILLIC_REPLACE = [
                    [/ong/g, "ung"],[/([zcs])i/g, "$1U"],[/([xqj])u/g, "$1v"],
                    [/^wu(.?)$/g, "u$1"],[/(.+)r(.?)$/g, "$1R$2"],[/^zh/g, "Cr"],
                    [/^ch/g, "C"],[/^j/g, "qZ"],[/^z/g, "qZ"],[/^x/g, "s"],
                    [/^sh/g, "S"],[/([^CSdst])uo/g, "$1o"],[/^y(.*)$/g, "I$1"],
                    [/Iai/g, "AI"],[/Ia/g, "A"],[/Ie/g, "E"],[/Ii/g, "i"],
                    [/Iou/g, "V"],[/Iu/g, "v"],[/(.v)(\d?)$/g, "$1I$2"],[/Io/g, "O"],
                    /*[/iu/g, "v"],*/[/ie/g, "E"],[/hui/g, "huei"],[/ui/g, "uI"],
                    [/ai/g, "aI"],[/ei/g, "eI"],[/ia/g, "A"],[/(.*[^h])n([^g]?)$/g, "$1nM$2"],
                    [/(.*[^h])ng(.?)$/g, "$1n$2"],[/^v(\d?$)/g, "vI"]
                ];
                const CYRILLIC_TABLE =_.fromPairs(_.zip(
                    'abwgdEOrZiIklmnopRstufhqcCSHTMUevAV'.split(""),
                    'абвгдеёжзийклмнопрстуфхццчшщъьыэюяю'.split("")));

                py = CYRILLIC_REPLACE.reduce((acum, value)=>acum.replace(value[0], value[1]), py);

                py = py.split("").reduce((acum, c)=>{return acum + _.get(CYRILLIC_TABLE, c, c)}, "");

                /*Здесь пиньин уже будет кирилицей с указанием интонации цифрами (tone3), либо без тона (normal)*/

                if (style === 'tone2') {
                    py = py.replace(/([аеёиоуыэюя])(.*?)(\d?$)/, "$1$3$2")
                } else if (!~['normal', 'tone3'].indexOf(style)) {
                    const TON_HTML = ['', '\u0304', '\u0301','\u030c','\u0300'];
                    py = py.replace(/([аеёиоуыэюя])(.*?)(\d?$)/, (m, a, b, c)=>{return a + this.TON_HTML[c || 0]+b})
                }

            } else if (alphabet == 'bopomofo') {

                const BOPOMOFO_REPLACE = [
                    [/^m(\d)$/g, "mu$1"],[/^n(\d)$/g, "N$1"],[/^r5$/g, "er5"],
                    [/iu/g, "iou"],[/ui/g, "uei"],[/ong/g, "ung"],[/^yi?/g, "i"],
                    [/^wu?/g, "u"],[/iu/g, "v"],[/^([jqx])u/g, "$1v"],[/([iuv])n/g, "$1en"],
                    [/^zhi?/g, "Z"],[/^chi?/g, "C"],[/^shi?/g, "S"],[/^([zcsr])i/g, "$1"],
                    [/ai/g, "A"],[/ei/g, "I"],[/ao/g, "O"],[/ou/g, "U"],[/ang/g, "K"],
                    [/eng/g, "G"],[/an/g, "M"],[/en/g, "N"],[/er/g, "R"],[/eh/g, "E"],
                    [/([iv])e/g, "$1E"],[/([^0-4])$/g, "$10"],[/1$/g, ""],
                ];
                const BOPOMOFO_TABLE =_.fromPairs(_.zip(
                    'bpmfdtnlgkhjqxZCSrzcsiuvaoeEAIOUMNKGR2340'.split(""),
                    'ㄅㄆㄇㄈㄉㄊㄋㄌㄍㄎㄏㄐㄑㄒㄓㄔㄕㄖㄗㄘㄙㄧㄨㄩㄚㄛㄜㄝㄞㄟㄠㄡㄢㄣㄤㄥㄦˊˇˋ˙'.split("")));

                py = BOPOMOFO_REPLACE.reduce((acum, value)=>acum.replace(value[0], value[1]), py);

                py = py.split("").reduce((acum, c)=>{return acum + _.get(BOPOMOFO_TABLE, c, c)}, "");
            };
            return py
        },

		updatepos(i){
            this.markpos=this.positions[i]
        },

    getpynyin(){
        this.loading=true;
        this.$bkrs.pinyin({text: this.text})
              .then(
                  response => {
                      var json=response.body,
                          words=json.words,
                          tones=json.tone,
                          s=0, pos=[];
                      for (var i=0;i<words.length;i++){
                          var word=words[i];
                          pos.push([s, s+word.length]);
                          s+=word.length;
                      };
                    this.positions=pos;
                    this.pinyin=tones;
                    this.loading=false;
                  },
                  response => {
                      console.log('Ошибочка вышла... ', response)
                  }
              )
    },
  }
}
</script>

<style scoped>
    .show-area {
        min-height:200px;
        border: 2px solid #74637f;
        border-radius: 0;
        padding: 10px;
        font: 20px/28px 'Open Sans', sans-serif;
        letter-spacing: 1px;
    }
    .alfa-style{border-top: 1px dotted green;}
    .ton0{color: rgb(119,119,119);}
    .ton1{color: rgb(227,0,0);}
    .ton2{color: rgb(2,179,28);}
    .ton3{color: rgb(21,16,240);}
    .ton4{color: rgb(137,0,191);}
    /*Флажек-переключатель*/
    .switcher__input {display: none;}
    .switcher__input:checked + .switcher__label {color: #000;}
    .switcher__input:checked + .switcher__label:before {background-color: #38cae5;}
    .switcher__input:checked + .switcher__label:after {transform: translateX(12px);}
    .switcher__input:checked + .switcher__label:active:after {transform: translateX(12px);}
    .switcher__input:checked + .switcher__label:active:before {background-color: #b4effa;}
    .switcher__label {display: inline-block;vertical-align: center;
    padding-left: 25px!important;line-height: 1;font-size: 14px;
    color: #ccc;cursor: pointer;position: relative;transition: color .1s linear; margin:0; vertical-align: middle;}
    .switcher__label:before {content: "";display: block;width: 24px;height: 12px;
    background-color: #e5e5e5;border-radius: 6px;position: absolute;top: 0;
    left: 0;z-index: 1;transition: background-color .1s linear;}
    .switcher__label:after {
        content: "";
        display: block;
        width: 10px;
        height: 10px;
        background-color: #fff;
        border-radius: 50%;
        position: absolute;
        top: 1px;
        left: 1px;
        z-index: 2;
        transition: transform .1s linear;
    }
    .switcher__label:active:after {
        transform: translateX(12px);
    }
    .switcher__label:active:before {
        background-color: #b4effa;
    }
    /*/Флажек-переключатель*/
</style>
