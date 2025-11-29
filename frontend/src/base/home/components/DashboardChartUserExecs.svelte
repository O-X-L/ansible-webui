<script lang="ts">
    import { onMount, onDestroy } from 'svelte';

    import { PieChart } from 'echarts/charts';
    import type { ComposeOption } from 'echarts/core';
    import { CanvasRenderer } from 'echarts/renderers';
    import type { PieSeriesOption } from 'echarts/charts';
    import { init, use, type ECharts } from 'echarts/core';
    import { TitleComponent, TooltipComponent, LegendComponent } from 'echarts/components';
    import type { 
        TitleComponentOption, 
        TooltipComponentOption, 
        LegendComponentOption 
    } from 'echarts/components';

    use([PieChart, TitleComponent, TooltipComponent, LegendComponent, CanvasRenderer]);

    type EChartsOption = ComposeOption<
        | PieSeriesOption
        | TitleComponentOption
        | TooltipComponentOption
        | LegendComponentOption
    >;

    import { share } from '../../Share.js';
    import type { statsJobs } from '../Types.js';
    import { tq } from '../../../util/translate.js';
    import { getDarkLightMode } from '../../DarkLightMode.js';

    let { data }: { data: statsJobs } = $props();

    let chartContainer: HTMLElement;
    let userExecsChart: ECharts | null = null;

    function t(code: string) : string {
        return tq($share, code);
    }

    /**
     * Calculates the execution count for each user (or 'scheduled').
     */
    function getExecByUserChartData() {
        let out: { [key: string]: number } = {};
        
        for (let s of data['stats']) {
            let n = t('jobs.info.scheduled');
            if (s[2] !== null) {
                n = data['mapping']['users'][s[2]];
            }
            if (!out[n]) {
                out[n] = 0;
            }
            out[n] += 1
        }
        
        const chartData = Object.keys(out).map(name => ({
            value: out[name],
            name: name
        }));

        if (chartData.length === 0) {
            return [{ value: 1, name: t('db.chart.no_data') }];
        }

        return chartData;
    }

    /**
     * Initializes the ECharts instance and sets up the chart options.
     */
    function addExecByUserChart() {
        const isDark = getDarkLightMode() == 'dark';
        if (!chartContainer) return;
        userExecsChart = init(chartContainer, isDark ? 'dark' : 'light');
        const option: EChartsOption = {
            title: {
                // text: t('db.chart.exec_by_user'),
                left: 'center',
                textStyle: {
                    color: isDark ? '#ADBABD' : '#333'
                }
            },
            backgroundColor: 'transparent',
            tooltip: {
                trigger: 'item',
                formatter: '{b}: {c} ({d}%)' 
            },
            legend: {
                orient: 'vertical',
                left: 'left',
                data: getExecByUserChartData().map(item => item.name),
                textStyle: {
                    color: isDark ? '#ADBABD' : '#333'
                }
            },
            series: [
                {
                    name: t('db.runs'),
                    type: 'pie',
                    radius: ['25%', '70%'],
                    avoidLabelOverlap: false,
                    itemStyle: {
                        borderRadius: 10,
                        borderColor: isDark ? '#1f2937' : '#fff',
                        borderWidth: 2
                    },
                    label: {
                        show: false,
                        position: 'center'
                    },
                    emphasis: {
                        label: {
                            show: false,
                        }
                    },
                    labelLine: {
                        show: false
                    },
                    data: getExecByUserChartData()
                }
            ]
        };

        userExecsChart.setOption(option);
        window.addEventListener('resize', resizeChart);
    }

    /**
     * Resizes the ECharts instance on window resize.
     */
    function resizeChart() {
        userExecsChart?.resize();
    }

    /**
     * Updates the chart data, and refreshes the chart.
     */
    function createUpdateChart() {
        const newData = getExecByUserChartData();
        
        if (!userExecsChart) {
            addExecByUserChart();
        } else {
            userExecsChart.setOption({
                legend: {
                    data: newData.map(item => item.name)
                },
                series: [{ data: newData }]
            });
        }
    }

    $effect(() => {
        data;
        createUpdateChart();
    });

    onMount(() => {
        addExecByUserChart();
    });

    onDestroy(() => {
        window.removeEventListener('resize', resizeChart);
        userExecsChart?.dispose();
    });
</script>

<div bind:this={chartContainer} id="chart-exec-by-user" class="h-96 w-full" role="img" aria-label="{t('db.chart.exec_by_user')} Chart"></div>