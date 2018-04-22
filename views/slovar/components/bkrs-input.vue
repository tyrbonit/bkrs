<template>
    <div class="bkrs-input">
        <div v-if="!textarea" class="form-group">
            <input type="text"
                   class="form-control"
                   ref="input"
                   @input="updateText($event.target.value)"
                   :value="value"/>
        </div>
        <div :class="classObject">
            <div class="hlt-area"
                 :contenteditable="textarea"
                 @input="updateText($event.target.innerText)"
                 @paste="handlePaste"
                 v-html="marked"
                 v-text="value">
            </div>
        </div>
    </div>
</template>

<script>
module.exports = {
  name: 'bkrs-input',
  props: {textarea: {type:Boolean, default: false},
          delay:{type:Number, default: 1000},
          markpos:{type:Array, default: ()=>[0,0]},
          markclass:{type:String, default: "highlight"},
		  value:{type:String, default: ""},
          },
          computed: {
  classObject() {
    return {
      'hlt-textarea': this.textarea,
      'hlt-input': !this.textarea
    }
  },
  marked(){
        let markpos=this.markpos, s=+markpos[0], e=+markpos[1], value=this.value;
        return txt=this.escapeHTML(value.substring(0,s))
              + '<span class="'+this.markclass+'">'
              + this.escapeHTML(value.substring(s,e))
              + '</span>' +
              this.escapeHTML(value.substring(e));
  }
  },
  created(){
	this.updateText=_.debounce(this.updateText,this.delay)
      },
  methods: {
  	handlePaste (e) {
    var clipboardData;
    e.stopPropagation();
    e.preventDefault();
    clipboardData = e.clipboardData || window.clipboardData;
    let text=clipboardData.getData('Text')
    this.insertTextAtCursor(text);
    this.updateText(e.target.innerText)
},
insertTextAtCursor(text) {
    var sel, range, html;
    if (window.getSelection) {
        sel = window.getSelection();
        if (sel.getRangeAt && sel.rangeCount) {
        		var textNode = document.createTextNode(text)
            range = sel.getRangeAt(0);
            range.deleteContents();
            range.insertNode( textNode );
            range.setStartAfter(textNode);
            sel.removeAllRanges();
            sel.addRange(range);
        }
    } else if (document.selection && document.selection.createRange) {
        document.selection.createRange().text = text;
    }
},
    updateText(value){
    if (this.value===value) return
    this.$emit('input', value)
    },
    escapeHTML (s) {
      		return String(s)
          				.replace(/&/g, '&amp;')
                  .replace(/</g, '&lt;')
                  .replace(/>/g, '&gt;')
                  .replace(/"/g, '&quot;')
                  },
  }
}
</script>

<style>
.highlight {background-color: yellow}

.hlt-textarea {
  min-height:200px;
  height: 100%;
  border: 2px solid #74637f;
  border-radius: 0;
}

.hlt-area {
  white-space: pre-wrap;
  min-height:inherit;
  padding: 10px;
  font: 20px/28px arial, "Times New Roman", 'Open Sans', sans-serif;
  letter-spacing: 1px;
}
</style>
