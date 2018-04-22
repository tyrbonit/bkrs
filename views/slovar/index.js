var BkrsPlugin = {
    install: function (Vue, options) {
    Vue.http.options.root = '{{=URL("slovar", "api")}}';
    Vue.prototype.$bkrs = Vue.resource(
        'slovar{/id}',
        {},
        {
            translate: {method: 'GET', url: 'translate{/args*}'},
            choiselist: {method: 'POST', url: 'slovar{/id}/choiselist'},
            bypass: {method: 'POST', url: 'slovar/onbypass{/id}'},
            pinyin: {method: 'GET', url: 'pinyin{/args*}'}
        },
        {
            responseType: 'json',
            before(request) {
                // abort previous request, if exists
                if (this.previousRequest) {
                    this.previousRequest.abort();
                }
                // set previous request on Vue instance
                this.previousRequest = request;
            }
        }
    );
    Vue.mixin({
        methods: {

            escapeHTML (s) {
                return String(s).replace(/&(?!\w+;)/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;')
            },

            escapeRegExp (text) {
                return text.replace(/[-[\]{}()*+?.,\\^$|#\s]/g, "\\$&")
            },

            byword_representer(perevod) {
                if (!perevod) return "";
                if (!/(?:(?:\[[-*\/\s\w]+\])+.*?|(?:.+?))(?=\[[-*\/\s\w]+\]|$)/gm.test(perevod)) return perevod;
                const bl_tags = ['m', 'hr'];
                const bl_class = ['*', 'ex'];
                var self=this;
                perevod = perevod
                    .replace(/\[m1\]-----\[\/m\]/g, "[hr][/hr]")
                    .replace(/\[(\/?)e\]/g, "[$1ex]")
                    .replace(/\[apndx\]/g, "[m1]")
                    .replace(/\[\/apndx\]/g, "[/m]");

                var blocks = perevod.match(/(?:(?:\[[-*\/\s\w]+\])+.*?|(?:.+?))(?=\[[-*\/\s\w]+\]|$)/gm).reduce(
                    function (blocks, match){
                        let RE_BB_TXT_GROUPS = /(^(?:\[[-*\/\s\w]+\])*)(.*)/g;
                        let RE_BB_TAG = /\[(\/?)([a-z*]+)\s?([\w\s]*?)\]/g;
                        var [, tag_group, text] = RE_BB_TXT_GROUPS.exec(match);
                        text = text.replace(/\\([\[\]])/g, "$1");
                        var block = blocks[blocks.length - 1];
                        var iattrs = block.childs.length?Object.assign({}, block.childs[block.childs.length-1].attributes):{};
                        while ((t = RE_BB_TAG.exec(tag_group)) != null) {
                            var [, open, tag, value] = t;
                            open=open?false:true;
                            value=value?value:true;
                            if (open && tag ==='c' && value===true) {value ='green'};
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
                        if (text) {block.childs.push({insert: text, attributes: iattrs})}
                        return blocks
                    }, [{childs:[], attributes:{}}]);

                var trans_table = {i:'i', b:'b', ref:'a'};
                var container = document.createElement('div');
                blocks.forEach(function (block) {
                    if (block.attributes.hr){
                        let hr=document.createElement('hr');
                        hr.className="bkrs-divider"
                        container.appendChild(hr)

                    } else if (!block.attributes.ex){
                        let p=document.createElement('p');
                        for (k in block.attributes){
                            let v = block.attributes[k];
                            v = (typeof v === 'boolean')? "":("-"+v);
                            if (k === "*") {
                                p.classList.add("bkrs-star")
                            } else {
                                p.classList.add("bkrs-" + k + v)
                            };
                        };

                        block.childs.forEach(
                            function (inline){
                                let node = document.createTextNode(inline.insert);
                                for (k in inline.attributes) {
                                    let v = inline.attributes[k];
                                    v = (typeof v === 'boolean')? "":("-"+v);
                                    let child = document.createElement(trans_table[k] || 'span');
                                    child.appendChild(node);
                                    child.classList.add("bkrs-" + k + v);
                                    if (k==="ref") {
                                        child.setAttribute('href', '?text='+inline.insert);
                                        child.setAttribute('target', '_blank');
                                    };
                                    node = child;
                                };
                                p.appendChild(node);
                            });
                        container.appendChild(p);
                    }
                });
                return container.innerHTML
            },
        },
         components: {{=XML(Vue.share())}},
    })
}};
Vue.use(BkrsPlugin);
