<template>
    <div>
        <el-steps :active="stage" finish-status="success">
            <el-step title="Подготовка к запуску">
                <el-alert v-if="file_ready" type="success" title="" show-icon :closable="false" slot="description">
                    <span> Файл найден</span>
                </el-alert>
                <el-alert v-else type="warning" title="" show-icon :closable="false" slot="description">
                    <span> Файл не найден</span></p>
                    <ol>
                        <li>Скачайте 7z архив словаря <a href="https://bkrs.info/p47">с сайта БКРС</a>, в dsl формате одной частью</li>
                        <li>Распакуйте архив, пароль bkrs.info</li>
                        <li>Переименуйте файл 大БКРС_*.dsl в dabkrs.dsl</li>
                        <li>Переместите (скопируйте) файл dabkrs.dsl в папку "bkrs/static/dsl"</li>
                    </ol>
                </el-alert>
            </el-step>
            <el-step title="Подтверждение запуска">
                <el-steps :active="task_step" finish-status="success" slot="description" direction="vertical">
                    <el-step title="Постановка в очередь">
                        <el-alert v-if="stage==1" slot="description" type="info" title="" show-icon :closable="false">
                            <span>Запустить процесс заполнения базы? </span>
                            <button type="button"
                                    class="el-button el-button--default el-button--mini is-round"
                                    @click.once="run"
                                    >Запустить
                            </button>
                        </el-alert>
                    </el-step>
                    <el-step title="Принятие к выполнению"></el-step>
                    <el-step title="Выполнение начато"></el-step>
                </el-steps>
            </el-step>
            <el-step title="Заполнение базы">
                <el-steps :active="run_step" :finish-status="end_step==0?'error':'success'" slot="description" direction="vertical">
                    <el-step title="Выполнение задачи">
                        <el-card v-if="stage==2&&run_step==0" class="box-card" slot="description">
                            <p>Вставлено: <i v-text="inserted"></i></p>
                            <p>Обновлено: <i v-text="updated"></i></p>
                            <p>Время: <i v-text="time"></i> мин.</p>
                            <el-progress :percentage="progress"></el-progress>
                            <button type="button"
                                    class="el-button el-button--default el-button--mini is-round"
                                    @click.once="stop"
                                    >Остановить
                            </button>
                        </el-card>
                    </el-step>
                    <el-step title="Задача выполнена"></el-step>
                </el-steps>
            </el-step>
            <el-step title="Завершение">
                <el-card v-if="stage>2" class="box-card" slot="description">
                    <el-alert v-if="end_step==0" type="danger" title="" show-icon :closable="false">
                        <p><span> Ошибка выполнения</span></p>
                    </el-alert>
                    <el-alert v-else-if="end_step==1" type="warning" title="" show-icon :closable="false">
                        <p><span>Заполнение базы остановлено</span></p>
                    </el-alert>
                    <el-alert v-else type="success" title="" show-icon :closable="false">
                        <span> База успешно заполнена</span></p>
                    </el-alert>
                    <pre v-if="end_step==0" v-text="run_traceback"></pre>
                    <button type="button"
                            class="el-button el-button--default el-button--mini is-round"
                            @click.once="start"
                            >Повторить
                    </button>
                </el-card>
            </el-step>
        </el-steps>
    </div>
</template>
<script>
module.exports = {
    name: 'bkrs-wizard',
    data () {
        return {
            run_output:{},
            run_traceback: "",
            run_status: "",
            task_status: "",
            file_ready: false,
            run_send: false,
            stop_send: false,
            time: 0
            }
    },
     created(){
        this.update();
        this.update=_.debounce(this.update, 3000)
    },
    computed:{
        task_step(){return {"QUEUED":0,"ASSIGNED":1, "RUNNING": 3, "FAILED": 4, "COMPLETED":5}[this.task_status]},
        run_step(){return {"RUNNING":0,"COMPLETED":2, "STOPPED":3, "FAILED":3}[this.run_status || this.task_status]},
        end_step(){return {"FAILED":0, "STOPPED":1}[this.run_status]},
        stage(){
            return !this.file_ready?0:
            this.task_step<2?1:
            this.task_step>2&&this.run_step===0?2:
            this.run_step===1?3:4
        },

        progress(){
            this.time = this.start_time?Math.round((new Date() - Date.parse(this.start_time))/1000/60, 1):0;
            return this.run_output.progress || 0
        },
        inserted(){return this.run_output.inserted || 0},
        updated(){return this.run_output.updated || 0},
    },
    methods:{
        update(){
            fetch('{{=URL(args=["stepper"], extension="json")}}', {method: "GET", credentials: 'include'})
            .then((response) => {
                if(response.ok) {return response.json()}
                throw new Error('Error update');
            })
            .then((json) => {
                this.run_output=json.run_output?JSON.parse(json.run_output):{}
                this.run_traceback=json.run_traceback
                this.run_status=json.run_status
                this.task_status=json.task_status
                this.start_time=json.start_time
                this.file_ready=json.file_ready
                this.update()
            })
            .catch((error) => {
                console.log(error)
            });
        },
        run(){
            fetch('{{=URL(args=["run"], extension="json")}}', {method: "GET", credentials: 'include'})
            .then((response) => {
                if(response.ok) {return response.json()}
                throw new Error('Error run');
            })
            .then((json) => {
                this.run_send=json.status
            })
            .catch((error) => {
                console.log(error)
            });
        },
        stop(){
            fetch('{{=URL(args=["stop"], extension="json")}}', {method: "GET", credentials: 'include'})
            .then((response) => {
                if(response.ok) {return response.json()}
                throw new Error('Error run');
            })
            .then((json) => {
                this.stop_send=json.status
                this.run_send=false
                this.start_send=false
            })
            .catch((error) => {
                console.log(error)
            });
        },
        start(){
            fetch('{{=URL(args=["new_start"], extension="json")}}', {method: "GET", credentials: 'include'})
            .then((response) => {
                if(response.ok) {return response.json()}
                throw new Error('Error run');
            })
            .then((json) => {
                this.start_send=json.status;
                this.run_send=false;
            })
            .catch((error) => {
                console.log(error)
            });
        },
    }
}
</script>
<style></style>
