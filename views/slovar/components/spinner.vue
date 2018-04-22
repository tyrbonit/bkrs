<template>
    <div style="position:relative;">
        <div :class="spinnerClass" v-show="status" :style="spinnerStyle" v-html="htmlhelper"></div>
        <slot></slot>
    </div>
</template>

<script>
    module.exports = {
        props: {
            status: {
                type: Boolean,
                default: true
            },
            clockwise: {
                type: Boolean,
                default: true
            },
            size: {
                type: Number,
                default: 30
            },
            depth: {
                type: Number,
                default: 3
            },
            period: {
                type: Number,
                default: 1.0
            },
            color: {
                type: String,
                default: '#6589b6'
            },
            top: {
                type: Number,
                default: 50
            },
            left: {
                type: Number,
                default: 50
            },
			
            type: {
                type: String,
                default: 'circle'
            },
        },
        data() {
            return {
                clockwiseAnimations: ['rotateСlockwise', 'rotateCounterСlockwise'],
                sizeUnits: 'px',
                timeUnits: 's'
            }
        },
        computed: {
            htmlhelper(){return this.type==='frames'?'<span></span><span></span><span></span><span></span>':''},
            spinnerClockwise() {
                return this.clockwise ? this.clockwiseAnimations[0] : this.clockwiseAnimations[1];
            },

            spinnerDepth() {
                return this.depth + this.sizeUnits;
            },
            spinnerPeriod() {
                return this.period + this.timeUnits;
            },
			spinnerSize() {
                return this.size + this.sizeUnits;
            },
            spinnerTop() {
				let k={matrix:5/8,
				circle:1/2, frames:1/2
				}[this.type];
                return 'calc(' + this.top + '% - '+ k +'*' + this.spinnerSize + ')';
            },
            spinnerLeft() {
                let k={matrix:1/8,
				circle:1/2, frames:1/2
				}[this.type];
                return 'calc(' + this.left + '% - '+ k +'*' + this.spinnerSize + ')';
            },
            spinnerStyle() {
               return {frames: {
                    top: this.spinnerTop,
                    left: this.spinnerLeft,
                    width: this.spinnerSize,
                    height: this.spinnerSize,
					borderWidth: this.spinnerDepth,
                    position: 'absolute',
                    animationDuration: this.spinnerPeriod
                },
                 matrix: {
                    top: this.spinnerTop,
                    left: this.spinnerLeft,
                    fontSize: "calc("+this.spinnerSize+'/4)',
                    position: 'absolute',
                    animationDuration: this.spinnerPeriod
                },
                circle: {
                    top: this.spinnerTop,
                    left: this.spinnerLeft,
                    position: 'absolute',
                    borderTopColor: this.hexToRGB(this.color, 0.15),
                    borderRightColor: this.hexToRGB(this.color, 0.15),
                    borderBottomColor: this.hexToRGB(this.color, 0.15),
                    borderLeftColor: this.color,
                    width: this.spinnerSize,
                    height: this.spinnerSize,
                    borderWidth: this.spinnerDepth,
                    animationName: this.spinnerClockwise,
                    animationDuration: this.spinnerPeriod
                }
				}[this.type]
            },
            spinnerClass(){
                return {
                    circle:'sl-spinner',
                    matrix:'sl-matrix',
                    frames:'sl-frames'
                }[this.type]
            },
        },
        methods: {
            hexToRGB(hex, alpha) {
                var r = parseInt(hex.slice(1, 3), 16),
                    g = parseInt(hex.slice(3, 5), 16),
                    b = parseInt(hex.slice(5, 7), 16);
                if (alpha) {
                    return 'rgba(' + r + ', ' + g + ', ' + b + ', ' + alpha + ')';
                } else {
                    return 'rgb(' + r + ', ' + g + ', ' + b + ')';
                }
            }
        }
    }
</script>

<style>
    .sl-spinner {
        z-index:1000;
        border-style: solid;
        -webkit-transform: translateZ(0);
        -ms-transform: translateZ(0);
        transform: translateZ(0);
        animation-iteration-count: infinite;
        animation-timing-function: linear;
        border-radius: 50%;
        width: 30px;
        height: 30px;
    }
    @keyframes rotateСlockwise {
        0% {
            -webkit-transform: rotate(0deg);
            transform: rotate(0deg);
        }
        100% {
            -webkit-transform: rotate(360deg);
            transform: rotate(360deg);
        }
    }
    @keyframes rotateCounterСlockwise {
        0% {
            -webkit-transform: rotate(0deg);
            transform: rotate(0deg);
        }
        100% {
            -webkit-transform: rotate(360deg);
            transform: rotate(-360deg);
        }
    }
    /*sl-matrix*/
.sl-matrix {
    z-index:1000;
    /* position */
    width: 1em;
    height: 1em;

    /* Styles */
    border-radius: 50%;
    background: #123456;
    transform-origin: 50% 250%;
    animation:
        blink 1s steps(1, start) infinite, /* Blink */
        counter-clock 8s linear infinite;  /* Rotation */

    /* Dots, clockwise */
    box-shadow:
       1em 1em #123456,
       2em 2em #123456,
       1em 3em #123456,
       0em 4em #123456,
      -1em 3em #123456,
      -2em 2em #123456,
      -1em 1em #123456;
}
.sl-matrix:after {
    /* Size and position */
    content: "";
    width: 3em;
    height: 3em;
    position: absolute;
    left: -1em;
    top: 1em;
 
    /* Styles */
    transform: rotate(45deg);
    background: rgba(255,255,255,0.6);
 
}
    
@keyframes counter-clock {
    to { transform: rotate(-360deg); }
}
 
@keyframes blink {
    12.5% {
    background: rgba(18,52,86,0.6);
    box-shadow:
       1em 1em #123456,
       2em 2em #123456,
       1em 3em #123456,
       0em 4em #123456,
      -1em 3em #123456,
      -2em 2em #123456,
      -1em 1em #123456;
    }
 
    25% {
    background: #123456;
    box-shadow:
       1em 1em rgba(18,52,86,0.6),
       2em 2em #123456,
       1em 3em #123456,
       0em 4em #123456,
      -1em 3em #123456,
      -2em 2em #123456,
      -1em 1em #123456;
    }
 
    37.5% {
    background: #123456;
    box-shadow:
       1em 1em #123456,
       2em 2em rgba(18,52,86,0.6),
       1em 3em #123456,
       0em 4em #123456,
      -1em 3em #123456,
      -2em 2em #123456,
      -1em 1em #123456;
    }
 
    50% {
    background: #123456;
    box-shadow:
      1em 1em #123456,
      2em 2em #123456,
      1em 3em rgba(18,52,86,0.6),
      0em 4em #123456,
      -1em 3em #123456,
      -2em 2em #123456,
      -1em 1em #123456;
    }
 
    62.5% {
    background: #123456;
    box-shadow:
       1em 1em #123456,
       2em 2em #123456,
       1em 3em #123456,
       0em 4em rgba(18,52,86,0.6),
      -1em 3em #123456,
      -2em 2em #123456,
      -1em 1em #123456;
    }
 
    75% {
    background: #123456;
      box-shadow:
       1em 1em #123456,
       2em 2em #123456,
       1em 3em #123456,
       0em 4em #123456,
      -1em 3em rgba(18,52,86,0.6),
      -2em 2em #123456,
      -1em 1em #123456;
    }
 
    87.5% {
    background: #123456;
    box-shadow:
       1em 1em #123456,
       2em 2em #123456,
       1em 3em #123456,
       0em 4em #123456,
      -1em 3em #123456,
      -2em 2em rgba(18,52,86,0.6),
      -1em 1em #123456;
    }
 
    100% {
    background: #123456;
    box-shadow:
       1em 1em #123456,
       2em 2em #123456,
       1em 3em #123456,
       0em 4em #123456,
      -1em 3em #123456,
      -2em 2em #123456,
      -1em 1em rgba(18,52,86,0.6);
    }
}
/*sl-matrix*/
    /*sl-frames <span></span><span></span><span></span><span></span>*/
@keyframes frames {
  0% {transform:rotate(-45deg)}
  25%{transform:rotate(-90deg)}
  50%{transform:rotate(-135deg)}
  75%{transform:rotate(-180deg)}
  100%{transform:rotate(-225deg)}}
@keyframes span-1 {
  0% {transform:translate(0);}
  50%{transform:translate(-50px, 0);border-color:#EE4D68}
  100%{transform:translate(0);}}
@keyframes span-2 {
  0%{transform:translate(0);}
  50%{transform:translate(50px, 0);border-color:#875678}
  100%{transform:translate(0);}}
@keyframes span-3 {
  0%{transform:translate(0);}
  50%{transform:translate(0, -50px);border-color:#FF9900}
  100%{transform:translate(0);}}
@keyframes span-4 {
  0%{transform:translate(0);}
  50%{transform:translate(0, 50px);border-color:#00E4F6}
  100%{transform:translate(0);}}
.sl-frames {
    z-index:1000;
  animation: frames 2s infinite ease-in-out;
}
.sl-frames span {
  width: inherit;
  height: inherit;
  position: absolute;
  left: 0;
  top: 0;
  border-style: solid;
  border-color:#0B1B48;
}
.sl-frames span:nth-child(1) {
  animation: span-1 2s ease-in-out infinite;
}
.sl-frames span:nth-child(2) {
  animation: span-2 2s ease-in-out infinite;
}
.sl-frames span:nth-child(3) {
  animation: span-3 2s ease-in-out infinite;
}
.sl-frames span:nth-child(4) {
  animation: span-4 2s ease-in-out infinite;
}
</style>
