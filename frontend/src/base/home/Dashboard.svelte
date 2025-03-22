<script lang="ts">
    import { onMount, onDestroy } from 'svelte';

    import { Spinner } from 'flowbite-svelte';

    import {
        Chart,
        LineController, LineElement, PointElement, CategoryScale, LinearScale,
        DoughnutController, ArcElement,
        Legend, SubTitle, Title, Tooltip, Filler,
    } from 'chart.js';

    import { share } from '../Share.js';
    import { apiGet } from '../../util/api.js';
    import { tq } from '../../util/translate.js';
    import { getRandomTailwindColor } from '../../util/main.js';

    let { open = $bindable(false) } = $props();

    let apiDataHash = $state('');
    let updateLoop: number = $state(0);
    let loaded = $state(false);

    interface statsExecutionHosts {
        h: string  // hostname
        u: boolean  // unreachable
        ts: number  // tasks-skipped
        to: number  // tasks-ok
        tf: number  // tasks-failed
        tr: number  // tasks-rescued
        ti: number  // tasks-ignored
        tc: number  // tasks-changed
    }
    interface statsExecution {
        j: number  // job id
        s: number  // status id
        u: number|null  // user id
        d: string  // duration
        t: number  // time
        f: boolean  // failed
        h: statsExecutionHosts[]
    }
    interface statsJobsMapping {
        jobs: any
        users: any
        status: any
        host_stats: any
    }
    interface statsJobs {
        stats: statsExecution[]
        mapping: statsJobsMapping
    }

    let statsJobsData: statsJobs = $state({});

    function t(code: string) : string {
      return tq($share, code);
    }

    function loadJobStats(j: any, h: string) {
        if (j === null || h == apiDataHash) {
            return;
        }
        statsJobsData = j;
        apiDataHash = h;
        if (!loaded) {
            // todo: allow for data-refresh in charts
            addExecSuccessfulCountChart();
            addExecFailedCountChart();
            addExecByUserCountChart();
            loaded = true;
        }
    }

    function buildJobStats() {
        if (!open || typeof(document.hidden) !== undefined && document['hidden']) {
            // tab in background
            return;
        }
        apiGet(`stats/jobs?hash=${apiDataHash}`, loadJobStats);
    }

    /*
    function addTestChart() {
        const data = [
            { year: 2010, count: 10 },
            { year: 2011, count: 20 },
            { year: 2012, count: 15 },
            { year: 2013, count: 25 },
            { year: 2014, count: 22 },
            { year: 2015, count: 30 },
            { year: 2016, count: 28 },
        ];

        new Chart(
            document.getElementById('test-chart'),
            {
            type: 'line',
            data: {
                labels: data.map(row => row.year),
                datasets: [{
                    label: 'Acquisitions by year',
                    data: data.map(row => row.count),
                    tension: 0.1,
                }]
            }
            }
        );
    }
    */

    function addExecSuccessfulCountChart() {
        addExecCountChart('chart-jobs-success', false, 'Successful Jobs');
    }

    function addExecFailedCountChart() {
        addExecCountChart('chart-jobs-failed', true, 'Failed Jobs');
    }

    function addExecCountChart(id: string, failed: boolean, title: string) {
        let data = {};

        for (let s of statsJobsData['stats']) {
            if (s['f'] == failed) {
                let n = statsJobsData['mapping']['jobs'][s['j']];
                if (!data[n]) {
                    data[n] = 0;
                }
                data[n] += 1
            }
        }

        let colors = [];
        for (let i = 0; i < Object.keys(data).length; i++) {
            colors.push(getRandomTailwindColor());
        }

        if (Object.keys(data).length == 0) {
            data['-'] = 1;
            colors = ['oklch(0.928 0.006 264.531)'];
        }

        new Chart(
            document.getElementById(id),
            {
                type: 'doughnut',
                data: {
                    labels: Object.keys(data),
                    datasets: [{
                        label: 'Successful Job runs',
                        data: Object.values(data),
                        backgroundColor: colors,
                        hoverOffset: 4,
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        /*
                        legend: {
                            position: 'top',
                        },
                        */
                        title: {
                            display: true,
                            text: title
                        }
                    }
                }
            }
        );
    }

    function addExecByUserCountChart() {
        let data = {};

        for (let s of statsJobsData['stats']) {
            let n = 'Scheduled';
            if (s['u'] !== null) {
                n = statsJobsData['mapping']['users'][s['u']];
            }
            if (!data[n]) {
                data[n] = 0;
            }
            data[n] += 1
        }

        let colors = [];
        for (let i = 0; i < Object.keys(data).length; i++) {
            colors.push(getRandomTailwindColor());
        }

        if (Object.keys(data).length == 0) {
            data['-'] = 1;
            colors = ['oklch(0.928 0.006 264.531)'];
        }

        new Chart(
            document.getElementById('chart-jobs-by-user'),
            {
                type: 'doughnut',
                data: {
                    labels: Object.keys(data),
                    datasets: [{
                        label: 'Automatic vs Manual Job runs',
                        data: Object.values(data),
                        backgroundColor: colors,
                        hoverOffset: 4,
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        /*
                        legend: {
                            position: 'top',
                        },
                        */
                        title: {
                            display: true,
                            text: 'Executions by User'
                        }
                    }
                }
            }
        );
    }

    onMount(() => {
        buildJobStats();

        // see: https://www.chartjs.org/docs/latest/getting-started/integration.html#bundle-optimization
        Chart.register(
            LineController, LineElement, PointElement, CategoryScale, LinearScale,
            DoughnutController, ArcElement,
            Legend, SubTitle, Title, Tooltip, Filler,
        );

        // todo: refresh data over websockets
        /*
        clearInterval(updateLoop);
        updateLoop = setInterval(() => {
            buildJobStats();
        }, 10000);
        */
    });

    onDestroy(()=>{
    	clearInterval(updateLoop);
    });
</script>

{#if !loaded}
    <div class="text-center mt-20">
        <Spinner/>
    </div>
{/if}
<div class="flex">
    <div>
        <canvas id="chart-jobs-success"></canvas>
    </div>
    <div>
        <canvas id="chart-jobs-failed"></canvas>
    </div>
    <div>
        <canvas id="chart-jobs-by-user"></canvas>
    </div>
</div>
<canvas id="test-chart"></canvas>

<!--
    IDEAS:
        * stats of failed jobs (for all readable - user can narrow it down to single jobs)
        * stats of changed items
        * stats per host (allow user to select single host)
          * changed items
          * when did which playbook target the host; who executed it
-->
