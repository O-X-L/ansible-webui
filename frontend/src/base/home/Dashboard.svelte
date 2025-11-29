<script lang="ts">
    import { onMount, onDestroy } from 'svelte';

    import {
        Spinner, Select, Button, Tooltip as FlowbiteTooltip, Input,
    } from 'flowbite-svelte';
    import { RefreshOutline } from 'flowbite-svelte-icons';

    import { share } from '../Share.js';
    import { apiGet } from '../../util/api.js';
    import { tq } from '../../util/translate.js';
    import { classFooterSpacing } from '../Style.js';
    import type { formChoiceType } from '../Types.js';
    import type { statsJobs, statsExecution } from './Types.js';
    import ChartExecOverTime from './components/DashboardChartExecOverTime.svelte';
    import ChartUserExecs from './components/DashboardChartUserExecs.svelte';
    import ChartJobResults from './components/DashboardChartJobResults.svelte';
    import ChartHostJobExecResults from './components/DashboardChartHostExecResults.svelte';

    let { open = $bindable(false) } = $props();

    let updateLoop: number = $state(0);

    const TIME_WINDOW_CHOICES: formChoiceType[] = [
        {name: t('db.time.minutes'), value: 'm'},
        {name: t('db.time.hours'), value: 'h'},
        {name: t('db.time.days'), value: 'd'},
        {name: t('db.time.weeks'), value: 'w'},
        {name: t('db.time.months'), value: 'M'},
    ];
    let statsTimeWindowValue: number = $state(1);
    let statsTimeWindowKind: string = $state('d');

    let data: statsJobs = $state({
        stats: [],
        mapping: {jobs: {}, users: {}, status: {}, host_stats: {}, stats: {}},
    });
    let lastExecTime = $state(0);
    let loaded = $state(false);

    function t(code: string) : string {
      return tq($share, code);
    }

    function getLastExecTime(stats: statsExecution[]) : number {
        let t = 0;
        for (let s of stats) {
            if (s[4] > t) {
                t = s[4];
            }
        }
        return t;
    }

    function loadJobStats(j: statsJobs) {
        if (j === null) {
            return;
        }
        data.mapping.jobs = {...data.mapping.jobs, ...j.mapping.jobs};
        data.mapping.users = {...data.mapping.users, ...j.mapping.users};
        data.mapping.status = {...data.mapping.status, ...j.mapping.status};
        data.mapping.stats = {...data.mapping.stats, ...j.mapping.stats};
        data.mapping.host_stats = {...data.mapping.host_stats, ...j.mapping.host_stats};
        data.stats = [...data.stats, ...j.stats];
        if (j.stats.length) {
            loaded = true;
            lastExecTime = getLastExecTime(j.stats);
        }
    }

    function buildJobStats() {
        if (!open || typeof(document.hidden) !== undefined && document['hidden']) {
            // tab in background
            return;
        }
        let limit = '';
        if (loaded) {
            limit = `limit_time=${lastExecTime}`;
        } else if (statsTimeWindowValue != 0) {
            limit = `limit_time=${statsTimeWindowValue}${statsTimeWindowKind}`;
        }
        apiGet(`stats/jobs?${limit}`, loadJobStats);
    }

    function updateStatsPeriod() {
        data.stats = [];
        lastExecTime = 0;
        loaded = false;
        buildJobStats();
    }

    onMount(() => {
        buildJobStats();

        // todo: refresh data over websockets
        clearInterval(updateLoop);
        updateLoop = setInterval(() => {
            if (lastExecTime != 0) {
                buildJobStats();
            }
        }, 2000);
    });

    onDestroy(()=>{
    	clearInterval(updateLoop);
    });
</script>

<header class="flex flex-col sm:flex-row justify-between items-center mb-6 p-4 dark:bg-gray-800 rounded-xl shadow-lg">
    <div class="flex justify-between w-full">
        <div>
            <h1 class="text-3xl font-bold dark:text-white mb-4 sm:mb-0">
                Dashboard
            </h1>
        </div>
        <div class="flex flex-column space-x-2">
            <div>
                <Input type="number" bind:value={statsTimeWindowValue} />
            </div>
            <div>
                <Select items={TIME_WINDOW_CHOICES} bind:value={statsTimeWindowKind} />
            </div>
            <div>
                <Button on:click={() => {updateStatsPeriod()}}><RefreshOutline/></Button>
                <FlowbiteTooltip>{t('btn.update')}</FlowbiteTooltip>
            </div>
        </div>
    </div>
</header>

<div class="grid grid-cols-1 lg:grid-cols-4 gap-6">
    <div class="lg:col-span-3 bg-gray-100 dark:bg-gray-800 p-6 rounded-xl shadow-lg">
        <div class="flex justify-between mb-2 w-full">
            <div>
                <h2 class="text-xl font-semibold mb-4">
                    {t('db.chart.exec_over_time')}
                </h2>
            </div>
            <div></div>
        </div>
        {#if !loaded}
            <div class="flex justify-center mt-10">
                <Spinner />
            </div>
        {:else}
            <ChartExecOverTime data={data} />
        {/if}
    </div>

    <div class="lg:col-span-1 bg-gray-100 dark:bg-gray-800 p-6 rounded-xl shadow-lg">
        <div class="flex justify-between mb-2 w-full">
            <div>
                <h2 class="text-xl font-semibold mb-4">
                    {t('db.chart.exec_by_user')}
                </h2>
            </div>
            <div></div>
        </div>

        {#if !loaded}
            <div class="flex justify-center mt-10">
                <Spinner />
            </div>
        {:else}
            <ChartUserExecs data={data} />
        {/if}
    </div>

    <div class="lg:col-span-2 bg-gray-100 dark:bg-gray-800 p-6 rounded-xl shadow-lg">
        <div class="flex justify-between mb-2 w-full">
            <div>
                <h2 class="text-xl font-semibold mb-4">
                    {t('db.chart.exec_results_by_job')}
                </h2>
            </div>
            <div></div>
        </div>

        {#if !loaded}
            <div class="flex justify-center mt-10">
                <Spinner />
            </div>
        {:else}
            <ChartJobResults data={data} />
        {/if}
    </div>
    <div class="lg:col-span-2 bg-gray-100 dark:bg-gray-800 p-6 rounded-xl shadow-lg">
        <div class="flex justify-between mb-2 w-full">
            <div>
                <h2 class="text-xl font-semibold mb-4">
                    {t('db.chart.exec_results_by_host')}
                </h2>
            </div>
            <div></div>
        </div>

        {#if !loaded}
            <div class="flex justify-center mt-10">
                <Spinner />
            </div>
        {:else}
            <ChartHostJobExecResults data={data} />
        {/if}
    </div>

</div>


<!--
    IDEAS:
        * stats of failed jobs (for all readable - user can narrow it down to single jobs)
        * stats of changed items
        * stats per host (allow user to select single host)
          * changed items
          * when did which playbook target the host; who executed it

    todo: allow users to choose stats time (hours, days, weeks, months)
        
-->

<div class={classFooterSpacing}></div>
<div id="loaded" class="h-0 w-0"></div>
