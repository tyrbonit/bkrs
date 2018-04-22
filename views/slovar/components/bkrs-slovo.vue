<template>
    <div class="slovo-cell">
        <slot name="toolbar"></slot>
        <div class="slovo" :sid="data.id">
            <slot></slot>
            <div v-if="ontitle" class="bkrs-ch">
                <a  class="bkrs-c-black"
                   :href="data.slovo"
                   target="_blank"
                   v-text="data.slovo">
                </a>
            </div>
            <div class="bkrs-py" v-html="py"></div>
            <div class="bkrs-ru" v-html="ru"></div>
        </div>
    </div>
</template>

<script>
module.exports = {
    name: 'bkrs-slovo',
      props: {
        data:{type: Object},
        ontitle:{type: Boolean,default:true}
        },
    computed: {
        ru () {return this.byword_representer(this.data.use_short?this.data.bywords_short:this.data.perevod)},
        py () {return this.byword_representer(this.data.pinyin)}
      },
    methods: {}
}
</script>

<style>
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
</style>
