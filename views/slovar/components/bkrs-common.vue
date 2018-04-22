<template>
    <div class="bkrs-common row">
        <div class="col-md-12">
            <a @click="modal=true;current={}" class="bkrs-btn" title="Добавить в словарь"><i class="glyphicon glyphicon-plus" aria-hidden="true"></i></a>
        </div>
        <bkrs-input :class="inputClass"
                    :textarea="textarea"
                    :markpos="markpos"
                    :value="slovar.text"
                    @input="translate">
        </bkrs-input>

        <div :class="inputClass">
            <div v-if="onchunks" :class="outputClass">
                <span v-for="(chunk, i) in chunks"
                            @mouseleave="markpos=[]"
                            @mouseenter="updatecurs(chunk)"
                            @click="setcurrent(chunk, $event)"
                            :key="chunk.id+'-'+i"
                            :class="chunk.class"
                            v-html="chunk.modi"
                           >
                </span>
            </div>

            <div v-else>
                <!--div v-if="slovar.record"
                    class="slovo-single">
                    <bkrs-slovo @mouseenter.native="updatecurs"
                              :data="slovar.data[slovar.record]">
                    </bkrs-slovo>
                </div-->

                <div :class="outputClass">
                    <div class="slovo-cell"
                         v-for="(chunk, i) in chunks"
                         :key="chunk.id+'-'+i"
                         @mouseleave="markpos=[]"
                         @mouseenter="updatecurs(chunk)"
                         @click.stop="setcurrent(chunk)"
                         >
                        <div v-if="!chunk.blocked" class="bkrs-toolbar">
                            <a @click="modal=true;popover=false" class="glyphicon glyphicon-book bkrs-btn" aria-hidden="true" title="Посмотреть статью из словаря"></a>
                            <a @click="runsplit" class="glyphicon glyphicon-transfer bkrs-btn" aria-hidden="true" title="Разделить на составляющие"></a>
                            <a @click="setbypass" class="glyphicon glyphicon-trash bkrs-btn" aria-hidden="true" title="Не использовать в переводе"></a>
                        </div>
                        <div class="slovo" :sid="chunk.data.id">
                            <span v-if="!chunk.blocked"
                                        @click.stop="setcurrent(chunk, $event)"
                                        class="chunk"
                                        v-html="chunk.modi"
                                        >
                            </span>
                            <div class="bkrs-ch">
                                <a  class="bkrs-c-black"
                                   :href="chunk.data.slovo"
                                   target="_blank"
                                   v-text="chunk.data.slovo">
                                </a>
                            </div>
                            <div class="bkrs-py" v-html="chunk.py"></div>
                            <div class="bkrs-ru" v-html="chunk.ru"></div>
                        </div>
                    </div>
                </div>
            </div>
            <v-spinner v-model="loading"></v-spinner>
        </div>
        <modal v-model="modal" :footer="false" title="Словарь">
            <div slot="title">
                <span>
                    <input type="checkbox" id="editmode" v-model="onedit" class="on-edit_input">
                    <label for="editmode" class="on-edit_label">
                        <i class="glyphicon glyphicon-pencil" aria-hidden="true"></i>
                    </label>
                </span>
                <i class="glyphicon glyphicon-book" aria-hidden="true"> Словарь</i>
            </div>
            <bkrs-viewer :data="current.data" @save="save_slovo($event)" :on-edit="onedit"></bkrs-viewer>
        </modal>
        <popover v-if="popover" :target="clicktarget" v-model="popover" placement="bottom">
            <div slot="popover" class="text-center">
                <div v-if="onchunks && Object.keys(current).length" class="bkrs-toolbar">
                    <a @click="modal=true;popover=false" class="glyphicon glyphicon-book bkrs-btn" aria-hidden="true" title="Посмотреть статью из словаря"></a>
                    <a @click="runsplit" class="glyphicon glyphicon-transfer bkrs-btn" aria-hidden="true" title="Разделить на составляющие"></a>
                    <a @click="setbypass" class="glyphicon glyphicon-trash bkrs-btn" aria-hidden="true" title="Не использовать в переводе"></a>
                </div>
                <div v-text="current.data.slovo" class="bkrs-ch"></div>
                <div v-html="current.py" class="bkrs-py"></div>
                <div class="text-left">
                    <input v-if="morechoises"
                           id="inp"
                           @keyup.enter="addnew"
                           v-model.trim="search"
                           class="form-control input-sm search-choise"
                           type="text"
                           placeholder="Найти/добавить"/>
                    <div v-for="(item, i) in list"
                           v-if="morechoises?item.show:(i<3)"
                           :key="item.key"
                           class="choise">
                        <a href="#" @click="popover=!popover">
                            <span v-text="item.text"
                                  @click="setfirst(i)">
                            </span>
                        </a>
                        <a class="bkrs-close" @click="remove(i)"></a>
                    </div>
                    <a @click="morechoises=!morechoises" v-text="morechoises?'Свернуть':(list.length>3)?'Еще варианты':'Добавить вариант'"></a>
                </div>
            </div>
        </popover>
      </div>
</template>

<script>
module.exports = {
    name: 'bkrs-common',
    data(){
      return {
          slovar: {},
          modal:false,
          popover: false,
          morechoises:false,
          current:{},
          markpos:[0,0],
          loading:false,
          onedit: false,
          clicktarget: {},
          search: ""
      }
    },
      props: {
          text: {type:String, default: ''},
          textarea: {type:Boolean, default: false},
          onchunks: {type:Boolean, default: false}
      },

      created(){
          if (this.text) {this.translate(this.text)}
      },

      watch: {
          loading(v){}
      },

      computed:{
          punctuation() {
              return {
                  '。':'.', '，':',', '、':',','“':'"',
                  '”':'"','‘':"'",'’':"'",'：':":",
                  '；':";",'《':"«",'》':"»",'（':"(",
                  '）':")",'〈':"&lt;",'〉':"&gt;",'！':"!",'／':"/",
                  '？':"?",'【':"[",'】':"]",'［':"[",'＜':"&lt;",'＞':"&gt;",
                  '］':"]",'～':"~",'℃':"&#176;C"
              }
          },

          repl_exp(){
                let a = Object.keys(this.punctuation).join('');
                a = this.escapeRegExp(a);
                return new RegExp('['+a+']','g')
            },

          chunks(){
              if (!Object.keys(this.slovar).length) return [];
            var chunks = this.slovar.chunks,
                n = chunks.length,
                data=this.slovar.data,
                space_start=/^[^\n\s,.:;'"，、。：；》’”)）\]/\\%］]/,
                space_end=/[^\s\n(«\[（【［《〈]$/;
            var mark=false;
            //var marker=/[的，。：；‘’“”《》［］（）【】]/;
            for (var i=0;i<n;i++) {
                var chunk = chunks[i];
                chunk.data = data[chunk.id];
                //mark=marker.test(chunk.data.slovo)?!mark:mark;
                chunk.py = this.byword_representer(chunk.data.pinyin);
                chunk.ru = this.byword_representer(chunk.data.use_short?chunk.data.bywords_short:chunk.data.perevod);
                chunk.index = i;
                chunk.blocked = !isFinite(chunk.id);
                chunk.text = chunk.data.choiselist.length?chunk.data.choiselist[0]:(chunk.blocked?chunk.data.perevod:chunk.data.slovo);
                chunk.usespace = (i<n-1)?(space_start.test(data[chunks[i+1].id].slovo) && space_end.test(chunk.data.slovo)):false;
                chunk.modi = this.escapeHTML(chunk.text).replace(this.repl_exp, a=>this.punctuation[a])+(chunk.usespace?"&#160;<wbr/>":"");
                chunk.class = {'chunk':true, 'none-translate':chunk.blocked, 'chunk-mark': mark, 'current-chunk': i === this.current.index};
            }
            /*console.log(chunks)*/
            return chunks
        },

        inputClass () {
          return {
            'col-md-6': this.textarea && this.onchunks,
            'col-md-12': (!this.onchunks && !this.textarea)
                        ||(this.textarea && !this.onchunks)
                        ||(this.onchunks && !this.textarea)}
        },

        outputClass () {
          return {
            'show-area': this.onchunks,
            'slov-list': !this.onchunks && this.slovar.chunks && this.slovar.chunks.length>1}
        },

          list(){
      		return this.current.data.choiselist.map(
                (v)=>{
                    return {text:v, show:this.ismatch(v), key:this.hashCode(v)}}, this
            )
          },
      },

      methods:{

          hashCode (txt) {
              var hash = 0;
              if (txt.length == 0) return hash;
              for (i = 0; i < txt.length; i++) {
                  char = txt.charCodeAt(i);
                  hash = ((hash << 5) - hash) + char;
                  hash = hash & hash;
              }
              return hash
          },


        ismatch(value){
        		return (value.search(this.escapeRegExp(this.search)) != -1)?true:false
        },

        updatecurs(chunk){
            this.markpos=chunk?[+chunk.start, +chunk.end]:[0,this.slovar.text.length]
        },

        translate (slovo) {
            this.loading=true;
            this.$bkrs.translate({text: slovo, args:['fullmatch', (this.onchunks?'':'cross')]})
            .then(response => {
                //console.log(response)
                this.slovar = response.body;
                this.loading = false;
            }, response => {
                this.loading=false;
            })
        },

        runsplit () {
            var indx=this.current.index,
                slovo=this.current.data.slovo;
            this.loading=true;
            if (slovo.length<2||!isFinite(this.current.data.id)){
                this.loading=false;return
            };

            this.$bkrs.translate({text:slovo})
                .then(response => {
                //console.log(response)
                var json = response.body;
                var arr=json.chunks,
                    chunks = this.slovar.chunks,
            		delta = chunks[indx].start;
                /*Коррект. поз.*/
                for (var i = 0; i < arr.length; i++) {arr[i].start+=delta;arr[i].end+=delta}
                /*Добав. данные в список кусков*/
                chunks.splice(indx, 1);
                chunks = chunks.concat(arr);
                /*Убираем дубляжи и пересечения*/
                chunks = _.uniqWith(chunks, (a, b)=>_.intersection(
                                      _.range(a.start,a.end),
                                      _.range(b.start,b.end)
                                  ).length)
                /*Сортируем по начальным позициям*/
                chunks = _.sortBy(chunks, 'start');
                /*Добав. данные в словарь*/
                for (var key in json.data){this.$set(this.slovar.data, key, json.data[key])};
                /*Обновляем последовательность*/
                this.$set(this.slovar, 'chunks', chunks);
                this.loading=false;
                }, response => {
                    this.loading=false;
                });
      },

      addnew(){
          if (!~this.current.data.choiselist.indexOf(this.search)){
              this.current.data.choiselist.splice(0, 0, this.search);
              this.$bkrs.choiselist({id:this.current.data.id}, {new: this.search})
                  .then(response=>{this.alertHandler(response.body)}, response=>{console.log(response)})
              this.search = "";
            }
      },

      setfirst(i){
          this.popover=!this.popover;
          var value = this.current.data.choiselist.splice(i, 1)[0];
          this.current.data.choiselist.splice(0, 0, value);
          this.$bkrs.choiselist({id:this.current.data.id}, {first: value})
              .then(response=>{this.alertHandler(response.body)}, response=>console.log(response))
      },

      remove(i){
          this.popover=true;
          var value = this.current.data.choiselist.splice(i, 1)[0];
          this.$bkrs.choiselist({id:this.current.data.id}, {remove: value})
                  .then(response=>{this.alertHandler(response.body)}, response=>console.log(response))
      },

       setbypass(){
           if (this.current.data.slovo.length<2){return };
           this.$bkrs.bypass({id:this.current.data.id}, {})
               .then(
               response=>{
                   this.translate(this.slovar.text);
                   this.alertHandler(response.body);
                   },
               response=>{
                   console.log(response)
               }
           );
       },

          save_slovo(data){
               this.$bkrs.save({}, data)
               .then(
                   response => {
                      this.alertHandler(response.body)
                  },
                  response => {
                      console.log(response)
                  }
               )
          },

          setcurrent(chunk, event){
              this.popover = false;
              if (event && !chunk.blocked) {
                  this.$nextTick(
                      function(){

                          this.current = chunk;
                          this.clicktarget = event.target;
                          this.popover = true;
                      })
              } else if (!chunk.blocked){
                  this.current = chunk;
              }
          },

          alertHandler(event){
              this.$root.alertHandler(event);
          }
        }
      }
</script>

<style>
    .on-edit_input {display: none;}
    .on-edit_input:checked + .on-edit_label {color: #000;}
    .on-edit_label {display: inline-block; color: #ccc; transition: color .1s linear;}
    .btn-dict, .btn-split, .btn-bypass{font-size:8px}
    .choise {
        position: relative;
        padding: 3px;
        margin-bottom: 5px;
        background-color: #f47c3c;
        border-color: transparent;
        color: #ffffff;
        border: 1px solid transparent;
        border-radius: 4px;}
    .choise a{color: #fff;}
    .show-area {
        min-height:204px;
        border: 2px solid #74637f;
        border-radius: 0;
        padding: 15px;
        font: 20px/28px 'Open Sans', sans-serif;
        letter-spacing: 1px;
        white-space: pre-wrap;
    }
    .chunk:hover {background-color: yellow;}
    .chunk-mark {border-radius: 3px;background-color: #e8eaf1;}
    /*for bbcodes*/
    .bkrs-p{
        display: inline-block;
        min-width: 10px;
        padding: 3px 7px;
        font-size: 12px;
        font-weight: normal;
        color: #ffffff;
        line-height: 1;
        vertical-align: middle;
        white-space: nowrap;
        text-align: center;
        background-color: #93c54b;
        border-radius: 10px;
    }
    .bkrs-c{
        color:blueviolet;
    }
    .bkrs-divider{
        margin: 10px 0;
        border: 0;
        border-top: 1px dashed #cccccc;
    }
    .bkrs-m-2{
        margin-left: 3em;
    }
    .bkrs-m-3{
        margin-left: 6em;
    }
    .bkrs-m-4{
        margin-left: 9em;
    }
    .bkrs-ex{
        border: 1px dotted;
        font-size: 90%;
    }
    .bkrs-star {
        display: list-item;
    }
    .bkrs-c-brown{
        color: brown;
    }
    .bkrs-c-black{
        color: black;
    }
    .bkrs-c-red{
        color: red;
    }
    .bkrs-c-crimson{
        color: crimson;
    }
    .bkrs-c-green{
        color: green;
    }
    .bkrs-c-violet{
        color: violet;
    }
    .bkrs-c-gray{
        color: gray;
    }
    .bkrs-ch{font-family: KaiTi,simsun,Nsimsun,STKaiti,STSong,arial unicode MS, sans-serif,arial;font-size:16pt;line-height: normal;text-align: center;}
    .bkrs-py{font-family:STSong, STKaiti, sans-serif, arial;font-size:12pt;line-height: normal;font-weight:bold;text-align: center;}
    .bkrs-py p{margin-bottom: 0; margin-top: 0; padding:1px;}
    .bkrs-ru{font-family:arial;font-size:12pt; line-height: normal; text-align: left; white-space: pre-wrap; word-wrap: break-word;}
    .bkrs-ru p{margin-bottom: 0; margin-top: 0; padding:1px;}
    /*.kitext{font-size: 20pt;font-family: KaiTi,simsun,Nsimsun,STKaiti,STSong,arial unicode MS, sans-serif,arial;}
    .kitext{max-height: 130px;overflow-y: auto;}*/
    .slov-list{background: #ffffff;}
    .slovo-cell{display:inline-block;/*max-height:150px;min-height:150px;height:150px;*/position:relative;line-height: 1.25;}
    /* one item */
    .slovo-cell:first-child:nth-last-child(1) {min-width:150px;max-width:100%;width: 100%;}
    /* two items */
    .slovo-cell:first-child:nth-last-child(2),
    .slovo-cell:first-child:nth-last-child(2)
    ~ .slovo-cell {min-width:150px;max-width:50%;width: 50%;vertical-align: top;}
    /* three items */
    .slovo-cell:first-child:nth-last-child(3),
    .slovo-cell:first-child:nth-last-child(3)
    ~ .slovo-cell {min-width:150px;max-width:33.3333%;width: 33.3333%;vertical-align: top;}
    /* four items */
    .slovo-cell:first-child:nth-last-child(4),
    .slovo-cell:first-child:nth-last-child(4)
    ~ .slovo-cell {min-width:150px;max-width:25%;width: 25%;vertical-align: top;}
    /* more four items */
    .slovo-cell:first-child:nth-last-child(n+4),
    .slovo-cell:first-child:nth-last-child(n+4)
    ~ .slovo-cell {min-width:150px;max-width:25%;width: 25%;max-height:155px;min-height:155px;height:155px;}
    .slovo {position: relative;overflow: hidden;background: #ffffff;
            border: 1px solid #ffffff;min-height: inherit;max-height: inherit;height: inherit;padding: 0;}
    .slovo:hover .bkrs-ru {max-height: inherit;overflow-y: auto;}
    /*Полосы прокрутки*/
    ::-webkit-scrollbar {width: 5px;height: 5px;}
    ::-webkit-scrollbar-track {-webkit-box-shadow: inset 0 0 2px rgba(0,0,0,0.3);-webkit-border-radius: 4px;border-radius: 4px;}
    ::-webkit-scrollbar-thumb {-webkit-border-radius: 4px;border-radius: 4px;background: rgba(255,0,0,0.8);-webkit-box-shadow: inset 0 0 2px rgba(0,0,0,0.5);}
    /*Полосы прокрутки*/
    .slov-list .slovo:hover {
        width:100%;
        background-color: #fafafa;
        border-bottom: 1px solid black;
        border-top: 1px solid black;
        position: absolute;
        z-index: 1;
        height: auto;
        max-height:800px;
        -webkit-transition: max-height 0.6s ease-out;
        -moz-transition: max-height 0.6s ease-out;
        -o-transition: max-height 0.6s ease-out;
        transition: max-height 0.6s, overflow, border-width;
        -webkit-transition-delay: 0.5s;
        -moz-transition-delay: 0.5s;
        -o-transition-delay: 0.5s;
        transition-delay: 0.5s;
        -webkit-box-shadow: 0 0 4px rgba(0, 0, 0, 0.2), inset 0 0 50px rgba(0, 0, 0, 0.1);
        -moz-box-shadow: 0 0 4px rgba(0, 0, 0, 0.2), inset 0 0 50px rgba(0, 0, 0, 0.1);
        box-shadow: 0 0 5px rgba(0, 0, 0, 0.2), inset 0 0 50px rgba(0, 0, 0, 0.1);
        }
    /*bbcode*/
    .current-chunk {border-bottom: blue dotted 1px;}

    .bkrs-toolbar {
        z-index: 1;
        display: block;
        font-size: xx-small;
        position: absolute;
        color: black;
        top: 0;
        left: 0;
        width: 15px;
        margin-top: 0;
        margin-left: -25px;
        padding-right: 25px;
    }
    .slovo-cell .bkrs-toolbar{
        display: none;
    }

    .slovo-cell:hover .bkrs-toolbar{
        display: block;
    }
    .bkrs-close {
        float: right;
        opacity: 0.4;
        height: 15px;
        width: 15px;
        cursor: pointer;
        background: transparent;
        border: 0;
        -webkit-appearance: none;
        margin-left: 5px;
    }
    .bkrs-close:after {
        content: "×";
        position: absolute;
        color: black;
        margin-left: 5px;
    }
    .bkrs-btn {
        border: 1px dotted;
        border-radius: 10px;
        border-color: black;
        min-width: 10px;
        min-height: 10px;
        padding: 1px;
        text-align: center;
        color: blueviolet;
        background-color: white;
        margin: 10px 0px;
    }

    .bkrs-close:hover, .bkrs-btn:hover {
        opacity: 1;
        animation: none;
        -webkit-animation: none;
        -webkit-transform: scale(2.0);
        transform: scale(2.0);
        color: #f1319a;
        text-decoration: none;
        border: none;
    }
</style>
