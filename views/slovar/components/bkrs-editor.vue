<template>
    <div class="quill-editor" :class="{'ql-disabled':disabled}">
        <slot name="toolbar"></slot>
        <div ref="editor"></div>
        <!--textarea :value="bbcode" cols="50" rows="10"></textarea-->
    </div>
</template>
<script>
    let Inline = Quill.import('blots/inline');
    let Embed = Quill.import('blots/embed');
    let Block = Quill.import('blots/block');
    let BlockEmbed = Quill.import('blots/block/embed');
    let Text = Quill.import('blots/text');
    let Parchment = Quill.import('parchment');
    let ui_icons = Quill.import('ui/icons');
    Inline.order = ['tag', 'link', 'cursor', 'inline', 'underline', 'strike', 'italic', 'bold', 'script', 'code'];

    ui_icons.divider='<i class="glyphicon glyphicon-minus" aria-hidden="true"></i>';
    class DividerBlot extends Block { }
    DividerBlot.blotName = 'divider';
    DividerBlot.tagName = 'hr';
    DividerBlot.className = 'bkrs-divider';
    Quill.register(DividerBlot);

    ui_icons.m={1:'M1', 2:'M2', 3:'M3', 4:'M4'};
    class mAttributor extends Parchment.Attributor.Class {
      add(node, value) {
        if (value === '+1' || value === '-1') {
          let indent = this.value(node) || 1;
          value = (value === '+1' ? (indent + 1) : (indent - 1));
        }
        //return super.add(node, value);
        if (value === 0) {
          this.remove(node);
          return true;
        } else {
          return super.add(node, value);
        }
      }

      canAdd(node, value) {
        return super.canAdd(node, value) || super.canAdd(node, parseInt(value));
      }

      value(node) {
        return parseInt(super.value(node)) || 1;
      }
    }

    let mClass = new mAttributor('m', 'bkrs-m', {
      scope: Parchment.Scope.BLOCK,
      whitelist: [0, 1, 2, 3, 4]
    });
    Quill.register(mClass, true);


    class TagBlot extends Inline {
    static create(value) {
        let node = super.create();
        node.setAttribute('title', value)
        return node;
      }
      static formats(node) {
        return node.getAttribute('title') || true
      }
    }

    TagBlot.blotName = 'tag';
    TagBlot.className = 'bkrs-tag';
    TagBlot.tagName = 'span';
    ui_icons.tag="TAG";
    Quill.register(TagBlot);

    ui_icons.ex="EX";
    let Example = new Parchment.Attributor.Class('ex', 'bkrs-ex');
    Quill.register(Example);

    ui_icons.star="*";
    let Star = new Parchment.Attributor.Class('star', 'bkrs-star');
    Quill.register(Star);


    let LinkClass = Quill.import('formats/link');

    class Link extends LinkClass {

        static create(url) {
            let node = super.create();
            node.setAttribute('href', url);
            node.setAttribute('rel', 'alternate');
            return node;
        }

        static formats(domNode) {
            return domNode.getAttribute('href') || true;
        }

    }

    Quill.register(Link, true);

    module.exports = {
        name: 'bkrs-editor',

        data: function() {
            return {
                delta: [],
                defaultModules: {
                    toolbar: [
                        [{color:['green', 'violet', 'red', 'crimson', 'black', 'grey']}, 'italic', 'bold', 'link'],
                        ['tag'],
                        [{m:1},{m:2}, {m:3}, {m:4}],
                        ['ex', 'star', 'divider'],
                        ['clean']
                    ],
                    keyboard: {
                        bindings: {
                            tab: {
                                key: 9,
                                format:{m:true},
                                handler: function(range, context) {
                                    this.quill.format('m', '+1')
                                }
                            },
                            untab:{
                                key: 9,
                                format:{m:true},
                                shiftKey: true,
                                handler:function(range, context) {
                                    this.quill.format('m', '-1')
                                }
                            },
                            firstspace:{
                                key: 32,
                                format:{m:true},
                                prefix: /^$/,
                                handler:function(range, context) {
                                    this.quill.format('m', '+1')
                                }
                            },
                            backspace:{
                                key: 8,
                                format:{m:true},
                                prefix: /^$/,
                                handler:function(range, context) {
                                    this.quill.format('m', '-1')
                                }
                            }
                        }
                    }
                }
            }
        },

        props: {
            value: String(),
            disabled: Boolean(true),
            placeholder: {type: String, default: 'Insert text here ...'},
            options: {
                type: Object,
                required: false,
                default: ()=>{return {}}
            }
        },

        mounted: function() {
            this.initialize()
        },

        beforeDestroy: function() {
            this.quill = null
        },

        computed:{
            bbcode(){return this.delta2bb(this.delta)}
        },

        watch: {
            value(v){
                this.quill.setContents(this.bb2delta(v))
            },

            delta(newVal, oldVal){
                this.$emit('input', this.bbcode);
            },

            disabled(newVal, oldVal) {
                if (this.quill) {
                    this.quill.enable(!newVal)
                }
            }
        },

        methods: {

            initialize: function() {
                if (this.$el) {
                    // options and instance
                    var self = this;
                    self.options.theme = self.options.theme || 'snow';
                    self.options.boundary = self.options.boundary || document.body;
                    self.options.modules = self.options.modules || self.defaultModules;
                    self.options.modules.toolbar = self.options.modules.toolbar !== undefined? self.options.modules.toolbar: self.defaultModules.toolbar;
                    self.options.placeholder = self.options.placeholder || self.placeholder;
                    self.options.readOnly = self.options.readOnly !== undefined ? self.options.readOnly: false;
                    self.options.formats = self.options.formats !== undefined ? self.options.formats: ['color', 'italic', 'bold', 'link', 'tag', 'm', 'ex', 'star', 'divider'];
                    self.quill = new Quill(self.$refs.editor, self.options);

                    self.quill.getModule('toolbar').addHandler('divider', function (){
                        let range = this.quill.getSelection(true);
                        this.quill.insertText(range.index, '\n', Quill.sources.USER);
                        this.quill.insertEmbed(range.index + 1, 'divider', true, Quill.sources.USER);
                        this.quill.setSelection(range.index + 2, Quill.sources.SILENT);
                    });

                    self.quill.getModule('toolbar').addHandler('link', function (value) {
                        let range=this.quill.getSelection();
                        /*console.log(range, this.quill.getLine(range.index))*/
                        if (value && range.length){
                            var href =this.quill.getText(range);
                            /*console.log(range)*/
                            if (href) {
                                /*this.quill.removeFormat(range.index, range.length)*/
                                this.quill.format('link', href, Quill.sources.USER)
                            };
                        } else {
                            this.quill.format('link', false, Quill.sources.USER);
                        }
                    });

                    self.quill.getModule('toolbar').addHandler('ex', function (value) {
                        this.quill.format('ex', value, Quill.sources.USER);
                        if (value) {
                            let m = this.quill.getFormat()['m'];
                            this.quill.format('m', m>1?m:2, Quill.sources.USER);
                        }
                    });

                        // mark model as touched if editor lost focus
                    self.quill.on('selection-change', (range) => {
                        if (!range) {
                            self.$emit('blur', self.quill)
                        } else {
                            self.$emit('focus', self.quill)
                        }
                    });
                    // update model if text changes
                    self.quill.on('text-change', (delta, oldDelta, source) => {
                        if (source == 'api') {
                        } else if (source == 'user') {
                            self.delta = self.quill.getContents().ops;
                        }
                    });
                    // disabled
                    if (this.disabled) {
                        this.quill.enable(false)
                    };
                    // emit ready
                    self.$emit('ready', self.quill);
                    if (self.value){
                        self.quill.setContents(self.bb2delta(self.value))
                    };
                }
            },

            bb2delta: function (txt){
                /*Функция преобразования текста в Дельта формат*/
                /*Массив из строк вида (BB тэг)+(BB тэг)+..+(текст) или просто (текст)*/
                if (!txt) return [];
                const TRANSFORM={m:'m', '*':'star', i:'italic', b:'bold', ex:'ex', e:'ex', c:'color', ref:'link', p:'tag', apndx:'m', hr:'divider'};
                const bl_tags = ['m', 'hr'].map((key)=>TRANSFORM[key]);
                const bl_class = ['*', 'ex'].map((key)=>TRANSFORM[key]);
                txt = txt.replace("[m1]-----[/m]", "[hr][/hr]");

                var blocks = txt.match(/(?:(?:\[[-*\/\s\w]+\])+.*?|(?:.+?))(?=\[[-*\/\s\w]+\]|$)/gm).reduce(
                    function (blocks, match){
                        let RE_BB_TXT_GROUPS = /(^(?:\[[-*\/\s\w]+\])*)(.*)/g; //Делит строку на группу с тэгами и группу с текстом
                        let RE_BB_TAG = /\[(\/?)([a-z*]+)\s?([\w\s]*?)\]/g;  // Определяет параметры тэга - тип(закр./откр.), имя, атрибут
                        var [, tag_group, text] = RE_BB_TXT_GROUPS.exec(match);

                        text = text.replace(/\\([\[\]])/g, "$1");
                        var block = blocks[blocks.length - 1];
                        var iattrs = block.childs.length?Object.assign({}, block.childs[block.childs.length-1].attributes):{};

                        while ((t = RE_BB_TAG.exec(tag_group)) != null) {
                            var [, open, tag, value] = t;
                            open=open?false:true;
                            value=value?value:true;
                            if (open && tag ==='c' && value===true) {value ='green'};
                            /*Трансформация имени тэга*/
                            tag = (tag in TRANSFORM)?TRANSFORM[tag]:tag;
                            if (~bl_tags.indexOf(tag)) {
                                iattrs = {};
                                if (open) {
                                    if (block.childs.length) {
                                        block = blocks[blocks.push({childs:[], attributes:{}})-1];
                                    }
                                    block.attributes[tag]=value;
                                } else {
                                    block = blocks[blocks.push({childs:[], attributes:{}})-1];
                                };

                            } else if (~bl_class.indexOf(tag)) {

                                if (open) {
                                    block.attributes[tag] = value
                                }

                            } else {
                                if (open) {
                                    iattrs[tag] = value
                                    } else {
                                    delete iattrs[tag]
                                }
                            };
                        };

                        if (text) {
                            if ('link' in iattrs) {iattrs.link = text};
                            block.childs.push({insert: text, attributes: iattrs})
                        }
                        return blocks

                    }, [{childs:[], attributes:{}}]);

                var ops=[];
                blocks.forEach(function(bl){
                	ops=ops.concat(bl.childs, {insert: "\n", attributes: bl.attributes});
                });
                return ops
            },

            group_by_blocks: function (delta) {
            /* Группирует список в дельта формате на список блоков */
                const TRANSFORM={m:'m', '*':'star', i:'italic', b:'bold', ex:'ex', e:'ex', c:'color', ref:'link', p:'tag', apndx:'m', hr:'divider'};
                const BLOCKTAGS = ['m', 'hr', '*', 'ex'].map((key)=>TRANSFORM[key]);
                return delta.reduce(
                    function (blocks, x){
                        let bl_atts = {}, inl_attrs = {};

                        for (k in x.attributes) {
                            if (~BLOCKTAGS.indexOf(k)){
                               bl_atts[k] = x.attributes[k];
                            } else if (inl_attrs) {
                               inl_attrs[k] = x.attributes[k];
                            }
                        };

                        blocks = x.insert.split(/(\n)/g).reduce(
                            function (blks, txt){
                                if (txt === "\n") {
                                    blks[blks.length-1].attributes=bl_atts;
                                    blks.push({childs:[], attributes:{}});
                                } else if (txt){
                                    blks[blks.length-1].childs.push({insert: txt, attributes: inl_attrs})
                                };
                                return blks
                            }, blocks);
                        return blocks
                    }, [{childs:[], attributes:{}}])
            },

            delta2bb: function (delta){
                const maptable={m:'m', divider: 'hr', color:'c', star:'*', italic:'i', bold:'b', ex:'ex', link:'ref', tag:'p'};
                const blocktags=['ex', 'star', 'divider', 'm'];
                const defvalues={color:'green'};
                return this.group_by_blocks(delta).reduce(
                    function (text, block){
                        /*if (!Object.keys(block.attributes).lenght) {block.attributes = {m: 1}};*/
                        var chunks = block.childs.reduce(
                            function (chunk, child){
                                let txt = child.insert.replace(/([\[\]])/g, "\\$1");
                                for (ikey in child.attributes){
                                    let tag=maptable[ikey], val=child.attributes[ikey];
                                    val=(val === 'true' || tag === 'ref')?true:val;
                                    val = (val === true ||defvalues[ikey]===val)?"":(isFinite(val)?val:(" "+val));
                                    txt = "["+tag+val+"]" + txt + "[/"+tag+"]"
                                };
                                return chunk+=txt
                            }, "");

                        chunks = blocktags.reduce(
                            function (chunks, bkey) {
                                if (bkey in block.attributes) {
                                    let tag=maptable[bkey], val=block.attributes[bkey];
                                    val=(val === 'true' || val === true)?"":(isFinite(val)?val:(" "+val));
                                    return "["+tag+val+"]" + chunks + "[/"+tag+"]"
                                } else {
                                    return chunks
                                };
                            }, chunks);
                        return text+=chunks
                    }, '')
            },
        },
    }
</script>
<style scoped>
    .ql-disabled .ql-toolbar {display: none;}
    .ql-toolbar button{margin:0;}
    .ql-active, .ql-active .ql-stroke {background-color: #9760ca!important;color: white!important;stroke: white!important;}
    .ql-editor{font-family:arial;font-size:12pt;}
    .ql-editor .bkrs-m-2{margin-left: 3em!important;}
    .ql-editor .bkrs-m-3{margin-left: 6em!important;}
    .ql-editor .bkrs-m-4{margin-left: 9em!important;}
    .ql-editor .bkrs-tag{
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
        border-radius: 10px;}
    .ql-editor .bkrs-divider{margin: 5px;border: 2px dotted;text-align: center;}
    /*.ql-editor .bkrs-divider:after{content:"Имена собственные";}*/
    .ql-editor .bkrs-ex-true{border: 1px dotted; font-size: 90%;}
    .ql-editor .bkrs-star-true{display: list-item;}
    .ql-container {max-height: 500px;min-height: 300px; overflow-y: auto;}
    .ql-container.ql-disabled {max-height: inherit;}
    .ql-container::-webkit-scrollbar {width: 5px;height: 5px;}
    .ql-container::-webkit-scrollbar-track {-webkit-box-shadow: inset 0 0 2px rgba(0,0,0,0.3);-webkit-border-radius: 4px;border-radius: 4px;}
    .ql-container::-webkit-scrollbar-thumb {-webkit-border-radius: 4px;border-radius: 4px;background: rgba(255,0,0,0.8);-webkit-box-shadow: inset 0 0 2px rgba(0,0,0,0.5);}
    
</style>
