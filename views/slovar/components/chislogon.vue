<template>
    <div class="form-horizontal">
        <div class="form-group">
            <label class="control-label col-xs-2" for="value">Введите число</label>
            <div class="col-xs-3">
                <input type="text" class="form-control" id="value" v-model="value" class="form-control" placeholder="Введите число">
            </div>
            <label class="control-label col-xs-1" for="zhnumber">или пропись</label>
            <div class="col-xs-4">
                <input type="text" class="form-control" id="zhnumber" v-model="zhnumber" class="form-control" placeholder="Введите пропись">
            </div>
            <div class="col-xs-2">
                <select class="form-control" v-model="options.currency">
                    <optgroup label="Числа">
                        <option value="chislo">Десятичное</option>
                    </optgroup>
                    <optgroup label="Валюта">
                        <option v-for="(value, key) in valunits"
                                :value="key"
                                v-text="key">
                        </option>
                    </optgroup>
                </select>
            </div>
        </div>
        <div class="form-group">
            <label class="control-label col-xs-2">Пропись числа</label>
            <div class="col-xs-10">
                <textarea class="form-control"  :value="propis"></textarea>
            </div>
        </div>
        <!--div>
             <textarea class="form-control"  :value="words"></textarea>
            <input class="form-control" v-model="word" placeholder="слово">
        </div-->
        <div class="form-group">
            <fieldset>
                <legend>Опции</legend>
                <div class="col-xs-6">
                    <label>Отключить пропись</label>
                    <input type="checkbox" class="switcher__input" id="off_base" v-model="options.off_base">
                    <label class="switcher__label" for="off_base"> целой части</label>
                    <input type="checkbox" class="switcher__input" id="off_part" v-model="options.off_part">
                    <label class="switcher__label" for="off_part"> дробной части</label>
                </div>
                <div class="col-xs-6">
                    <label>Показывать нулевое значение</label>
                    <input type="checkbox" class="switcher__input" id="zero_base" v-model="options.zero_base">
                    <label class="switcher__label" for="zero_base"> целой части</label>
                    <input type="checkbox" class="switcher__input" id="zero_part" v-model="options.zero_part">
                    <label class="switcher__label" for="zero_part"> дробной части</label>
                </div>
            </fieldset>
        </div>
    </div>
</template>
<script>
module.exports = {
    name: 'chislogon',
    data(){
        return {
            zhnumber:'四亿一千四百二十九万四千一百八十二',
            options:{off_base: false,
                     off_part: false,
                     zero_base:false,
                     zero_part:false,
                     currency: "chislo",
                    },
            value: '0',
            mode:'simple',
            word:'',
            valunits: {
                RUB: {
                    base: ['m', 'рубль', 'рубля', 'рублей'],
                    part: ['f', 'копейка', 'копейки', 'копеек']
                },
                USD: {
                    base: ['m', 'доллар', 'доллара', 'долларов'],
                    part: ['m', 'цент', 'цента', 'центов']
                },
                EUR: {
                    base: ['m', 'евро', 'евро', 'евро'],
                    part: ['m', 'евроцент', 'евроцента', 'евроцентов']
                },
                CNY: {
                    base: ['m', 'юань', 'юаня', 'юаней'],
                    part: ['m', 'фэнь', 'фэня', 'фэней'],
                    part10: ['m', 'цзяо', 'цзяо', 'цзяо']
                },
                KZT: {
                    base: ['m', 'тенге', 'тенге', 'тенге'],
                    part: ['f', 'тиын', 'тиына', 'тиынов']
                },
                UAH: {
                    base: ['f', 'гривна', 'гривны', 'гривен'],
                    part: ['f', 'копейка', 'копейки', 'копеек']
                }
            }
        }
    },
    computed:{
        propis(){
            if (this.options.currency==='chislo'){
                return this.decimal(String(this.value), this.options)
            } else {
                return this.currency(String(this.value), this.options)
            }
        }
    },
    watch: {
        zhnumber(v){
            this.value = this.zhnum(v);
        }
    },
    methods:{
        split3 (x, a) {
            if (!a) a = [];
            if (x === "" || !/\d{1,3}$/g.test(x)) return a;
            return this.split3(
                x.replace(/\d{1,3}$/g, (m)=>{ a.push(m);return ""}), a)
        },
        format (num, options){
            var x=new Intl.NumberFormat("ru-ru",{style: "currency",
                                                 currency: "RUB"});
            console.log(x.resolvedOptions ());
            return x.format(num)
        },

        razryad (snum, unit, zero) {
            unit = unit || ["m", "", "", ""];
            snum = {
                0: "000",
                1: "00",
                2: "0",
                3: ""
            }[snum.length] + snum; /*Фиксация формата*/
            if (/^0{3}$/.test(snum)) {
                return zero ? (zero == true ? unit[3] : zero) : ""
            }; //Обработка zero
            var odin = {
                "m": "один",
                "f": "одна",
                "n": "одно"
            }[unit[0]] || "один";
            var dva = {
                "m": "два",
                "f": "две",
                "n": "два"
            }[unit[0]] || "два";
            var h100 = ["", "сто", "двести", "триста", "четыреста", "пятьсот",
                        "шестьсот", "семьсот", "восемьсот", "девятьсот"];
            var h010 = ["", "", "двадцать", "тридцать", "сорок", "пятьдесят",
                        "шестьдесят", "семьдесят", "восемьдесят", "девяносто"];
            var h011 = ["", odin, dva, "три", "четыре", "пять", "шесть", "семь",
                        "восемь", "девять", "десять", "одиннадцать", "двенадцать",
                        "тринадцать", "четырнадцать", "пятнадцать", "шестнадцать",
                        "семнадцать", "восемнадцать", "девятнадцать"];
            return snum.replace(
                /^([0-9])(?:(1[0-9])|(?:([02-9])([0-9])))$/g,
                function(m, s100, d011, d010, e011) {
                    var form = +e011;
                    var u = (form > 4 || !form) ? unit[3] : (form > 1 && form < 5) ? unit[2] : unit[1];
                    return [h100[s100], h011[d011], h010[d010], h011[e011], u].filter((x)=>x?true:false).join(' ')
                })
        },
        common (number, unit, zero, ondig) {
            unit = unit || ["m", "", "", ""];
            number = number || "";
            if (/^0+$/.test(number)) {
                return zero ? (zero == true ? (ondig?"0 ":"ноль ")+unit[3]: zero) : ""
            };
            var n = this.split3(number);
            var units = [unit,
                         ["f", "тысяча", "тысячи", "тысяч"],
                         ["m", "миллион", "миллиона", "миллионов"],
                         ["m", "миллиард", "миллиарда", "миллиардов"],
                         ["m", "триллион", "триллиона", "триллионов"],
                         ["m", "квадриллион", "квадриллиона", "квадриллионов"]
                        ];
            if (ondig||n.length > units.length) {
                var form=(number.slice(-2,-1))<2?+number.slice(-2):+number.slice(-1);
                var u = (form > 4 || !form) ? unit[3] : (form > 1 && form < 5) ? unit[2] : unit[1];
                number=number.replace(/^0+/g,"");
                return number?number+" "+u:""
            };
            for (var i = 0; i < units.length; i++) {
                units[i] = n[i] ? this.razryad(n[i], units[i], i == 0) : ""
            };
            return units.reverse().filter((x)=>x?true:false).join(' ').trim();
        },
        dolya (dotnum) {
            var wrd = ["десят", "сот", "тысячн", "десятитысячн", "стотысячн",
                       "миллионн", "десятимиллионн", "стомиллионн",
                       "миллиардн", "десятимиллиардн", "стомиллиардн",
                       "триллионн", "десятитриллионн", "стотриллионн",
                       "квадриллионн", "десятиквадриллионн", "стоквадриллионн"
                      ][dotnum.length - 1];
            return ["f", wrd + "ая", wrd + "ых", wrd + "ых"]
        },
        decimal (snum, options) {
            //console.log(snum);
            let dflt_opt={off_base:false, off_part:false, zero_base:false, zero_part:false};
            options=Object.assign(dflt_opt, options);
            var tnum = snum.split(",").join(".").split(".");
            tnum[0] = this.common(tnum[0], (tnum[1] ? ["f", "целая", "целых", "целых"] : false), options.zero_base, options.off_base);
            tnum[1] = tnum[1] ? this.common(tnum[1], this.dolya(tnum[1]), options.zero_part, options.off_part) : "";
            tnum = tnum.join(" ");
            return tnum.trim()
        },
        currency (summa, options) {
            var units = this.valunits;
            var dflt_opt= {currency: "RUB", off_base: false, off_part: false, zero_base:false, zero_part:false};
            options=Object.assign(dflt_opt, options);
            options.currency=options.currency.toUpperCase();
            options['unit']=options['unit']?options['unit']:(units[options.currency]||{base: "", part: ""});
            var tnum = parseFloat(summa.split(",").join(".")).toFixed(2).split(".");
            tnum[0] = /\d/.test(tnum[0]) ? this.common(tnum[0], options.unit.base, options.zero_base, options.off_base) : "";
            if ('part10' in options.unit){
                tnum[2] = tnum[1] ? this.common(tnum[1][1], options.unit.part, options.zero_part, options.off_part) : "";
                tnum[1] = tnum[1] ? this.common(tnum[1][0], options.unit.part10, options.zero_part, options.off_part) : "";
            } else {
                tnum[1] = tnum[1] ? this.common(tnum[1], options.unit.part, options.zero_part, options.off_part) : "";
            };
            tnum = tnum.filter((x)=>x?true:false).join(" ");
            return tnum.trim()
        },

        zhnum(txt){
            const numreplace={'零':'0','〇':'0','一':'1','二':'2','三':'3','四':'4','五':'5','六':'6','七':'7','八':'8','九':'9'};
            if (/^[零〇一二三四五六七八九]{2,}$/g.test(txt)) {
                txt=txt.replace(/[零〇一二三四五六七八九]/g, (m)=>numreplace[m]);
                return eval(txt)
            };
            const regcorr=/([百佰万亿])[一二两三四五六七八九零壹贰叁肆伍陆柒捌玖]$/g;
            const repcorr={"百":"十","佰":"十","万":"千","亿":"万"};
            const regroup1=/([〇一二两三四五六七八九零壹贰叁肆伍陆柒捌玖十百拾佰千仟万萬]+)([万萬亿億兆])/g;
            const wani={"万":"10000", "萬":"10000","亿":"100000000","億":"100000000", "兆":"1000000000000"};
            const regroup2=/([〇一二两三四五六七八九零壹贰叁肆伍陆柒捌玖十百拾佰]+)([千仟])/g;
            const regroup3=/([〇一二两三四五六七八九零壹贰叁肆伍陆柒捌玖]+)([十百拾佰])/g;
            const shibai={"十":"10", "百":"100", "拾":"10", "佰":"100"};
            const slogi={"〇":"+0","一":"+1","二":"+2","两":"+2","三":"+3","四":"+4","五":"+5",
                       "六":"+6","七":"+7","八":"+8","九":"+9","零":"+0","壹":"+1","贰":"+2",
                       "叁":"+3","肆":"+4","伍":"+5","陆":"+6","柒":"+7","捌":"+8","玖":"+9",
                       "十":"+10", "百":"+100", "拾":"+10", "佰":"+100", "千":"+1000",
                       "仟":"+1000", "万":"+10000","萬":"+10000","亿":"+100000000",
                       "億":"+100000000", "兆":"+1000000000000"};
            const reslogi=/[〇一二两三四五六七八九零壹贰叁肆伍陆柒捌玖十百拾佰千仟万萬亿億兆]/g;
            //console.log(txt);
            txt=txt.replace("万万","亿");
            txt=txt.replace(regcorr,function (m,a){
                return m+repcorr[a]
            });
            txt=txt.replace(regroup1, function (m, g, a){
                return "+("+g+")*"+wani[a];
            });
            //console.log(txt);
            txt=txt.replace(regroup2, function (m, g, a){
                return "+("+g+")*1000";
            });
            //console.log(txt);
            txt=txt.replace(regroup3, function (m, g, a){
                return g+"*"+shibai[a];
            });
            //console.log(txt);
            txt=txt.replace(reslogi, function (m){
                return slogi[m]
            });
            //console.log(txt);
            return eval(txt)
        }
    },
}
</script>
<style scoped>
        /*Флажек-переключатель*/
    .switcher__input {display: none;}
    .switcher__input:checked + .switcher__label {color: #000;}
    .switcher__input:checked + .switcher__label:before {background-color: #38cae5;}
    .switcher__input:checked + .switcher__label:after {transform: translateX(12px);}
    .switcher__input:checked + .switcher__label:active:after {transform: translateX(12px);}
    .switcher__input:checked + .switcher__label:active:before {background-color: #b4effa;}
    .switcher__label {display: inline-block;vertical-align: center;
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
