<template>
    <div class="bkrs-viewer">
        <div class="row">
            <div class="col-md-6 col-md-offset-3">
                <input v-if="blank" v-model="slovo" class="form-control input-sm bkrs-c-black bkrs-ch" type="text"/>
                <span v-else v-text="slovo" class="form-control input-sm bkrs-c-black bkrs-ch"></span>
            </div>
            <div class="col-md-6 col-md-offset-3">
                <input v-if="editable" v-model="pinyin" class="form-control input-sm bkrs-py" type="text"/>
                <span v-else v-text="pinyin" class="form-control input-sm bkrs-py"></span>
                <a v-if="editable" href="#" @click="getpinyin" class="auto-pinyin">Авто</a>
            </div>
        </div>
        <tabs>
            <tab title="Полный перевод" group="Перевод">
                <bkrs-editor :value="data.perevod" @input="perevod = $event" :disabled="!editable" placeholder="Введите текст полного перевода"></bkrs-editor>
            </tab>
            <tab title="Сокращенный перевод" group="Перевод">
                <div v-if="use_short">
                    <bkrs-editor :value="data.bywords_short" @input="bywords_short = $event" :disabled="!editable" placeholder="Введите текст сокращенного перевода"></bkrs-editor>
                </div>
                <div v-else class="bkrs-ru">
                    <p>Сокращенный перевод не используется</p>
                </div>
            </tab>
            <tab title="Список вариантов">
                <a v-if="editable && choiselist.length === 0" @click="choise_new()" href="#">Добавить</a>
                <transition-group name="list-complete" tag="div" class="choise-container bkrs-ru row">
                    <div class="choise-box list-complete-item" v-for="(item, i) in choiselist" :key="item.key">
                        <div v-if="editable" class="box-toolbar">
                            <a @click="choise_up(i)" class="glyphicon glyphicon-chevron-up box-btn" aria-hidden="true" title="Поднять"></a>
                            <a @click="choise_down(i)" class="glyphicon glyphicon-chevron-down box-btn" aria-hidden="true" title="Опустить"></a>
                            <a @click="choise_first(i)" class="glyphicon glyphicon-flag choise-check box-btn" aria-hidden="true" title="Сделать первым"></a>
                            <a @click="choise_delete(i)" class="glyphicon glyphicon-remove pull-right box-btn" aria-hidden="true" title="Удалить"></a>
                        </div>
                        <input v-if="editable" @keyup.enter="choise_new(i)" v-model.lazy.trim="item.text" v-focus="!item.text" class="choise-box-input">
                        <span v-else v-text="item.text" class="choise-box-input"></span>
                    </div>
                </transition-group>
            </tab>
            <form slot="nav-right">
                <label for="onshort">Cокр.
                    <input type="checkbox" id="onshort" v-model="use_short" class="switcher__input" :disabled="!editable">
                    <label for="onshort" class="switcher__label"></label>
                </label>
                <label for="onshort">Пропуск
                    <input type="checkbox" id="onbypass" v-model="bywords_out" class="switcher__input" :disabled="!editable">
                    <label for="onbypass" class="switcher__label"></label>
                </label>
                <button v-if="editable" type="success" @click.prevent="save" class="btn btn-xs">Сохранить</button>
            </form>
        </tabs>
    </div>
</template>
<script>
module.exports = {
    name: 'bkrs-viewer',

    props: {
        data: {
            type: Object,
            default: function () {
                return {}
            }
        },
        'on-edit': {type: Boolean, default:false},
           },

    data () {
        return {
            slovo: String(),
            pinyin: String(),
            perevod: String(),
            bywords_short: String(),
            choiselist: Array(),
            use_short: {type: Boolean, default:false},
            bywords_out: {type: Boolean, default:false},
            nextkey: 0
        }
    },

    directives: {
        focus: {
            inserted: function (el, binding) {
                if (binding.value) el.focus();
            }
        }
    },

    watch:{

        data:{
            handler:function (value){
                this.slovo = this.blank?"":value.slovo;
                this.pinyin = this.blank?"":value.pinyin;
                this.perevod = this.blank?"":value.perevod;
                this.bywords_short = this.blank?"":value.bywords_short;
                this.choiselist = this.blank?[]:value.choiselist.map(function (item, i){return {text:item, key:i}});
                this.use_short = this.blank?false:Boolean(value.use_short);
                this.bywords_out = this.blank?false:Boolean(value.bywords_out);
                this.nextkey = this.choiselist.length;
            },
            immediate: true
        },
    },

    computed: {
        blank(){return Object.keys(this.data).length < 1},
        editable(){return this.onEdit || this.blank}
    },

    methods: {

        getpinyin(){
        this.$bkrs.pinyin({text: this.slovo})
              .then(
                  response => {
                      this.pinyin = response.body.tone.reduce(
                          function (a, b){
                              a.push((typeof b === 'string')?b:b.join(''))
                              return a;
                          }, new Array).join(" ");
                  },
                  response => {
                      console.log('Ошибочка вышла... ', response)
                  }
              )
        },

        choise_up(i){
            if (i>0){
                this.choiselist.splice(i-1, 0, this.choiselist.splice(i, 1)[0])
            }
        },

        choise_down(i){
            if (i+1<this.choiselist.length){
                this.choiselist.splice(i+1, 0, this.choiselist.splice(i, 1)[0])
            }
        },

        choise_first(i){
            if (i){
                this.choiselist.unshift(this.choiselist.splice(i, 1)[0])
            }
        },

        choise_delete(i){
            this.choiselist.splice(i, 1)
        },

        choise_new(i){
            i = (typeof i==="undefined")?0:i+1;
            this.choiselist.splice(i, 0, {text:"", key: this.nextkey})
            this.nextkey++;
        },

        save(){
            this.data.slovo = this.slovo;
            this.data.pinyin = this.pinyin;
            this.data.perevod = this.perevod;
            this.data.bywords_short = this.bywords_short;
            this.data.choiselist = this.choiselist.map(item => item.text);
            this.data.use_short = this.use_short;
            this.data.bywords_out = this.bywords_out;
            this.$emit('save', this.data)
        }
    }
}
</script>
<style>
.list-complete-item {
  transition: all 1s;
  display: inline-block;
}
.list-complete-enter, .list-complete-leave-to {
  opacity: 0;
  transform: translateY(30px);
}
.list-complete-leave-active {
  position: absolute;
}
    .choise-box {
        padding: 1px;
        margin: 5px 3px;
        border: 1px solid transparent;
        border-radius: 4px;
        background-color: #93c54b;
        border-color: transparent;
        color: #ffffff;
        white-space: normal;
        display:inline-block;
        position:relative;
        line-height: 1.25;
    }
    /* one item */
    .choise-box:first-child:nth-last-child(1) {max-width:100%; width:100%;}
    /* two items */
    .choise-box:first-child:nth-last-child(2),
    .choise-box:first-child:nth-last-child(2)
    ~ .choise-box {max-width:48%;width: 48%;vertical-align: top;}
    /* three items */
    .choise-box:first-child:nth-last-child(3),
    .choise-box:first-child:nth-last-child(3)
    ~ .choise-box {max-width:32%;width: 32%;vertical-align: top;}
    /* more three items */
    .choise-box:first-child:nth-last-child(n+3),
    .choise-box:first-child:nth-last-child(n+3)
    ~ .choise-box {max-width:32%;width: 32%;}

    .choise-box-input {
        display: block;
        width: 100%;
        color: #3e3f3a;
        background-color: #ffffff;
        background-image: none;
        border: 1px solid #dfd7ca;
            height: 30px;
        padding: 5px 10px;
        font-size: 12px;
        line-height: 1.5;
        border-radius: 3px;
        -webkit-box-shadow: inset 0 1px 1px rgba(0,0,0,0.075);
        box-shadow: inset 0 1px 1px rgba(0,0,0,0.075);
        -webkit-transition: border-color ease-in-out .15s,-webkit-box-shadow ease-in-out .15s;
        -o-transition: border-color ease-in-out .15s,box-shadow ease-in-out .15s;
        transition: border-color ease-in-out .15s,box-shadow ease-in-out .15s;
    }
    .choise-container {counter-reset: choices;}
    .choise-box::before {
        counter-increment: choices;
        content: counter(choices);
        position: absolute;
        font-size: xx-small;
        font-weight: bold;
        border: black solid 1px;
        border-radius: 10px;
        min-width: 15px;
        text-align: center;
        background-color: whitesmoke;
        color: black;
        margin-left: -6px;
        margin-top: -10px;
    }
    .choise:first-child .box-btn.choise-check{color: red;}
    .box-toolbar {display: none;}
    .box-btn {
    border: 1px dotted;
    border-radius: 10px;
    border-color: black;
        margin: 0px 5px 0px 3px;
    min-width: 10px;
    min-height: 10px;
    padding: 1px;
    text-align: center;
    color: blueviolet;
    background-color: white;
}
    .choise-box:hover .box-toolbar {
    display: block;
    font-size: xx-small;
    width: 100%;
    position: absolute;
    color: black;
    margin-top: -10px;
    padding: 0px 7px 0px 14px;
}
    
    
    .auto-pinyin {
        position: absolute;
        display: block;
        font-size: x-small;
        margin: -12px 0px 0px 4px;
    }
    
    
    .bkrs-ch{font-family: KaiTi,simsun,Nsimsun,STKaiti,STSong,arial unicode MS, sans-serif,arial;font-size:16pt;text-align: center;}
    .bkrs-py{font-family:STSong, STKaiti, sans-serif, arial;font-size:12pt;font-weight:bold;text-align: center;}
    .bkrs-ru{font-family:arial;font-size:12pt; line-height: 1.42; text-align: left; white-space: pre-wrap; word-wrap: break-word; padding: 12px 15px;}
    .bkrs-ru p{margin-bottom: 0; margin-top: 0; padding:1px;}
    /*Флажек-переключатель*/
    .switcher__input {display: none;}
    .switcher__input:checked + .switcher__label {color: #000;}
    .switcher__input:checked + .switcher__label:before {background-color: #38cae5;}
    .switcher__input:checked + .switcher__label:after {transform: translateX(12px);}
    .switcher__input:checked + .switcher__label:active:after {transform: translateX(12px);}
    .switcher__input:checked + .switcher__label:active:before {background-color: #b4effa;}
    .switcher__label {display: inline-block;vertical-align: super;
    padding-left: 25px!important;line-height: 1;font-size: 14px;
    color: #ccc;cursor: pointer;position: relative;transition: color .1s linear;}
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
